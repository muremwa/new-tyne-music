from django.test import TestCase, tag

from music.models import Artist, Creator
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
