from django.test import TestCase, tag, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from music.models import Artist, Creator, Genre, Album, Song, Playlist, CreatorSection
from core.models import User


@tag('music-m-artist')
class ArtistTestCase(TestCase):
    def setUp(self):
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.artist_3: Artist = Artist.objects.create(
            name='Offset'
        )
        self.artist_4: Artist = Artist.objects.create(
            name='Migos',
            is_group=True
        )
        self.artist_5: Artist = Artist.objects.create(
            name='The Fugees',
            is_group=True
        )

    def test_artists_exists(self):
        self.assertEqual(Artist.objects.count(), 5)

    def test_add_artist_to_group(self):
        self.artist_4.add_artist_to_group(self.artist_1)
        self.artist_4.add_artist_to_group(self.artist_2)
        self.artist_4.add_artist_to_group(self.artist_3)
        self.artist_4.add_artist_to_group(self.artist_5)
        self.assertEqual(self.artist_4.group_members.all().count(), 3)
        self.assertListEqual(list(self.artist_4.group_members.all()), [self.artist_1, self.artist_2, self.artist_3])
        self.artist_1.add_artist_to_group(self.artist_2)
        self.assertEqual(self.artist_1.group_members.all().count(), 1)
        self.assertListEqual(list(self.artist_1.group_members.all()), [self.artist_4])

    def test_string_names(self):
        self.assertEqual('<Artist \'Quavo\'>', str(self.artist_1))
        self.assertEqual('<Group \'The Fugees\'>', str(self.artist_5))


@tag('music-m-creator')
class CreatorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator_user',
            email='creator@tyne.com',
            password='pass@123'
        )
        self.creator = Creator.objects.create(
            name='Tyne Music Pop'
        )

    def test_creator_exists(self):
        self.assertEqual(Creator.objects.count(), 1)

    def test_creator_accepts_staff_only(self):
        self.creator.add_creator_user(self.user)
        self.assertEqual(self.creator.users.count(), 0)
        self.user.is_staff = True
        self.user.save()
        self.creator.add_creator_user(self.user)
        self.assertEqual(self.creator.users.count(), 1)
        self.assertListEqual(list(self.creator.users.all()), [self.user])

    def test_string_names(self):
        self.assertEqual('<TyneMusicContentCreator: \'Tyne Music Pop\'>', str(self.creator))


@tag('music-m-genre')
class GenreTestCase(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(
            title='Pop'
        )

    def test_genre_exists(self):
        self.assertEqual(Genre.objects.count(), 1)

    def test_string_name(self):
        self.assertEqual('<Genre: \'Pop\'>', str(self.genre))


@tag('music-m-album')
class AlbumTestCase(TestCase):
    def setUp(self):
        self.genre: Genre = Genre.objects.create(
            title='Hip-Hop'
        )
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.album_1: Album = Album.objects.create(
            title='WAX',
            genre=self.genre,
            date_of_release='2021-05-05'
        )
        self.album_1.artists.add(self.artist_1)
        self.album_2: Album = Album.objects.create(
            title='WAX (Deluxe)',
            genre=self.genre,
            date_of_release='2021-05-12'
        )
        self.album_2.artists.add(self.artist_1)
        self.album_2.add_sister_album(self.album_1)
        self.album_3: Album = Album.objects.create(
            title='WAX (Tyne Music Edition)',
            genre=self.genre,
            date_of_release='2021-05-12'
        )
        self.album_3.artists.add(self.artist_1)
        self.album_3.add_sister_album(self.album_1)
        self.album_3.add_sister_album(self.album_2)

        self.album_4: Album = Album(
            title='ENOCH',
            genre=self.genre,
            date_of_release='2021-05-21',
            is_ep=True
        )

        self.album_5: Album = Album(
            title='KEN',
            genre=self.genre,
            date_of_release='2021-05-21',
            is_single=True
        )

        self.albums = [self.album_1, self.album_2, self.album_3]

    def test_other_versions(self):
        for album in self.albums:
            self.assertEqual(album.other_versions.count(), 2)
            self.assertListEqual(list(album.other_versions.all()), [al for al in self.albums if al is not album])

    def test_string_name(self):
        self.album_4.save()
        self.assertEqual(str(self.album_4), f'<EP: \'{self.album_4.title}\'>')
        self.album_5.save()
        self.assertEqual(str(self.album_5), f'<Single: \'{self.album_5.title}\'>')
        self.assertEqual(str(self.album_1), f'<Album: \'{self.album_1.title}\'>')

    def test_saving_ep_and_single(self):
        self.album_4.is_single = True
        with self.assertRaisesRegex(ValidationError, 'EP or Single not both'):
            self.album_4.save()

        self.album_5.is_ep = True
        with self.assertRaisesRegex(ValidationError, 'EP or Single not both'):
            self.album_5.save()

        self.album_5.is_ep = False
        self.album_5.save()
        self.album_5.refresh_from_db()
        self.assertEqual(self.album_5, Album.objects.get(pk=self.album_5.pk))

    def test_album_artists(self):
        self.assertListEqual(list(self.album_1.artists.all()), [self.artist_1])
        self.album_1.artists.add(self.artist_2)
        self.assertEqual(self.album_1.artists.count(), 2)
        self.assertListEqual(list(self.album_1.artists.all()), [self.artist_1, self.artist_2])


@tag('music-m-song')
class SongTestCase(TransactionTestCase):
    def setUp(self):
        self.genre: Genre = Genre.objects.create(
            title='Hip-Hop'
        )
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.album_1: Album = Album.objects.create(
            title='WAX',
            genre=self.genre,
            date_of_release='2021-05-05'
        )
        self.album_1.artists.add(self.artist_1)
        self.song_1: Song = Song.objects.create(
            title='Timmy',
            track_no=1,
            album=self.album_1,
            genre=self.genre,
            length=285
        )
        self.song_1.additional_artists.add(self.artist_2)

    def test_artists_auto_added(self):
        self.assertEqual(self.song_1.additional_artists.count(), 1)
        self.assertEqual(
            list(self.song_1.additional_artists.all()) + (list(self.song_1.album.artists.all())),
            [self.artist_2, self.artist_1]
        )

    def test_string_name(self):
        self.assertEqual(str(self.song_1), f'<Song: \'{self.song_1.title}\' from \'{self.song_1.album.title}\'>')

    def test_song_number_not_repeated(self):
        song = Song(
            title='Pig',
            track_no=1,
            album=self.album_1,
            genre=self.genre,
            length=285
        )
        with self.assertRaisesRegex(IntegrityError, 'UNIQUE constraint failed'):
            song.save()

        song.track_no = 2
        song.save()
        self.assertEqual(self.album_1.song_set.count(), 2)
        self.assertListEqual(list(self.album_1.song_set.all()), [self.song_1, song])

    def test_song_additional_artist(self):
        song = Song.objects.create(
            title='Pig',
            track_no=3,
            album=self.album_1,
            genre=self.genre,
            length=265
        )
        self.assertEqual(song.additional_artists.count(), 0)
        song.add_additional_artist(self.artist_1)
        self.assertEqual(song.additional_artists.count(), 0)
        song.add_additional_artist(self.artist_2)
        self.assertEqual(song.additional_artists.count(), 1)


@tag('music-m-playlist')
class PlaylistTestCase(TestCase):
    def setUp(self):
        self.genre: Genre = Genre.objects.create(
            title='Hip-Hop'
        )
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.album_1: Album = Album.objects.create(
            title='WAX',
            genre=self.genre,
            date_of_release='2021-05-05'
        )
        self.album_1.artists.add(self.artist_1)
        self.song_1: Song = Song.objects.create(
            title='Timmy',
            track_no=1,
            album=self.album_1,
            genre=self.genre,
            length=285
        )
        self.song_1.additional_artists.add(self.artist_2)
        self.song_2 = Song.objects.create(
            title='Pig',
            track_no=3,
            album=self.album_1,
            genre=self.genre,
            length=265
        )
        self.creator = Creator.objects.create(
            name='Tyne Music Pop'
        )
        self.playlist_1: Playlist = Playlist.objects.create(
            title='All Time Pop',
            creator=self.creator
        )
        self.playlist_2: Playlist = Playlist.objects.create(
            title='Home work',
            profile=User.objects.create_user(
                username='pl',
                email='pl@tyne.com',
                password='pass@123'
            ).main_profile
        )

    def test_playlist_only_user_or_creator(self):
        self.playlist_2.creator = self.creator
        with self.assertRaisesRegex(ValidationError, 'Playlist is by either Profile or Creator'):
            self.playlist_2.save()

    def test_playlist_songs(self):
        self.playlist_1.add_song_to_playlist(self.song_1)
        self.playlist_1.add_song_to_playlist(self.song_2)
        self.playlist_1.add_song_to_playlist(self.song_2)
        self.assertEqual(self.playlist_1.songs.count(), 2)
        self.assertEqual(self.playlist_1.songs_order, f'{self.song_1.pk},{self.song_2.pk}')
        self.assertListEqual(self.playlist_1.songs_order_pk, [self.song_1.pk, self.song_2.pk])
        self.playlist_1.set_song_order(self.song_1.pk, 1)
        self.assertListEqual(self.playlist_1.songs_order_pk, [self.song_2.pk, self.song_1.pk])
        self.playlist_1.set_song_order(self.song_2.pk, 8)
        self.assertListEqual(self.playlist_1.songs_order_pk, [self.song_1.pk, self.song_2.pk])
        self.assertListEqual(self.playlist_1.songs_by_order(), [self.song_1, self.song_2])

    def test_string_name(self):
        self.assertEqual(
            str(self.playlist_1),
            f'<CreatorPlaylist \'{self.playlist_1.title}\' by \'{self.playlist_1.creator.name}\'>'
        )
        self.assertEqual(
            str(self.playlist_2),
            f'<UserPlaylist \'{self.playlist_2.title}\' by \'{self.playlist_2.profile.name}\'>'
        )
        self.assertEqual(self.playlist_1.owner(), self.creator.name)
        self.assertEqual(self.playlist_2.owner(), 'pl')


@tag('music-m-section')
class CreatorSectionTestCase(TestCase):
    def setUp(self):
        self.creator = Creator.objects.create(
            name='Tyne Music Pop'
        )
        self.section = CreatorSection.objects.create(
            name='Favourite Artits',
            creator=self.creator
        )

    def test_string_name(self):
        self.assertEqual(str(self.section), f'<CreatorSection from \'{self.creator.name}\'>')
