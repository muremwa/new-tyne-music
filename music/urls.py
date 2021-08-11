from django.urls import path


from .views import profile_library, albums, artists, genres, curators, search


app_name = 'music'


urlpatterns = [
    # library/
    path('library/', profile_library, name='library'),

    # albums/
    path('albums/', albums, name='albums'),

    # artists/
    path('artists/', artists, name='artists'),

    # genres/
    path('genres/', genres, name='genres'),

    # curators/
    path('curators/<int:curator_id>/', curators, name='curator'),

    # search/
    path('search/', search, name='search'),

]
