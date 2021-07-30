from django.db import models
from django.conf import settings


def upload_artist_image(instance: 'Artist', filename: str):
    return f'dy/music/artists/{instance.pk}/{filename}'


def upload_creator_image(instance: 'Creator', filename: str):
    return f'dy/music/creators/{instance.pk}/{filename}'


def upload_genre_image(instance: 'Genre', filename: str):
    return f'dy/music/creators/{instance.pk}/{filename}'


class Artist(models.Model):
    name = models.CharField(max_length=100)
    is_group = models.BooleanField(default=False)
    group_members = models.ManyToManyField('self')
    avi = models.ImageField(default='/defaults/artist.png', upload_to=upload_artist_image)
    cover = models.ImageField(default='/defaults/artist_large.png', upload_to=upload_artist_image)
    bio = models.TextField(blank=True, null=True)
    nicknames = models.TextField(blank=True, null=True, help_text='Comma separated names the artist goes by')
    objects = models.Manager()

    def add_artist_to_group(self, artist: 'Artist'):
        if self.is_group and type(artist) == type(self) and not artist.is_group:
            self.group_members.add(artist)

    def __str__(self):
        _type_ = 'Group' if self.is_group else 'Artist'
        return f'<{_type_} \'{self.name}\'>'


class Creator(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    avi = models.ImageField(default='/defaults/creator.png', upload_to=upload_creator_image)
    cover = models.ImageField(default='/defaults/creator_wide.png', upload_to=upload_creator_image)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    objects = models.Manager()

    def add_creator_user(self, user):
        if hasattr(user, 'is_staff') and user.is_staff:
            self.users.add(user)

    def __str__(self):
        return f'<TyneMusicContentCreator: \'{self.name}\'>'


class Genre(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    avi = models.ImageField(default='/defaults/genre.png', upload_to=upload_genre_image)
    cover = models.ImageField(default='/defaults/genre_wide.png', upload_to=upload_genre_image)
    objects = models.Manager()

    def __str__(self):
        return f'<Genre: \'{self.title}\'>'
