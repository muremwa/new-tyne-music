from typing import Dict, Union
from re import search, compile, findall

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework.authtoken.models import Token

from .models import User, Profile


class SmartForm:
    fields = {}

    """Add field information retrieval sugar"""
    def fields_info(self):
        """Get all fields with help_text and whether they are required"""
        fields_ = {}

        for key in self.fields:
            field_ = self.fields.get(key)

            if field_:
                fields_.update({
                    key: {
                        'help': field_.help_text if hasattr(field_, 'help_text') else '',
                        'required': field_.required if hasattr(field_, 'required') else False
                    }
                })
        return fields_


class CoreUserCreationForm(SmartForm, forms.Form):
    """
        If the form is valid returns a dict with:\n
        The new created user. -> 'new_user'\n
        And\n
        The user authtoken. -> 'token_key'
    """
    username = forms.CharField(max_length=191, required=True, help_text='A unique username', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter a username'}
    ))
    email = forms.EmailField(required=True, help_text='Your email address', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Your working email'}
    ))
    password = forms.CharField(required=True, help_text='A strong password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Strong password'}
    ))
    password_2 = forms.CharField(required=True, help_text='Repeat the password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Repeat the password'}
    ))

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

        # username exists
        if User.objects.filter(username=username).count() > 0:
            raise ValidationError(__(f'The username \'{username}\' already exists'))

        # weird characters
        pt = compile(r'[^0-9a-zA-Z_]')
        if search(pt, username):
            illegals = findall(pt, username)
            raise ValidationError(__(f'No special characters on username (like: {", ".join(illegals)}), except _'))

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)

        # email exists
        if User.objects.filter(email=email).count() > 0:
            raise ValidationError(__(f'The email \'{email}\' already exists'))
        return email

    def save(self) -> Dict[str, Union[User, Token]]:
        """
            If form is valid and data changed, returns \n
            {\n
                'new_user': User ->  USER instance,\n
                'token_key': Token.key -> STRING\n
            }\n
        """
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
            new_user_token: Token = Token.objects.create(user=new_user)
            return {
                'new_user': new_user,
                'token_key': new_user_token.key
            }


class CoreUserEditForm(CoreUserCreationForm):
    """
        Edits a user but doesn't return, it's assumed you have access to the user already.\n
        Takes a positional argument user, that is to be edited
    """
    password = None
    password_2 = None
    username = forms.CharField(required=False, help_text='A unique username')
    email = forms.CharField(required=False, help_text='Your email address')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = super().clean_username()
        return username

    def save(self):
        if self.has_changed():
            for field in self.changed_data:
                setattr(self.user, field, self.cleaned_data.get(field))
            self.user.save()


class ProfileCreateForm(SmartForm, forms.Form):
    """If the form is valid returns the new created profile"""
    profile_name = forms.CharField(required=True, help_text='A name for your profile')
    is_minor = forms.BooleanField(required=False, help_text='Is the profile for a child')
    profile_image = forms.ImageField(required=False, help_text='An image for your profile')
    account = forms.ModelChoiceField(queryset=User.objects.all())
    key_maps = {
        'profile_name': 'name',
        'profile_image': 'avi',
        'is_minor': 'minor',
        'account': 'user'
    }

    def clean(self):
        data: Dict = self.cleaned_data

        if 'account' in data.keys():
            account: User = data.get('account')
            if account.profile_full:
                raise ValidationError(__('Account limit reached'))
        return data

    def save(self):
        if self.has_changed():
            name = self.cleaned_data.get('profile_name')
            user = self.cleaned_data.get('account')
            minor = self.cleaned_data.get('is_minor')
            avi = self.cleaned_data.get('profile_image')

            if all([name, user]):
                new_profile = Profile(
                    name=name,
                    user=user,
                    minor=minor
                )

                if 'profile_image' in self.changed_data:
                    new_profile.avi = avi
                new_profile.save()

                return new_profile


class ProfileEditForm(ProfileCreateForm):
    """
        Edits an existing profile, nothing is returned.\n
        Takes a keyword argument profile, that is to be edited.
    """
    account = None
    profile_name = forms.CharField(required=False, help_text='A name for your profile')

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)

    def save(self):
        for field in self.cleaned_data.keys():
            a_name = self.key_maps.get(field)
            setattr(self.profile, a_name, self.cleaned_data.get(field))
        self.profile.save()
