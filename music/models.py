from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as __
from django.core.exceptions import ValidationError


def upload_artist_image(instance: 'Artist', filename: str):
    return f'dy/music/artists/{instance.pk}/{filename}'


def upload_creator_image(instance: 'Creator', filename: str):
    return f'dy/music/creators/{instance.pk}/{filename}'


def upload_genre_image(instance: 'Genre', filename: str):
    return f'dy/music/creators/{instance.pk}/{filename}'


def upload_album_image(instance: 'Album', filename: str):
    return f'dy/music/albums/{instance.pk}/{filename}'


def upload_song_file(instance: 'Song', filename: str):
    return f'dy/music/albums/{instance.album.pk}/{instance.pk}/{filename}'


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

    def __repr__(self):
        return self.__str__()


class Genre(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    avi = models.ImageField(default='/defaults/genre.png', upload_to=upload_genre_image)
    cover = models.ImageField(default='/defaults/genre_wide.png', upload_to=upload_genre_image)
    objects = models.Manager()

    def __str__(self):
        return f'<Genre: \'{self.title}\'>'

    def __repr__(self):
        return self.__str__()


class Album(models.Model):
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    date_of_release = models.DateField()
    is_single = models.BooleanField(default=False)
    is_ep = models.BooleanField(default=False)
    cover = models.ImageField(default='/defaults/album.png', upload_to=upload_album_image)
    likes = models.IntegerField(default=0, null=True, blank=True)
    copyright = models.TextField(blank=True, null=True)
    artists = models.ManyToManyField(Artist, blank=True)
    other_versions = models.ManyToManyField('self', blank=True)
    objects = models.Manager()

    @property
    def album_type(self):
        t = 'Long Play'
        if self.is_ep:
            t = 'Extended Play'
        elif self.is_single:
            t = 'Single'

        return t

    def add_sister_album(self, album):
        if type(album) == type(self) and self.pk:
            self.other_versions.add(album)

    def clean(self):
        if self.is_single and self.is_ep:
            raise ValidationError(__('EP or Single not both'))

        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        name = 'Album'
        if self.is_ep:
            name = 'EP'
        elif self.is_single:
            name = 'Single'

        return f'<{name}: \'{self.title}\'>'


class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    track_no = models.IntegerField()
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    explicit = models.BooleanField(default=False)
    length = models.IntegerField(default=0, help_text='Length of the song in seconds')
    file = models.FileField(blank=True, null=True, upload_to=upload_song_file)
    likes = models.IntegerField(default=0, blank=True, null=True)
    additional_artists = models.ManyToManyField(Artist, blank=True)
    streams = models.IntegerField(default=0, blank=True, null=True)
    objects = models.Manager()

    class Meta:
        unique_together = (('album', 'track_no'),)

    @property
    def length_string(self):
        l = '0:00'
        if self.pk and self.length:
            l = f'{self.length // 60}:{self.length % 60}'
        return l

    def add_additional_artist(self, artist):
        if self.pk and type(artist) == Artist and artist not in self.album.artists.all():
            self.additional_artists.add(artist)

    def __str__(self):
        return f'<Song: \'{self.title}\' from \'{self.album.title}\'>'
