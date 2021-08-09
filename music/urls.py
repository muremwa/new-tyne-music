from django.urls import path


from .views import profile_library, albums


app_name = 'music'


urlpatterns = [
    # library/
    path('library/', profile_library, name='library'),

    # albums/
    path('albums/', albums, name='albums'),

]
