from django.urls import path


from .views import profile_library


app_name = 'music'


urlpatterns = [
    # library/
    path('library/', profile_library, name='library'),

]
