from typing import List
from re import findall

from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, reverse, redirect

from .models import Artist, Creator, Genre, Album, Song, Playlist, CreatorSection, LibraryAlbum, Disc


@admin.register(Artist)
class Artist(admin.ModelAdmin):
    GRP_INFO_NAME = 'Group Info'
    fieldsets = [
        (
            None, {
                'fields': ['name']
            }
        ),
        (
            GRP_INFO_NAME, {
                'fields': ['is_group', 'group_members']
            }
        ),
        (
            'Information', {
                'fields': ['bio', 'avi', 'cover']
            }
        ),
        (
            'Misc', {
                'fields': ['nicknames']
            }
        )
    ]
    readonly_fields = ['group_members', 'is_group']
    list_filter = ['is_group']
    list_display = ['name', 'is_group']

    def get_readonly_fields(self, request, obj=None):
        r_fields = super().get_readonly_fields(request, obj)
        if 'add' in request.path.split('/'):
            r_fields = []
        return r_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and not obj.is_group:
            fieldsets = [field_set for field_set in fieldsets if field_set[0] != self.GRP_INFO_NAME]
        return fieldsets


@admin.register(CreatorSection)
class CreatorSectionModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator']
    list_filter = ['creator']
    search_fields = ['name', 'creator']
    fieldsets = [
        (
            None, {
                'fields': ['name', 'creator']
            }
        ),
        (
            'Items', {
                'fields': ['artists', 'albums', 'playlists']
            }
        )
    ]


class CreatorSectionInline(admin.StackedInline):
    model = CreatorSection
    extra = 1
    show_change_link = True


@admin.register(Creator)
class CreatorModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': ['name', 'genres']
            }
        ),
        (
            'Information', {
                'fields': ['description', 'users']
            }
        ),
        (
            'Art', {
                'fields': ['avi', 'cover']
            }
        )
    ]
    inlines = (CreatorSectionInline,)
    list_display = ['name']
    list_filter = ['genres']
    readonly_fields = ['users']


@admin.register(Genre)
class GenreModelAdmin(admin.ModelAdmin):
    list_display = ['title']


class SongInline(admin.TabularInline):
    model = Song
    fields = ['track_no', 'title', 'genre', 'explicit']
    extra = 1
    show_change_link = True
    ordering = ('track_no',)


class DiscInline(admin.TabularInline):
    model = Disc
    show_change_link = True
    extra = 1


@admin.register(Album)
class AlbumModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_of_release', 'album_type', 'genre', 'likes', 'published']
    readonly_fields = ['other_versions', 'likes']
    search_fields = ['title', 'artists__name']
    list_filter = ['genre', 'is_single', 'is_ep', 'date_of_release', 'published']
    inlines = (DiscInline,)
    actions = ['publish_albums', 'un_publish_albums']
    fieldsets = [
        (
            None, {
                'fields': ['title', 'date_of_release', 'is_single', 'is_ep', 'published']
            }
        ),
        (
            'Relations', {
                'fields': ['artists', 'genre', 'other_versions']
            }
        ),
        (
            'Information and Art', {
                'fields': ['notes', 'cover', 'likes']
            }
        )
    ]

    def get_readonly_fields(self, request, obj=None):
        r_fields: List = super().get_readonly_fields(request, obj)

        if request.user.is_superuser and request.GET.get('v'):
            if request.GET.get('v') == '1':
                r_fields = [f for f in r_fields if f != 'other_versions']

        return r_fields

    @staticmethod
    def pluralize(upd):
        al = 'album' if upd == 1 else 'albums'
        return f'{upd} {al}'

    def publish_albums(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{self.pluralize(updated)} published")

    def un_publish_albums(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{self.pluralize(updated)} un published", level=messages.WARNING)


@admin.register(Disc)
class DiscModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'album']
    inlines = (SongInline,)


@admin.register(Song)
class SongModelAdmin(admin.ModelAdmin):
    list_display = ['track_no', 'title', 'disc', 'length_string', 'likes', 'streams']
    readonly_fields = ['additional_artists', 'likes', 'streams']
    search_fields = ['title', 'disc__album__title', 'disc__album__artists__name', 'additional_artists__name']
    fieldsets = [
        (
            None, {
                'fields': ['track_no', 'title', 'disc']
            }
        ),
        (
            'Relations', {
                'fields': ['genre', 'additional_artists']
            }
        ),
        (
            'File', {
                'fields': ['file', 'length', 'explicit']
            }
        ),
        (
            'Information', {
                'fields': ['likes', 'streams']
            }
        )
    ]

    def get_readonly_fields(self, request, obj=None):
        r_fields: List = super().get_readonly_fields(request, obj)

        if 'change' in request.path.split('/') and 'disc' not in r_fields:
            r_fields.append('disc')

        for g, field in [['aa', 'additional_artists'], ['ds', 'disc']]:
            if request.user.is_superuser and request.GET.get(g):
                if request.GET.get(g) == '1':
                    r_fields = [f for f in r_fields if f != field]
        return r_fields


@admin.register(Playlist)
class PlaylistModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'likes']
    readonly_fields = ['creator', 'profile', 'songs', 'songs_order', 'likes', 'created']
    actions = ['order_songs_og']
    fieldsets = [
        (
            None, {
                'fields': ['title', 'creator', 'profile', 'created']
            }
        ),
        (
            'Information', {
                'fields': ['description', 'likes', 'songs', 'songs_order'],
            }
        ),
        (
            'Art', {
                'fields': ['cover', 'cover_wide', 'timely_cover', 'timely_cover_wide']
            }
        )
    ]

    def order_songs_og(self, request, queryset: List[Playlist]):
        m = 'Only superusers can OG playlists'
        if request.user.is_superuser:
            m = 'OG order achieved'
            for playlist in queryset:
                playlist.og_order()
        self.message_user(request, message=m)

    def get_readonly_fields(self, request, obj=None):
        r_fields: List = super().get_readonly_fields(request, obj)

        for g, field in [['s', 'songs'], ['c', 'creator'], ['p', 'profile'], ['so', 'songs_order']]:
            if request.user.is_superuser and request.GET.get(g):
                if request.GET.get(g) == '1':
                    r_fields = [f for f in r_fields if f != field]

        if 'add' in request.path.split('/'):
            r_fields = ['likes', 'created']

        return r_fields


@admin.register(LibraryAlbum)
class LibraryAlbumModelAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse('admin:music_libraryalbum_change', kwargs={'object_id': obj.pk}))

    def get_readonly_fields(self, request, obj=None):
        r_fields = list(super().get_readonly_fields(request, obj))
        if 'add' in request.path.split('/') and 'songs' not in r_fields:
            r_fields.append('songs')
        return tuple(r_fields)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'songs' and 'change' in request.path.split('/'):
            library_album_ids = findall(r'libraryalbum/(\d+)/change', request.path)
            if len(library_album_ids) > 0:
                library_album_id = int(library_album_ids[0])
                library_album: LibraryAlbum = get_object_or_404(LibraryAlbum, pk=library_album_id)
                kwargs['queryset'] = Song.objects.filter(
                    disc__pk__in=[disc.pk for disc in library_album.album.disc_set.all()]
                )

        return super().formfield_for_manytomany(db_field, request, **kwargs)
