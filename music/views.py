from re import findall
from itertools import chain

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404

from . import models as ms_models, serializers as ms_serializers
from .searches import MusicSearch


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_library(request):
    """
        Retrieve the library of the logged in user.\n
        Add parameter '?p=profile_pk' to retrieve the library of another profile from the user
    """
    profile_pk = request.GET.get('p')

    if profile_pk and profile_pk.isdigit() and request.user.tier == 'F':
        try:
            profile = request.user.profile_set.get(pk=int(profile_pk))
        except ObjectDoesNotExist:
            raise Http404

    else:
        profile = request.user.main_profile

    lib = ms_serializers.Library(profile)

    return Response(lib.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def albums(request):
    """
    Retrieve albums -> all, by artist, by year, by genre or a specific album
    use the following parameters
    all = /
    specific album = ?id=album_id
    by artist = ?a=artist_id
    by  year = ?y=YEAR
    between years = ?y=YEAR_EARLIEST-YEAR_LATEST
    by genre = ?g=genre_id
    """
    published_albums = ms_models.Album.objects.filter(published=True).order_by('-date_of_release')
    album_pk = request.GET.get('id')

    # looking for a single album
    if album_pk:
        if not album_pk.isdigit():
            raise Http404

        try:
            album = published_albums.get(pk=int(album_pk))
            response = ms_serializers.AlbumSerializer(album, read_only=True).data
        except ObjectDoesNotExist:
            raise Http404

    # list of albums
    else:
        # get filters
        filters = {filter_: request.GET.get(filter_) for filter_ in request.GET if filter_ in ['a', 'y', 'g']}

        # by artist
        if 'a' in filters.keys():
            if filters['a'].isdigit():
                published_albums = published_albums.filter(artists__pk=filters['a'])

        # by genre
        if 'g' in filters.keys():
            if filters['g'].isdigit():
                published_albums = published_albums.filter(genre__pk=filters['g'])

        # by years
        if 'y' in filters.keys():
            years = findall(r'\d{4}', filters['y'])

            if len(years) > 0:
                years = sorted([int(year) for year in years])

                # between two years
                if len(years) == 2:
                    start_year = years[0]
                    last_year = years[-1]
                    published_albums = published_albums.filter(
                        date_of_release__year__gte=start_year
                    ).filter(
                        date_of_release__year__lte=last_year
                    )

                # specific year
                elif len(years) == 1:
                    published_albums = published_albums.filter(date_of_release__year=years[0])

        response = ms_serializers.AlbumSerializer(published_albums, many=True, read_only=True, no_discs=True).data

    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def artists(request):
    """
    Retrieve artists or a specific artist
    1. List artists - returns an array of artists with basic info => name, covers, etc.
    2. Specific artist - returns basic info plus, Top songs, Albums, EPs and Singles, Tyne Music Playlists of the artist
        Use '?id=artist_id' for a specific artist
    """
    artist_pk = request.GET.get('id')

    if artist_pk:
        if not artist_pk.isdigit():
            raise Http404

        artist = get_object_or_404(ms_models.Artist, pk=artist_pk)
        response = ms_serializers.ArtistSerializer(artist, read_only=True).data
        album_set = artist.album_set.filter(published=True)

        # top songs
        songs = [song for album in album_set for song in album.all_songs()]
        additional_artist_songs = artist.additions.filter(disc__album__published=True)
        features = artist.features.filter(disc__album__published=True)

        top_songs = ms_serializers.SongSerializer(
            sorted(chain(songs, additional_artist_songs, features), key=lambda song: song.streams, reverse=True)[:10],
            many=True,
            read_only=True,
            album_info=True
        )

        # albums, Singles, EPs
        artist_albums = ms_serializers.AlbumSerializer(
            album_set.filter(is_ep=False, is_single=False),
            many=True,
            read_only=True,
            no_discs=True
        )
        singles = ms_serializers.AlbumSerializer(
            album_set.filter(is_single=True),
            many=True,
            read_only=True,
            no_discs=True
        )
        eps = ms_serializers.AlbumSerializer(
            album_set.filter(is_ep=True),
            many=True,
            read_only=True,
            no_discs=True
        )

        # playlists
        playlists = ms_serializers.PlaylistSerializer(
            artist.playlists.all(),
            many=True,
            read_only=True
        )

        response.update({
            'top_songs': top_songs.data,
            'albums': artist_albums.data,
            'singles': singles.data,
            'eps': eps.data,
            'playlists': playlists.data
        })

    else:
        all_artists = ms_serializers.ArtistSerializer(
            ms_models.Artist.objects.order_by('name'),
            many=True,
            read_only=True
        )
        response = all_artists.data

    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def genres(request):
    """
    Retrieve Genres or a specific genre
    1. Returns a list of genres
    2. A specific Genre that includes related Creators/Curators
        Use parameter '?id=genre_id'
    """
    genre_pk = request.GET.get('id')

    if genre_pk:
        if not genre_pk.isdigit():
            raise Http404

        genre = get_object_or_404(ms_models.Genre, pk=genre_pk)
        response = ms_serializers.GenreSerializer(genre, read_only=True).data
        genre_curators = set(list(genre.creator_set.all()) + [genre.main_curator])
        sections = genre.main_curator.creatorsection_set.all()
        response.update({
            'curators': ms_serializers.CreatorSerializer(genre_curators, many=True, read_only=True).data,
            'sections': ms_serializers.CreatorSectionSerializer(sections, many=True, read_only=True).data,
            'playlists': ms_serializers.PlaylistSerializer(
                genre.main_curator.playlist_set.filter(artist__isnull=True),
                many=True,
                read_only=True
            ).data
        })

    else:
        all_genres = ms_models.Genre.objects.all()
        response = ms_serializers.GenreSerializer(all_genres, many=True, read_only=True).data

    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def curators(request, curator_id):
    curator = get_object_or_404(ms_models.Creator, pk=curator_id)
    sections = curator.creatorsection_set.all()
    playlists = curator.playlist_set.filter(artist__isnull=True)
    response = ms_serializers.CreatorSerializer(curator, read_only=True).data

    info_only = request.GET.get('io')

    if not info_only:
        response.update({
            'sections': ms_serializers.CreatorSectionSerializer(sections, many=True, read_only=True).data,
            'playlists': ms_serializers.PlaylistSerializer(playlists, many=True, read_only=True).data
        })

    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    """
    Search the tyne music catalogue
    use the parameter ?q=search_term
    Results are in the following format
    {
        'top_results': [mix of albums, songs, playlists, genres, etc],
        'albums': [albums],
        'artists': [artists],
        'playlists': [playlists],
        'genres': [genres],
        'curators': [curators],
        'time': seconds of how long the search took
    }
    """
    term = request.GET.get('q')
    response = {}

    if term:
        ms_search = MusicSearch(term)
        response = ms_search.get_results(serialize=True)
        response.update({
            'time': ms_search.time_taken
        })

    return Response(response)
