from rest_framework.test import APIClient, APITestCase
from django.test import tag
from django.urls import reverse

from music import views as ms_views, models as ms_models, serializers as ms_s
from core.models import User


@tag('music-v')
class MusicViewsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='creator_user',
            email='creator@tyne.com',
            password='pass@123',
            tier='F'
        )
        self.creator = ms_models.Creator.objects.create(
            name='Tyne Music Pop'
        )
        self.genre: ms_models.Genre = ms_models.Genre.objects.create(
            title='Hip-Hop'
        )
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
        self.album_1: ms_models.Album = ms_models.Album.objects.create(
            title='WAX (Deluxe)',
            genre=self.genre,
            date_of_release='2021-05-12'
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
        self.playlist_1: ms_models.Playlist = ms_models.Playlist.objects.create(
            title='All Time Pop',
            creator=self.creator
        )
        self.user_2 = User.objects.create_user(
            username='pl',
            email='pl@tyne.com',
            password='pass@123'
        )
        self.playlist_2: ms_models.Playlist = ms_models.Playlist.objects.create(
            title='Home work',
            profile=self.user_2.main_profile
        )
        self.library: ms_models.LibraryAlbum = ms_models.LibraryAlbum.objects.create(
            profile=self.user.main_profile,
            album=self.album_1
        )
        self.library.songs.add(self.song_1)

    def test_library_view(self):
        url = reverse('music:library')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.json(), ms_s.Library(self.user.main_profile).data)
        response = self.client.get(f'{url}?p={self.user_2.main_profile.pk}')
        self.assertEqual(response.status_code, 404)



