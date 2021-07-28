from typing import Dict, List

from django.test import TestCase, tag
from rest_framework.authtoken.models import Token

from core.models import User, Profile
from core.forms import CoreUserCreationForm, CoreUserEditForm, ProfileCreateForm, ProfileEditForm


@tag('core-fu')
class CoreUserFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test1',
            email='test@test.com',
            password='pass@123'
        )
        self.data = {
            'username': 'test2',
            'email': 'test1@test.com',
            'password': 'pass@123',
            'password_2': 'pass@123'
        }

    @tag('core-fu-ue')
    def test_username_exists(self):
        self.data.update({
            'username': self.user.username
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertEqual(usf.is_valid(), False)
        self.assertEqual(usf.errors.get('username', []), [f'The username \'{self.user.username}\' already exists'])

    @tag('core-fu-ee')
    def test_email_exists(self):
        self.data.update({
            'email': self.user.email
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertEqual(usf.is_valid(), False)
        self.assertEqual(usf.errors.get('email', []), [f'The email \'{self.user.email}\' already exists'])

    def test_passwords_similar(self):
        self.data.update({
            'password_2': '24224'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('password', []), ['The passwords do not match'])

    def test_passwords_similar_to_email_and_username(self):
        self.data.update({
            'username': 'tynemusicsite',
            'password': 'tynemusicsite123',
            'password_2': 'tynemusicsite123',
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('password', []), ['The password is too similar to the username.'])

        self.data.update({
            'username': 'time',
            'email': 'tynemusic@tyme.com'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('password', []), ['The password is too similar to the email.'])

    def test_weird_username(self):
        self.data.update({
            'username': '&unhinged'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('username', []), [
            'Enter a valid username. This value may contain only letters, numbers, and _ character.'
        ])

        self.data.update({
            'username': '@un-hinged'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('username', []), [
            'No special characters on username (like: @, -), except _'
        ])

    def test_email(self):
        self.data.update({
            'email': 'next@tyne'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('email', []), ['Enter a valid email address.'])

        self.data.update({
            'email': 'nexttyne.com'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('email', []), ['Enter a valid email address.'])

        self.data.update({
            'email': 'nexttyne'
        })
        usf = CoreUserCreationForm(data=self.data)
        self.assertListEqual(usf.errors.get('email', []), ['Enter a valid email address.'])

    @tag('core-fu-fs')
    def test_form_saving(self):
        usf = CoreUserCreationForm(data=self.data)

        if usf.is_valid():
            user_data: Dict = usf.save()
            self.assertListEqual(list(user_data.keys()), ['new_user', 'token_key'])
            user = user_data.get('new_user')
            token = user_data.get('token_key')
            users = User.objects.filter(username=self.data.get('username'))
            tokens: List[Token] = list(Token.objects.filter(user=users[0]))
            self.assertEqual(users.count(), 1)
            self.assertEqual(len(tokens), 1)
            self.assertEqual(user.pk, users[0].pk)
            self.assertEqual(token, tokens[0].key)

    @tag('core-fu-uef')
    def test_form_edit_form(self):
        x = User(
            username='w',
            email='a@b.com',
            password='pass@123',
        )
        x.save()

        # duplicate email address
        uef = CoreUserEditForm(data={
            'email': x.email
        }, user=self.user)
        self.assertEqual(uef.is_valid(), False)
        self.assertListEqual(uef.errors.get('email', []), [f'The email \'{x.email}\' already exists'])

        # duplicate username
        uef = CoreUserEditForm(data={
            'username': x.username
        }, user=self.user)
        self.assertEqual(uef.is_valid(), False)
        self.assertListEqual(uef.errors.get('username', []), [f'The username \'{x.username}\' already exists'])

        # bad email
        uef = CoreUserEditForm(data={
            'email': 'bad_email'
        }, user=self.user)
        self.assertListEqual(uef.errors.get('email', []), ['Enter a valid email address.'])

        # bad username
        uef = CoreUserEditForm(data={
            'username': '@bad_email'
        }, user=self.user)
        self.assertListEqual(uef.errors.get('username', []), [
            'No special characters on username (like: @), except _'
        ])

        # correct username
        uef = CoreUserEditForm(data={
            'username': 'good_user'
        }, user=self.user)
        self.assertEqual(uef.is_valid(), True)
        if uef.is_valid():
            uef.save()
            us = User.objects.get(pk=self.user.pk)
            self.assertEqual(us.username, 'good_user')

        # correct email
        uef = CoreUserEditForm(data={
            'email': 'good@email.com'
        }, user=self.user)
        self.assertEqual(uef.is_valid(), True)
        if uef.is_valid():
            uef.save()
            us = User.objects.get(pk=self.user.pk)
            self.assertEqual(us.email, 'good@email.com')

        # both correct username & email
        uef = CoreUserEditForm(data={
            'username': 'tyne_user',
            'email': 'new@tyne.com'
        }, user=self.user)
        self.assertEqual(uef.is_valid(), True)
        if uef.is_valid():
            uef.save()
            us = User.objects.get(pk=self.user.pk)
            self.assertEqual(us.username, 'tyne_user')
            self.assertEqual(us.email, 'new@tyne.com')

    @tag('core-fu-sm')
    def test_smart_fields_info(self):
        c_form = CoreUserCreationForm()

        creator = {
            'username': {
                'help': c_form.fields.get('username').help_text,
                'required': c_form.fields.get('username').required
            },
            'email': {
                'help': c_form.fields.get('email').help_text,
                'required': c_form.fields.get('email').required
            },
            'password': {
                'help': c_form.fields.get('password').help_text,
                'required': c_form.fields.get('password').required
            },
            'password_2': {
                'help': c_form.fields.get('password_2').help_text,
                'required': c_form.fields.get('password_2').required
            },

        }

        self.assertDictEqual(c_form.fields_info(), creator)

        e_form = CoreUserEditForm(user=None)

        editor = {
            'username': {
                'help': e_form.fields.get('username').help_text,
                'required': False
            },
            'email': {
                'help': e_form.fields.get('email').help_text,
                'required': False
            }
        }

        self.assertDictEqual(e_form.fields_info(), editor)


@tag('core-fp')
class ProfileFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test1',
            email='test@test.com',
            password='pass@123',
        )

    def test_profile_creation_form(self):
        # account full
        pcf = ProfileCreateForm(data={
            'profile_name': 'name_1',
            'account': self.user.pk,
        })
        self.assertEqual(pcf.is_valid(), False)
        self.assertListEqual(pcf.errors.get('__all__', []), ['Account limit reached'])

        self.user.tier = 'F'
        self.user.save()

        # no account
        pcf = ProfileCreateForm(data={
            'profile_name': 'name_1'
        })
        self.assertEqual(pcf.is_valid(), False)
        self.assertListEqual(pcf.errors.get('account', []), ['This field is required.'])

        # no profile_name
        pcf = ProfileCreateForm(data={
            'account': self.user.pk,
        })
        self.assertEqual(pcf.is_valid(), False)
        self.assertListEqual(pcf.errors.get('profile_name', []), ['This field is required.'])

        # correct details
        pcf = ProfileCreateForm(data={
            'profile_name': 'name_1',
            'account': self.user.pk,
        })
        self.assertEqual(pcf.is_valid(), True)
        if pcf.is_valid():
            new_profile = pcf.save()
            self.assertEqual(new_profile in list(self.user.profile_set.all()), True)
            self.assertEqual(new_profile.main, False)
            self.assertEqual(new_profile.minor, False)

        # correct details with minor as true
        pcf = ProfileCreateForm(data={
            'profile_name': 'name_1',
            'account': self.user.pk,
            'is_minor': True
        })
        self.assertEqual(pcf.is_valid(), True)
        if pcf.is_valid():
            new_profile = pcf.save()
            self.assertEqual(new_profile in list(self.user.profile_set.all()), True)
            self.assertEqual(new_profile.main, False)
            self.assertEqual(new_profile.minor, True)

    def test_profile_edit_form(self):
        x_profile: Profile = self.user.main_profile

        # name
        pef = ProfileEditForm({
            'profile_name': 'new_name'
        }, profile=x_profile)
        self.assertEqual(pef.is_valid(), True)

        if pef.is_valid():
            pef.save()
            x_profile.refresh_from_db()
            self.assertEqual(x_profile.name, 'new_name')

        # minor
        pef = ProfileEditForm({
            'is_minor': True
        }, profile=x_profile)
        self.assertEqual(pef.is_valid(), True)

        if pef.is_valid():
            pef.save()
            x_profile.refresh_from_db()
            self.assertEqual(x_profile.minor, True)

    @tag('core-fp-sm')
    def test_smart_profile_form(self):
        c_form = ProfileCreateForm()

        creator = {
            'profile_name': {
                'help': c_form.fields.get('profile_name').help_text,
                'required': c_form.fields.get('profile_name').required
            },
            'profile_image': {
                'help': c_form.fields.get('profile_image').help_text,
                'required': c_form.fields.get('profile_image').required
            },
            'is_minor': {
                'help': c_form.fields.get('is_minor').help_text,
                'required': c_form.fields.get('is_minor').required
            },
            'account': {
                'help': c_form.fields.get('account').help_text,
                'required': c_form.fields.get('account').required
            }
        }

        self.assertDictEqual(c_form.fields_info(), creator)

        e_form = ProfileEditForm(profile=None)

        editor = {
            'profile_name': {
                'help': e_form.fields.get('profile_name').help_text,
                'required': False
            },
            'profile_image': {
                'help': e_form.fields.get('profile_image').help_text,
                'required': False
            },
            'is_minor': {
                'help': e_form.fields.get('is_minor').help_text,
                'required': False
            },

        }

        self.assertDictEqual(e_form.fields_info(), editor)
