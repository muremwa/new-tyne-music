from django import forms
from django.db.models import Model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as __

from core.forms import SmartForm
from core.models import Profile
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


class ArtistForm(SmartForm, forms.ModelForm):

    class Meta:
        model = Artist
        exclude = ('group_members',)


class ArtistEditForm(ClassicModelEditForm):

    class Meta:
        model = Artist
        exclude = ('group_members',)

    def clean(self):
        if not self.instance.pk:
            raise ValidationError(__('Artist to be edited required'))

        return super().clean()


class AlbumForm(SmartForm, forms.ModelForm):

    class Media:
        js = ('js/ajaxWrapper.js', 'staff/js/album_form.js', 'staff/js/select_artists.js')
        css = {
            'all': ('staff/css/album_form.css', 'staff/css/select_artists.css')
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
        js = ('js/ajaxWrapper.js', 'staff/js/album_form.js', 'staff/js/select_artists.js')
        css = {
            'all': ('staff/css/album_form.css', 'staff/css/select_artists.css')
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
    length = forms.IntegerField(required=False, help_text='Length of the file, if it exists')

    class Meta:
        model = Song
        exclude = ('additional_artists', 'likes', 'streams')

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        length = cleaned_data.get('length')

        if length and not file:
            raise ValidationError(__('Length allowed when file is present'))

        return cleaned_data


class SongEditForm(ModelEditWithRelatedFields):
    track_no = forms.IntegerField(required=False)
    title = forms.CharField(required=False, max_length=100)
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), required=False)
    explicit = forms.BooleanField(required=False)
    file = forms.FileField(required=False)
    length = forms.IntegerField(required=False, help_text='Length of the file, if it exists')


class CreatorForm(SmartForm, forms.ModelForm):

    class Meta:
        model = Creator
        exclude = ('users', 'genres',)


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
