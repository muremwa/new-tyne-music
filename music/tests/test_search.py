from django.test import TestCase, tag

from music import models as ms_models, searches
from core.models import User


@tag('music-search')
class SearchTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
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

    def test_simple_search(self):
        ms = searches.MusicSearch('Wax')
        res = ms.get_results()
        self.assertListEqual(list(res.keys()), [
            'albums', 'songs', 'artists', 'playlists', 'genres', 'curators', 'top_results'
        ])

        serial_data = ms.get_results(serialize=True)
        self.assertEqual(list(serial_data.keys()), [
            'albums', 'songs', 'artists', 'playlists', 'genres', 'curators', 'top_results'
        ])

    def test_staff_view(self):
        ms = searches.MusicSearch('Wax')
        res = ms.get_results()
        self.assertTrue(self.album_3 not in res.get('albums'))

        ms = searches.MusicSearch('Wax', True)
        res = ms.get_results()
        self.assertTrue(self.album_3 in res.get('albums'))
