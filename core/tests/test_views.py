from django.test import tag
from django.shortcuts import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from core.views import CREATE_USER, EDIT_USER, GET_USER
from core.models import User, Profile
from core.serializers import UserSerializer, ProfileSerializer
from core.forms import CoreUserCreationForm, CoreUserEditForm, ProfileCreateForm, ProfileEditForm


# noinspection PyPep8Naming
@tag('core-v-a')
class AccountActionTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='view_user',
            email='email@test.com',
            password='pass@123'
        )
        self.def_resp = {
            'url': 'account action',

        }

    def test_unknown_action(self):
        NOT_AN_ACTION = 'not_an_action'
        self.def_resp.update({
            "404 Error": f"{NOT_AN_ACTION} not supported",
            "urls_supported": [
                "/core/accounts/create/",
                "/core/accounts/edit/",
                "/core/accounts/get/?username=user"
            ]
        })
        response = self.client.get(reverse('core:account-action', kwargs={'action': NOT_AN_ACTION}))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), self.def_resp)

    @tag('core-v-a-gu')
    def test_get_user(self):
        url = f"{reverse('core:account-action', kwargs={'action': GET_USER})}?username={self.user.username}"
        user_info = UserSerializer(self.user).data
        profiles = user_info.pop('profiles')
        self.def_resp.update({
            "action": "Retrieve user",
            "user": user_info
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.def_resp)

        self.client.force_login(user=self.user)
        response = self.client.get(url)
        user_info.update({
            'profiles': profiles
        })
        self.def_resp.update({
            'user': user_info
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.def_resp)

    def test_create_user_get(self):
        url = reverse('core:account-action', kwargs={'action': CREATE_USER})

        self.def_resp.update({
            "action": "Create a new user",
            'login_required': False,
            "fields": CoreUserCreationForm().fields_info()
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), self.def_resp)

    def test_create_user_post(self):
        url = reverse('core:account-action', kwargs={'action': CREATE_USER})
        # POST data with errors
        data = {
            'username': self.user.username,
            'email': 'test@email.com',
            'password': 'pass@123',
            'password_2': 'pass@123'
        }
        self.def_resp.update(dict(
            errors={
                'username': [f'The username \'{self.user.username}\' already exists'],
            },
            success=False,
            action='Create user'
        ))
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 202)
        self.assertDictEqual(response.json(), self.def_resp)

        # correct data
        data.update({
            'username': 'abs_new_username'
        })
        self.def_resp.update(dict(
            success=True,
        ))
        self.def_resp.pop('errors')
        response = self.client.post(url, data=data)
        user = User.objects.get(username='abs_new_username')
        token = Token.objects.get(user=user)
        self.def_resp.update({
            'new_user': UserSerializer(user).data,
            'user_token': token.key
        })
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), self.def_resp)

    def test_edit_user_get(self):
        url = reverse('core:account-action', kwargs={'action': EDIT_USER})

        self.def_resp.update({
            'action': 'Edit an existing user',
            'login_required': True,
            'fields': CoreUserEditForm(user=None).fields_info()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), self.def_resp)

    @tag('core-v-a-ep')
    def test_edit_user_post(self):
        url = reverse('core:account-action', kwargs={'action': EDIT_USER})

        # without being authenticated
        response = self.client.post(url, data={
            'username': 'jim'
        })
        self.def_resp.update({
            'success': False,
            'error': 'user is not authenticated'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), self.def_resp)
        self.def_resp.pop('error')

        # authenticate user
        self.client.force_login(self.user)

        # authenticated user with wrong details
        data = {
            'username': '&username',
            'email': 'email'
        }
        for key in data.keys():
            datum = {key: data.get(key)}

            form = CoreUserEditForm(data=datum, user=self.user)
            response = self.client.post(url, data=datum)
            self.def_resp.update({
                'errors': form.errors
            })
            self.assertEqual(response.status_code, 400)
            self.assertDictEqual(response.json(), self.def_resp)
            self.def_resp.pop('errors')

        # authenticated user correct details
        data = {
            'username': 'new_username',
            'email': 'email_new@test.com'
        }
        self.def_resp['success'] = True

        # both details
        response = self.client.post(url, data=data)
        self.def_resp.update({
            'edited': data
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(self.def_resp, response.json())
        for key in data.keys():
            self.assertEqual(getattr(self.user, key), data.get(key))
        self.def_resp.pop('edited')

        # each detail
        data = {
            'username': 'username_r',
            'email': 'email_r@test.com'
        }
        for key in data.keys():
            datum = {
                key: data.get(key)
            }
            response = self.client.post(url, data=datum)
            self.def_resp.update({
                'edited': datum
            })
            self.user.refresh_from_db()
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(self.def_resp, response.json())
            self.assertEqual(getattr(self.user, key), datum[key])
            self.def_resp.pop('edited')


@tag('core-v-l')
class LoginTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self._pass = 'pass@123'
        self.user = User.objects.create_user(
            username='login_user',
            email='email@test.com',
            password=self._pass
        )
        self.def_resp = {
            'url': 'user authentication',
        }
        self.url = reverse('core:login')

    def test_login_get(self):
        self.def_resp.update({
            'fields': ['username', 'email', 'password'],
            'returns': ['token', 'user_data']
        })
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), self.def_resp)

    def test_login_post_wrong_data(self):
        self.def_resp.update({
            'success': False,
            'error': 'Wrong Credentials'
        })
        response = self.client.post(self.url, data={
            'username': self.user.username,
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), self.def_resp)

    def test_login_with_username_or_email(self):
        self.def_resp.update({
            'success': True,
            'token': self.user.get_user_auth_token().key,
            'details': UserSerializer(self.user).data
        })

        # login with username
        response = self.client.post(self.url, data={
            'username': self.user.username,
            'password': self._pass
        })
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), self.def_resp)

        # login with email
        response = self.client.post(self.url, data={
            'email': self.user.email,
            'password': self._pass
        })
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), self.def_resp)

        # login with email and username
        response = self.client.post(self.url, data={
            'username': self.user.username,
            'email': self.user.email,
            'password': self._pass
        })
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), self.def_resp)


@tag('core-v-p')
class ProfileActionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='login_user',
            email='email@test.com',
            password='pass@123'
        )
        self.client = APIClient()
        self.create_url = reverse('core:profile-create')
        self.edit_url = reverse('core:profile-edit', kwargs={'profile_pk': self.user.main_profile.pk})

    @tag('core-v-p-cg')
    def test_create_get(self):
        # user not authenticated
        resp = {"detail": "Authentication credentials were not provided."}
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(response.json(), resp)

        self.client.force_login(user=self.user)

        # user authenticated
        _fields = ProfileCreateForm().fields_info()
        _fields.pop('account')
        resp = {
            'url action': 'Create profiles',
            'fields': _fields
        }
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(resp, response.json())

    def test_create_post(self):
        # user not authenticated
        resp = {"detail": "Authentication credentials were not provided."}
        response = self.client.post(self.create_url)
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(response.json(), resp)

        self.client.force_login(user=self.user)

        # authenticated user - account limit reached
        data = {
            'profile_name': 'jimmy',
            'account': self.user.pk
        }
        form = ProfileCreateForm(data)
        errors = form.errors
        data.pop('account')

        resp = {
            'url action': 'Create profiles',
            'success': False,
            'errors': errors
        }
        response = self.client.post(self.create_url, data=data)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), resp)

        # authenticated user - correct details
        self.user.tier = 'F'
        self.user.save()
        data = {
            'profile_name': 'jimmy',
        }
        response = self.client.post(self.create_url, data=data)
        resp = {
            'url action': 'Create profiles',
            'success': True,
            'profile': ProfileSerializer(self.user.profile_set.get(pk=2)).data
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), resp)

    @tag('core-v-p-eg')
    def test_profile_edit_get(self):
        # user not authenticated
        resp = {"detail": "Authentication credentials were not provided."}
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(response.json(), resp)

        self.client.force_login(user=self.user)

        # user authenticated
        _fields = ProfileEditForm(profile=None).fields_info()
        resp = {
            'url action': f'Profile id \'{self.user.main_profile.pk}\' edit',
            'fields': _fields
        }
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(resp, response.json())

    @tag('core-v-p-ep')
    def test_profile_post(self):
        # without being authenticated
        response = self.client.post(self.edit_url, data={
            'profile_name': 'test_profile_name'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Authentication credentials were not provided."})

        # authenticate user
        self.client.force_login(self.user)

        # profile does not belong to you
        p = Profile(
            name='jus_name',
            user=User.objects.create_user(
                username='e',
                email='e@e.com',
                password='pass@123',
                tier='F'
            )
        )
        p.save()

        response = self.client.post(reverse('core:profile-edit', kwargs={'profile_pk': p.pk}))
        self.assertEqual(response.status_code, 404)

        # authenticated user correct details
        profile = self.user.main_profile
        data = {
            'profile_name': 'new_profile_name',
            'is_minor': True
        }
        def_resp = {
            'url action': f'Profile id \'{self.user.main_profile.pk}\' edit',
            'success': True,
            'edited': data
        }
        keys_ = ProfileEditForm(profile=None).key_maps

        # both details
        response = self.client.post(self.edit_url, data=data)
        profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(def_resp, response.json())
        for key in data.keys():
            self.assertEqual(getattr(profile, keys_[key]), data.get(key))
        def_resp.pop('edited')

        # each detail
        data = {
            'profile_name': 'ind_name',
            'is_minor': False
        }
        for key in data.keys():
            datum = {
                key: data.get(key)
            }
            response = self.client.post(self.edit_url, data=datum)
            def_resp.update({
                'edited': datum
            })
            profile.refresh_from_db()
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(def_resp, response.json())
            self.assertEqual(getattr(profile, keys_[key]), datum[key])
            def_resp.pop('edited')
