from django.test import TestCase, tag

from core.models import User
from core.forms import CoreUserCreationForm, CoreUserEditForm


@tag('core-s')
class CoreFormTestCase(TestCase):
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

    def test_form_saving(self):
        usf = CoreUserCreationForm(data=self.data)

        if usf.is_valid():
            user = usf.save()
            users = User.objects.filter(username=self.data.get('username'))
            self.assertEqual(users.count(), 1)
            self.assertEqual(user.pk, users[0].pk)

    def test_form_edit_form(self):
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
