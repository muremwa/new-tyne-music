from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as __
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.authtoken.models import Token


SINGLE = 'Single'
FAMILY = 'Family'

TIERS = (
    ('S', SINGLE),
    ('F', FAMILY)
)


class User(AbstractUser):
    email = models.EmailField(blank=False, null=False, unique=True)
    tier = models.CharField(max_length=2, choices=TIERS, default='S')

    def clean(self):
        if not self.email:
            raise ValidationError(__('Email field required'))

        if not self.pk and User.objects.filter(email=self.email).count() > 0:
            raise ValidationError(__('User with this Email already exists'))

        return super().clean()

    @property
    def c_tier(self):
        if self.tier == 'S':
            return SINGLE
        elif self.tier == 'F':
            return FAMILY

    @property
    def main_profile(self):
        all_profiles = self.profile_set.order_by('pk')
        main_profiles = [profile for profile in all_profiles if profile.main]

        if len(main_profiles) == 0:
            return None

        else:
            return main_profiles[0]

    @property
    def profile_count(self):
        return self.profile_set.count()

    @property
    def profile_full(self):
        max_ = 1 if self.tier == 'S' else 6
        return self.profile_count >= max_

    def get_user_auth_token(self):
        token = None
        if self.pk:
            tokens = Token.objects.filter(user=self.pk)

            if tokens.count() == 1:
                token = tokens[0]
            elif tokens.count() == 0:
                user = User.objects.get(pk=self.pk)
                token = Token.objects.create(user=user)

        return token

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        # create a profile for the first time
        if not self.main_profile:
            profile = Profile(
                user=self,
                name=self.username,
                main=True,
            )
            profile.save()

        return self


def upload_avi(instance: 'Profile', filename: str):
    return f'dy/accounts/{instance.user.pk}/{instance.pk}/{filename}'


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    main = models.BooleanField(default=False)
    minor = models.BooleanField(default=False)
    avi = models.ImageField(upload_to=upload_avi, default='/defaults/default_profile.jpg')
    objects = models.Manager()

    @property
    def tier(self):
        if self.user.tier == 'S':
            return SINGLE
        elif self.user.tier == 'F':
            return FAMILY

    @property
    def email(self):
        return self.user.email

    def delete(self, *args, **kwargs):
        if self.main:
            raise ValidationError(__('Main profile cannot be deleted'))

        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save()

    def clean(self):
        profile_count = self.user.profile_set.count()

        if not self.pk and self.user.tier == 'S' and profile_count > 0:
                raise ValidationError(__('Maximum possible profiles (Upgradable)'))

        if not self.pk and self.user.main_profile and self.main:
            raise ValidationError(__('A main profile already exists'))

        elif not self.pk and self.user.tier == 'F' and profile_count > 5:
            raise ValidationError(__('Maximum possible profiles'))

        return super().clean()

    def __str__(self):
        return f'{self.name}(profile from {self.user.email})'
