from django.test import TestCase, tag

from core.models import Profile, User, FAMILY
from core.serializers import ProfileSerializer, UserSerializer


@tag('core-s')
class SerializersTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.user = User.objects.create_user(
            username='stest',
            first_name='Test',
            last_name='One',
            email='test@test.com',
            password='testing@123',
            tier='F'
        )

        self.profile_2 = Profile(
            name='profile2',
            main=False,
            user=self.user
        )
        self.profile_2.save()

    def test_profile_serializer_data(self):
        test_data = {
            'name': 'profile2',
            'minor': False,
            'main': False,
            'avi': '/media/defaults/default_profile.jpg',
            'tier': FAMILY
        }
        ps = ProfileSerializer(self.profile_2)
        self.assertDictEqual(test_data, ps.data)

    def test_user_serializer_data(self):
        test_data = {
            'username': 'stest',
            'email': 'test@test.com',
            'tier': 'F',
            'tier_name': FAMILY,
            'profile_full': False,
            'profiles': [
                {
                    'name': 'stest',
                    'minor': False,
                    'main': True,
                    'avi': '/media/defaults/default_profile.jpg',
                    'tier': FAMILY
                },
                {
                    'name': 'profile2',
                    'minor': False,
                    'main': False,
                    'avi': '/media/defaults/default_profile.jpg',
                    'tier': FAMILY
                }
            ]
        }
        us = UserSerializer(self.user)
        self.assertDictEqual(test_data, us.data)
