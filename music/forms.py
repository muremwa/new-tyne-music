from django import forms
from django.db.models import Model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as __
from django.core.files.images import get_image_dimensions

from mutagen import File

from core.forms import SmartForm
from core.models import Profile, User
from .models import Artist, Album, Genre, Disc, Song, Creator, CreatorSection, Playlist


class ClassicModelEditForm(SmartForm, forms.ModelForm):
    """This inherits from forms.ModelForm and sets every field as not required"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False


class ModelEditWithRelatedFields(SmartForm, forms.Form):
    """inherits from forms.Form and sets an instance to be updated"""
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        if isinstance(instance, Model):
            self.instance = instance

    def save(self, commit=True):
        if self.has_changed():
            for key in self.changed_data:
                if hasattr(self.instance, key):
                    new_value = self.cleaned_data.get(key)
                    setattr(self.instance, key, new_value)
            if commit:
                self.instance.save()
        return self.instance


class CleanArtist:
    class Media:
        css = {
            'all': ('staff/css/artists/artist_form.css',)
        }
        js = (
            'staff/js/artists/artist_form.js',
            'staff/js/aspectRatioCheck.js',
        )

    class Meta:
        model = Artist
        exclude = ('group_members',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'artist\'s name'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Something about the artist'}),
            'avi': forms.FileInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'nicknames': forms.HiddenInput()
        }

    @staticmethod
    def check_aspect_ratio(width: int, height: int, ratio: []) -> bool:
        """
        Checks whether the width and height are in the aspect ratio; ratio
        :param width: width of an item
        :type width: int
        :param height: height of an item
        :type height: int
        :param ratio: a list of ratio; if aspect ratio is 16:9 then ratio will be [16, 9]
        :type ratio: list
        :return: Whether or not the aspect ratio matches
        :rtype: bool
        """
        pro = (width / height) * ratio[-1]
        return pro == ratio[0]

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name and not self.instance:
            raise ValidationError(__('Name is required'))

        return name

    def clean_avi(self):
        avi = self.cleaned_data.get('avi')

        if avi and '/defaults/' not in str(avi):
            width, height = get_image_dimensions(avi)
            if not self.check_aspect_ratio(width, height, [1, 1]):
                raise ValidationError(__('Artist avi should 1:1'))

        return avi

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')

        if cover and '/defaults/' not in str(cover):
            width, height = get_image_dimensions(cover)
            if not self.check_aspect_ratio(width, height, [3, 1]):
                raise ValidationError(__('Artist cover should be 3:1'))

        return cover


class ArtistForm(SmartForm, CleanArtist, forms.ModelForm):
    pass


class ArtistEditForm(CleanArtist, ClassicModelEditForm):

    def clean(self):
        if not self.instance.pk:
            raise ValidationError(__('Artist to be edited required'))

        return super().clean()


class AlbumForm(SmartForm, forms.ModelForm):

    class Media:
        js = (
            'js/ajaxWrapper.js',
            'staff/js/aspectRatioCheck.js',
            'staff/js/albums/album_form.js',
            'staff/js/select_artists.js',
        )
        css = {
            'all': ('staff/css/albums/album_form.css', 'staff/css/select_artists.css')
        }

    class Meta:
        model = Album
        exclude = ('other_versions', 'artists', 'published', 'likes')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Album title...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Editor notes here...'}),
            'is_single': forms.CheckboxInput(attrs={'class': 'hidden-checks'}),
            'is_ep': forms.CheckboxInput(attrs={'class': 'hidden-checks'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'date_of_release': forms.DateInput(attrs={'class': 'form-select', 'type': 'date'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'copyright': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Copyright information...'})
        }


class AlbumEditForm(ModelEditWithRelatedFields):
    title = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    is_single = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'hidden-checks'}))
    is_ep = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'hidden-checks'}))
    cover = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    copyright = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), required=False, widget=forms.Select(attrs={
        'class': 'form-select',
    }))
    date_of_release = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-select',
        'type': 'date'
    }))

    class Media:
        js = (
            'js/ajaxWrapper.js',
            'staff/js/aspectRatioCheck.js',
            'staff/js/albums/album_form.js',
            'staff/js/select_artists.js',
        )
        css = {
            'all': ('staff/css/albums/album_form.css', 'staff/css/select_artists.css')
        }

    def clean(self):
        if not hasattr(self, 'instance'):
            raise ValidationError(__('Album to be edited required'))

        if self.cleaned_data.get('is_single') and self.cleaned_data.get('is_ep'):
            raise ValidationError(__('Single or EP not both'))

        return super().clean()


class GenreForm(SmartForm, forms.ModelForm):

    class Meta:
        model = Genre
        fields = '__all__'


class GenreEditForm(ClassicModelEditForm):

    class Meta:
        model = Genre
        fields = '__all__'


class DiscForm(SmartForm, forms.ModelForm):

    class Meta:
        model = Disc
        fields = '__all__'


class DiscEditForm(ModelEditWithRelatedFields):
    name = forms.CharField(max_length=100, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)


class SongForm(SmartForm, forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'audio/*'
    }))
    length = forms.IntegerField(required=False, help_text='Length of the file, if it exists')

    class Meta:
        model = Song
        exclude = ('additional_artists', 'likes', 'streams', 'disc')
        widgets = {
            'track_no': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter track number',
                'min': '1'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter song title'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    class Media:
        js = ('js/ajaxWrapper.js', 'staff/js/select_artists.js')
        css = {
            'all': ('staff/css/select_artists.css',)
        }

    def __init__(self, *args, **kwargs):
        song_disc = kwargs.pop('song_disc', None)
        super().__init__(*args, **kwargs)

        if isinstance(song_disc, Disc):
            self.song_disc = song_disc

    def clean_track_no(self):
        track_no = int(self.data.get('track_no'))

        if track_no:
            if track_no < 1:
                raise ValidationError(__('No negative track numbers'))

            if self.song_disc.song_set.filter(track_no=track_no):
                raise ValidationError(__(f'Another song with the track number "{track_no}" exists on this disc'))

        return track_no

    def clean_file(self):
        file = self.files.get('file')

        if file:
            x_file = File(file)

            if not x_file or not hasattr(x_file.info, 'length'):
                raise ValidationError(__('Wrong format audio  file'))

        return file


class SongEditForm(ModelEditWithRelatedFields):
    track_no = forms.IntegerField(required=False, label='Track Number', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter track number', 'min': '1'}
    ))
    title = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter song title'
    }))
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), required=False, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'audio/*'
    }))
    explicit = forms.BooleanField(required=False)
    length = forms.IntegerField(required=False, help_text='Length of the file, if it exists')

    class Media:
        js = ('js/ajaxWrapper.js', 'staff/js/select_artists.js')
        css = {
            'all': ('staff/css/select_artists.css',)
        }

    def clean_track_no(self):
        track_no = self.data.get('track_no')

        if track_no:
            track_no = int(track_no)
            if track_no < 1:
                raise ValidationError(__('No negative track numbers'))

            if self.instance:
                if self.instance.disc.song_set.filter(track_no=track_no).exclude(pk=self.instance.pk).count() != 0:
                    raise ValidationError(__(f'Another song with the track number "{track_no}" exists'))

        return track_no

    def clean_file(self):
        file = self.files.get('file')

        if file:
            x_file = File(file)

            if not x_file or not hasattr(x_file.info, 'length'):
                raise ValidationError(__('Wrong format audio  file'))

        return file


class CreatorForm(SmartForm, forms.ModelForm):

    class Meta:
        model = Creator
        exclude = ('users', 'genres',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '6'}),
            'avi': forms.FileInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CreatorEditForm(ClassicModelEditForm):

    class Meta:
        model = Creator
        exclude = ('users', 'genres',)


class CreatorSectionForm(SmartForm, forms.ModelForm):

    class Meta:
        model = CreatorSection
        fields = ('name', 'creator')


class CreatorSectionEditForm(SmartForm, forms.ModelForm):

    class Meta:
        model = CreatorSection
        fields = ('name',)


class ProfilePlaylistForm(SmartForm, forms.ModelForm):
    profile = forms.ModelChoiceField(queryset=Profile.objects.all())

    class Meta:
        model = Playlist
        fields = ('title', 'description', 'profile', 'cover')

    def save(self, commit=True):
        playlist: Playlist = super().save(commit=True)
        playlist.og_order()
        return playlist


class ProfilePlaylistEditForm(ClassicModelEditForm):

    class Meta:
        model = Playlist
        fields = ('title', 'description', 'cover')


class CreatorPlaylistForm(SmartForm, forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=Creator.objects.all())

    class Meta:
        model = Playlist
        fields = ('title', 'description', 'creator', 'cover', 'cover_wide', 'timely_cover', 'timely_cover_wide')


class CreatorPlaylistEditForm(ClassicModelEditForm):

    class Meta:
        model = Playlist
        fields = ('title', 'description', 'cover', 'cover_wide', 'timely_cover', 'timely_cover_wide')


class CreatorGenreForm(forms.ModelForm):

    class Meta:
        model = Creator
        fields = ('genres',)
        widgets = {
            'genres': forms.SelectMultiple(attrs={'class': 'form-control s-field'})
        }


class MultipleUserChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.username} ({obj.email})'


class CreatorUsersForm(forms.ModelForm):
    users = MultipleUserChoiceField(
        queryset=User.objects.filter(is_staff=True).filter(
            groups__permissions__codename='add_playlist'
        ).filter(
            groups__permissions__codename='change_playlist'
        ).filter(
            groups__permissions__codename='add_creatorsection'
        ).filter(
            groups__permissions__codename='change_creatorsection'
        ),
        widget=forms.SelectMultiple(attrs={'class': 'form-control s-field'}),
        required=False
    )

    class Meta:
        model = Creator
        fields = ('users',)
