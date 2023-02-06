from typing import List, Dict
from itertools import chain
from time import time

from Levenshtein import distance
from django.db.models import Q

from . import models as ms_models, serializers as ms_serializers


class MusicSearch:
    """
    Search music
        ms_search = MusicSearch(term='drake', staff_view=False)
    takes two args
        1. term = search term
        2. staff_view = True if used in a staff view else False for normal users view

    Usage:
        ms_search.get_results()

        returns an Dict of results
        {
            'top_results': [mix of all below],\n
            'albums': Album[],\n
            'songs': Song[],\n
            'artists': Artist[],\n
            'playlists': Playlist[],\n
            'genres': Genre[],\n
            'curators': Creator[],\n
        }

    `ms_search.get_results` takes 2 args
        1. serialize = True to return serialized results False for normal lists with model objects
        2. refresh = Refresh the results

    To avoid searching/hitting the database a lot of unnecessary times, the results and serialized data is
    available from `ms_search.results` and `ms_search.serial_data` after get_results is called for results and
    serialize=True makes serial_data available. Calling `get_results` uses `ms_search.results` and same for
    serial_data, unless refresh=True hits database again
    """

    def __init__(self, term='', staff_view=False):
        self.term = term
        self.staff_view = staff_view
        self.results = None
        self.serial_data = None
        self.time_taken = None

    def __distance(self, string: str) -> int:
        return distance(self.term.lower(), string.lower())

    def __search_albums(self) -> List:
        albums_q_set = (
            Q(title__icontains=self.term) | Q(notes__icontains=self.term) | Q(artists__name__icontains=self.term)
        )
        s_albums = ms_models.Album.objects.filter(albums_q_set)
        if not self.staff_view:
            s_albums = s_albums.filter(published=True)

        return sorted(set(s_albums), key=lambda album: self.__distance(str(album.title)))

    def __search_artists(self) -> List:
        # search by name and group member names
        artists_q_set = (
            Q(name__icontains=self.term) | Q(group_members__name__icontains=self.term)
        )
        s_artists_by_name = ms_models.Artist.objects.filter(artists_q_set)

        # search from nicknames
        s_artists_by_nicknames = ms_models.Artist.objects.filter(nicknames__icontains=self.term)

        # join all artists and remove duplicates
        s_artists = set(chain(s_artists_by_name, s_artists_by_nicknames))

        # return a sorted list
        return sorted(s_artists, key=lambda artist: self.__distance(str(artist.name)))

    def __search_genres_and_curators(self) -> Dict:
        # genres
        s_genres = ms_models.Genre.objects.filter(title__icontains=self.term)

        # creators
        creator_q_set = (
            Q(name__icontains=self.term) | Q(genres__title__icontains=self.term)
        )
        s_creators = ms_models.Creator.objects.filter(creator_q_set)

        return {
            'genres': sorted(s_genres, key=lambda genre: self.__distance(str(genre.title))),
            'curators': sorted(set(s_creators), key=lambda curator_: self.__distance(str(curator_.name)))
        }

    def __search_playlists(self) -> List:
        playlist_q_set = (
            Q(title__icontains=self.term) |
            Q(description__icontains=self.term) |
            Q(creator__name__icontains=self.term) |
            Q(creator__genres__title__icontains=self.term)
        )
        s_playlists = ms_models.Playlist.objects.filter(playlist_q_set, profile__isnull=True)

        return sorted(
            set(s_playlists),
            key=lambda playlist: self.__distance(str(playlist.title))
        )

    def __search_songs(self) -> List:
        song_s = (
            Q(title__icontains=self.term) |
            Q(disc__album__artists__name__icontains=self.term) |
            Q(disc__album__title__icontains=self.term) |
            Q(additional_artists__name__icontains=self.term)
        )
        s_songs = ms_models.Song.objects.filter(song_s)

        if not self.staff_view:
            s_songs = s_songs.filter(disc__album__published=True)

        return sorted(
            set(s_songs),
            key=lambda song: self.__distance(str(song.title))
        )

    def __process(self) -> Dict:
        genres_curators = self.__search_genres_and_curators()
        results = {
            'albums': self.__search_albums(),
            'songs': self.__search_songs(),
            'artists': self.__search_artists(),
            'playlists': self.__search_playlists(),
            'genres': genres_curators.get('genres', []),
            'curators': genres_curators.get('curators', []),
        }
        results.update({
            'top_results': self.__top_results(results)
        })
        return results

    def __top_results(self, results: Dict) -> List:
        """Bring together a list of top results from each section"""
        top_results = []

        # take the 1st 5 results from each section
        for key in results:
            top_results.extend(results[key][:5])

        # sort the results by how close they are to the search term
        def det_klass_comparison(item):
            comp = 'TYNE MUSIC'
            klass_for_title = [ms_models.Album, ms_models.Song, ms_models.Playlist, ms_models.Genre]
            klass_for_name = [ms_models.Artist, ms_models.Creator]

            title = [isinstance(item, klass) for klass in klass_for_title]
            name = [isinstance(item, klass) for klass in klass_for_name]

            if any(title):
                comp = 'title'
            elif any(name):
                comp = 'name'

            if hasattr(item, comp):
                comp = getattr(item, comp)
                comp = str(comp)

            return comp

        top_results.sort(
            key=lambda result: self.__distance(det_klass_comparison(result))
        )

        return top_results

    @staticmethod
    def __serialize_item(item) -> Dict:
        data = None

        if isinstance(item, ms_models.Album):
            data = ms_serializers.AlbumSerializer(item, read_only=True, no_discs=True).data
            data['item_type'] = 'ALBUM'

        elif isinstance(item, ms_models.Song):
            data = ms_serializers.SongSerializer(item, read_only=True, album_info=True).data
            data['item_type'] = 'SONG'

        elif isinstance(item, ms_models.Artist):
            data = ms_serializers.ArtistSerializer(item, read_only=True).data
            data['item_type'] = 'ARTIST'

        elif isinstance(item, ms_models.Playlist):
            data = ms_serializers.PlaylistSerializer(item, read_only=True).data
            data['item_type'] = 'PLAYLIST'

        elif isinstance(item, ms_models.Genre):
            data = ms_serializers.GenreSerializer(item, read_only=True).data
            data['item_type'] = 'GENRE'

        elif isinstance(item, ms_models.Creator):
            data = ms_serializers.CreatorSerializer(item, read_only=True).data
            data['item_type'] = 'CURATOR'

        return data

    def __serialize_results(self, res: Dict) -> Dict:
        res.update({
            'top_results': [self.__serialize_item(item_) for item_ in res.get('top_results', [])],
            'albums': ms_serializers.AlbumSerializer(res.get('albums'), many=True, no_discs=True, read_only=True).data,
            'songs': ms_serializers.SongSerializer(res.get('songs'), many=True, album_info=True, read_only=True).data,
            'artists': ms_serializers.ArtistSerializer(res.get('artists'), many=True, read_only=True).data,
            'playlists': ms_serializers.PlaylistSerializer(res.get('playlists'), many=True, read_only=True).data,
            'genres': ms_serializers.GenreSerializer(res.get('genres'), many=True, read_only=True).data,
            'curators': ms_serializers.CreatorSerializer(res.get('curators'), many=True, read_only=True).data,
        })
        return res

    def get_results(self, serialize=False, refresh=False) -> Dict:
        """serialize=True to get serial_data"""
        start_time = time()
        if self.results is None or refresh:
            self.results = self.__process()

        if (serialize and self.serial_data is None) or refresh:
            self.serial_data = self.__serialize_results(self.results)
        end_time = time()
        self.time_taken = end_time - start_time

        return self.serial_data if serialize else self.results
