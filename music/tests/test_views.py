from rest_framework.test import APIClient, APITestCase
from django.test import tag
from django.urls import reverse

from music import models as ms_models, serializers as ms_s
from core.models import User


@tag('music-v')
class MusicViewsTestCase(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        # users
        self.user = User.objects.create_user(
            username='creator_user',
            email='creator@tyne.com',
            password='pass@123',
            tier='F'
        )
        self.user_2 = User.objects.create_user(
            username='pl',
            email='pl@tyne.com',
            password='pass@123'
        )
        self.client.force_login(self.user)

        # creators and sections
        self.creator = ms_models.Creator.objects.create(
            name='Tyne Music Pop'
        )
        self.creator_2 = ms_models.Creator.objects.create(
            name='Tyne Music Hip-Hop'
        )
        self.section: ms_models.CreatorSection = ms_models.CreatorSection.objects.create(
            name='Top Albums',
            creator=self.creator
        )

        # genre
        self.genre: ms_models.Genre = ms_models.Genre.objects.create(
            title='Hip-Hop',
            main_curator=self.creator_2
        )
        self.creator.genres.add(self.genre)

        # artists
        self.artist_1: ms_models.Artist = ms_models.Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: ms_models.Artist = ms_models.Artist.objects.create(
            name='Takeoff'
        )
        self.artist_3: ms_models.Artist = ms_models.Artist.objects.create(
            name='Offset'
        )
        self.artist_4: ms_models.Artist = ms_models.Artist.objects.create(
            name='Migos',
            is_group=True
        )

        # album 1 and songs
        self.album_1: ms_models.Album = ms_models.Album.objects.create(
            title='WAX (Deluxe)',
            genre=self.genre,
            date_of_release='2021-05-12',
            published=True
        )
        self.album_1.artists.add(self.artist_1)
        self.song_1: ms_models.Song = ms_models.Song.objects.create(
            title='Timmy',
            track_no=1,
            disc=self.album_1.disc_one,
            genre=self.genre,
            length=285
        )
        self.song_1.additional_artists.add(self.artist_2)

        # album 2
        self.album_2: ms_models.Album = ms_models.Album.objects.create(
            title='WAX',
            genre=self.genre,
            date_of_release='2021-05-12',
            published=True
        )
        self.album_2.add_sister_album(self.album_1)

        # album 3
        self.album_3: ms_models.Album = ms_models.Album.objects.create(
            title='WAX Platinum Edition',
            genre=self.genre,
            date_of_release='2021-05-12'
        )

        # playlists
        self.playlist_1: ms_models.Playlist = ms_models.Playlist.objects.create(
            title='All Time Pop',
            creator=self.creator
        )
        self.playlist_2: ms_models.Playlist = ms_models.Playlist.objects.create(
            title='Home work',
            profile=self.user_2.main_profile
        )
        self.playlist_3: ms_models.Playlist = ms_models.Playlist.objects.create(
            title=f'{self.artist_1} Must Listens',
            creator=self.creator_2
        )
        self.artist_1.playlists.add(self.playlist_3)
        self.section.albums.add(self.album_1)

        # library
        self.library: ms_models.LibraryAlbum = ms_models.LibraryAlbum.objects.create(
            profile=self.user.main_profile,
            album=self.album_1
        )
        self.library.songs.add(self.song_1)

    def test_library_view(self):
        url = reverse('music:library')
        response = self.client.get(url)
        self.assertEqual(response.json(), ms_s.Library(self.user.main_profile).data)
        response = self.client.get(f'{url}?p={self.user_2.main_profile.pk}')
        self.assertEqual(response.status_code, 404)

    def test_albums(self):
        url = reverse('music:albums')

        # album list
        response = self.client.get(url)
        self.assertListEqual(
            response.json(),
            ms_s.AlbumSerializer(
                ms_models.Album.objects.filter(published=True).order_by('date_of_release'),
                many=True,
                read_only=True,
                no_discs=True
            ).data
        )

        # specific album
        response = self.client.get(f'{url}?id={self.album_1.pk}')
        self.assertDictEqual(response.json(), ms_s.AlbumSerializer(self.album_1, read_only=True).data)

        # unknown album or not published
        response = self.client.get(f'{url}?id={self.album_3.pk}')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'{url}?id=800')
        self.assertEqual(response.status_code, 404)

    def test_artists(self):
        url = reverse('music:artists')

        # list
        response = self.client.get(url)
        self.assertListEqual(
            response.json(),
            ms_s.ArtistSerializer(ms_models.Artist.objects.order_by('name'), many=True, read_only=True).data
        )

        # specific artist
        response = self.client.get(f'{url}?id={self.artist_1.pk}')
        artist_info = ms_s.ArtistSerializer(self.artist_1, read_only=True).data
        album_songs = [
            album.all_songs() for album in self.artist_1.album_set.filter(published=True) if album.all_songs()
        ]
        songs = [song for album in album_songs for song in album]
        songs.sort(key=lambda song: song.streams, reverse=True)
        album_set = self.artist_1.album_set.filter(published=True).order_by('-date_of_release')
        albums = album_set.filter(is_ep=False, is_single=False)
        eps = album_set.filter(is_ep=True)
        singles = album_set.filter(is_single=True)

        artist_info.update({
            'top_songs': ms_s.SongSerializer(songs, many=True, read_only=True, album_info=True).data,
            'albums': ms_s.AlbumSerializer(albums, many=True, read_only=True, no_discs=True).data,
            'singles': ms_s.AlbumSerializer(singles, many=True, read_only=True, no_discs=True).data,
            'eps': ms_s.AlbumSerializer(eps, many=True, read_only=True, no_discs=True).data,
            'playlists': ms_s.PlaylistSerializer(self.artist_1.playlists.all(), many=True, read_only=True).data
        })

        self.assertDictEqual(
            response.json(),
            artist_info
        )

        # no such artist
        response = self.client.get(f'{url}?id=800')
        self.assertEqual(response.status_code, 404)

    def test_genres(self):
        url = reverse('music:genres')

        # list
        response = self.client.get(url)
        self.assertEqual(
            response.json(),
            ms_s.GenreSerializer(ms_models.Genre.objects.all(), many=True, read_only=True).data
        )

        # specific genre
        response = self.client.get(f'{url}?id={self.genre.pk}')
        genre_info = ms_s.GenreSerializer(self.genre).data
        curators = list(self.genre.creator_set.all()) + [self.genre.main_curator]
        genre_info.update({
            'curators': ms_s.CreatorSerializer(set(curators), many=True).data,
            'sections': ms_s.CreatorSectionSerializer(self.genre.main_curator.creatorsection_set.all(), many=True).data,
            'playlists': ms_s.PlaylistSerializer(
                self.genre.main_curator.playlist_set.filter(artist__isnull=True),
                many=True,
                read_only=True
            ).data
        })
        self.assertEqual(response.json(), genre_info)

        # no such genre
        response = self.client.get(f'{url}?id=800')
        self.assertEqual(response.status_code, 404)

    def test_curator(self):
        url = reverse('music:curator', kwargs={'curator_id': self.creator.pk})
        response = self.client.get(url)
        c_info = ms_s.CreatorSerializer(self.creator, read_only=True).data
        c_info.update({
            'sections': ms_s.CreatorSectionSerializer(
                self.creator.creatorsection_set.all(),
                many=True,
                read_only=True
            ).data,
            'playlists': ms_s.PlaylistSerializer(
                self.creator.playlist_set.filter(artist__isnull=True),
                many=True,
                read_only=True
            ).data
        })
        self.assertEqual(response.json(), c_info)
