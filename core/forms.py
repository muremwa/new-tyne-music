from typing import Dict
from re import search, compile, findall

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

from .models import User


class CoreUserCreationForm(forms.Form):
    username = forms.CharField(max_length=191)
    email = forms.EmailField()
    password = forms.CharField()
    password_2 = forms.CharField()

    @property
    def errors(self):
        errors: Dict = super().errors
        term = '@/./+/-/_'

        if errors.get('username'):
            for key, error in enumerate(errors.get('username', [])):
                if term in error:
                    repaired_term = error.replace(f'{term} characters', '_ character')
                    errors['username'][key] = repaired_term

        return errors

    def clean_password(self):
        data: Dict = self.cleaned_data
        password1 = data.get('password')
        password2 = self.data.get('password_2')
        email = data.get('email')
        username = data.get('username')

        # passwords not similar
        if password1 != password2:
            raise ValidationError(__('The passwords do not match'))

        # similar to the email
        t_user = User(
            username=username,
            email=email
        )
        validate_password(password1, t_user)

        return password1

    def clean_username(self):
        username = self.cleaned_data.get('username')
        User.username_validator(username)

        # weird characters
        pt = compile(r'[^0-9a-zA-Z_]')
        if search(pt, username):
            illegals = findall(pt, username)
            raise ValidationError(__(f'No special characters on username (like: {", ".join(illegals)}), except _'))

        return username

    def save(self):
        data: Dict = self.cleaned_data
        av_items = data.keys()
        req_items = ['username', 'email', 'password']
        missing_keys = [key for key in req_items if key not in av_items]

        if len(missing_keys) == 0:
            new_user = User(
                username=data['username'],
                email=data['email'],
            )
            new_user.set_password(data['password'])
            new_user.save()
            return new_user


class CoreUserEditForm(CoreUserCreationForm):
    password = None
    password_2 = None
    username = forms.CharField(required=False)
    email = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = super().clean_username()
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
        return email

    def save(self):
        if self.has_changed():
            for field in self.changed_data:
                setattr(self.user, field, self.cleaned_data.get(field))
            self.user.save()
