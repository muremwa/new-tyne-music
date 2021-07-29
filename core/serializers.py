from rest_framework.serializers import ModelSerializer, BooleanField, CharField, IntegerField

from .models import User, Profile


class ProfileSerializer(ModelSerializer):
    id = IntegerField(source='pk')

    class Meta:
        model = Profile
        fields = ('id', 'name', 'minor', 'main', 'avi', 'tier')


class UserSerializer(ModelSerializer):
    profiles = ProfileSerializer(source='profile_set', many=True)
    profile_full = BooleanField()
    tier_name = CharField(source='c_tier')

    class Meta:
        model = User
        fields = ('username', 'email', 'tier', 'tier_name', 'profiles', 'profile_full')
