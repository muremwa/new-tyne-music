from django.test import tag
from django.shortcuts import reverse
from rest_framework.test import APITestCase, APIClient

from core.views import account_action, CREATE_USER, EDIT_USER, GET_USER
from core.models import User
from core.serializers import UserSerializer
from core.forms import CoreUserCreationForm, CoreUserEditForm


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

    def test_get_user(self):
        url = f"{reverse('core:account-action', kwargs={'action': GET_USER})}?username={self.user.username}"
        self.def_resp.update({
            "action": "Retrieve user",
            "user": UserSerializer(self.user).data
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.def_resp)

    def test_create_user_get(self):
        url = reverse('core:account-action', kwargs={'action': CREATE_USER})

        self.def_resp.update({
            "action": "Create a new user",
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
        self.def_resp.update({
            'new_user': UserSerializer(user).data
        })
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), self.def_resp)

    def test_edit_user_get(self):
        url = reverse('core:account-action', kwargs={'action': EDIT_USER})

        self.def_resp.update({
            'action': 'Edit an existing user',
            'fields': CoreUserEditForm(user=None).fields_info()
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), self.def_resp)

    def test_edit_user_post(self):
        url = reverse('core:account-action', kwargs={'action': EDIT_USER})

        data_1 = {
            'username': self.user.username,
        }
