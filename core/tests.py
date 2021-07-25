from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import User, Profile


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test1',
            first_name='Test',
            last_name='One',
            email='test@test.com',
            password='newuser@123'
        )

    def test_email(self):
        with self.assertRaisesRegex(ValidationError, 'Email field required'):
            User.objects.create_user(
                username='noemail',
                first_name='Test',
                last_name='One',
                password='newuser@123'
            )

    def test_tier(self):
        users = User.objects.all()
        self.assertEqual(users[0], self.user)
        self.assertEqual(self.user.tier, 'S')

    def test_main_profile(self):
        profile = self.user.main_profile
        self.assertEqual(self.user.profile_set.count(), 1)
        self.assertEqual(profile.main, True)
        self.assertEqual(profile.name, 'test1')
        self.assertEqual(profile.minor, False)

    def test_single_tier_profiles(self):
        self.assertEqual(self.user.tier, 'S')
        with self.assertRaises(ValidationError, msg='Maximum possible profiles (Upgradable)'):
            Profile.objects.create(
                user=self.user,
                name='wicked',
                main=False
            )

    def test_multiple_main_profiles(self):
        self.user.tier = 'F'
        self.user.save()
        self.assertEqual(self.user.tier, 'F')
        with self.assertRaises(ValidationError, msg='A main profile already exists'):
            Profile.objects.create(
                user=self.user,
                name='wicked',
                main=True
            )

    def test_multiple_profiles(self):
        self.user.tier = 'F'
        self.user.save()
        self.assertEqual(self.user.tier, 'F')
        Profile.objects.create(
            user=self.user,
            name='wicked2',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked3',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked4',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked5',
            main=False
        )
        with self.assertRaisesRegex(ValidationError, 'A main profile already exists'):
            Profile.objects.create(
                user=self.user,
                name='wickeder',
                main=True
            )
        Profile.objects.create(
            user=self.user,
            name='wicked6',
            main=False
        )

        self.assertEqual(self.user.profile_set.count(), 6)

        with self.assertRaisesRegex(ValidationError, 'Maximum possible profiles'):
            Profile.objects.create(
                user=self.user,
                name='wicked7',
                main=False
            )

    def test_profiles_editing(self):
        profile = self.user.main_profile
        profile.name = 'june'
        profile.save()
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'june')

        # multiple profiles
        self.user.tier = 'F'
        self.user.save()
        Profile.objects.create(
            user=self.user,
            name='wicked2',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked3',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked4',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked5',
            main=False
        )
        px = Profile(
            user=self.user,
            name='wicked6',
            main=False
        )
        px.save()
        px.name = 'wicked6_edited'
        px.save()
        px_x = Profile.objects.get(pk=px.pk)
        self.assertEqual(px_x.name, 'wicked6_edited')

        # deleting profiles
        with self.assertRaisesRegex(ValidationError, 'Main profile cannot be deleted'):
            profile.delete()

        pre_count = self.user.profile_count
        px_x.delete()
        post_count = self.user.profile_count
        self.assertEqual(post_count, (pre_count - 1))

    def test_wrong_main_profile(self):
        self.user.tier = 'F'
        self.user.save()
        profile = self.user.main_profile
        profile.main = False
        profile.save()
        Profile.objects.create(
            user=self.user,
            name='wicked2',
            main=False
        )
        Profile.objects.create(
            user=self.user,
            name='wicked4',
            main=False
        )
        m = Profile(
            user=self.user,
            name='wicked3',
            main=True
        )
        m.save()
        self.assertEqual(self.user.main_profile.pk, m.pk)
        m.main = False
        m.save()
        self.assertEqual(self.user.main_profile, None)
