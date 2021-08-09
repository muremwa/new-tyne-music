from re import findall
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from . import models as ms_models, serializers as ms_serializers


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
    if album_pk and album_pk.isdigit():
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
                try:
                    artist = ms_models.Artist.objects.get(pk=int(filters['a']))
                    published_albums = published_albums.filter(artists__name=artist.name)
                except ObjectDoesNotExist:
                    pass

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
