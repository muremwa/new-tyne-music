from django.test import TestCase, tag

from music.models import Artist, Creator, Genre, Album
from django.core.exceptions import ValidationError
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
