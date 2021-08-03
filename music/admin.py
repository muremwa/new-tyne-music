from typing import List

from django.contrib import admin

from .models import Artist, Creator, Genre, Album, Song


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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and not obj.is_group:
            fieldsets = [field_set for field_set in fieldsets if field_set[0] != self.GRP_INFO_NAME]
        return fieldsets


@admin.register(Creator)
class CreatorModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': ['name']
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
    list_display = ['name']
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


@admin.register(Album)
class AlbumModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_of_release', 'album_type', 'genre', 'likes']
    readonly_fields = ['other_versions', 'likes']
    inlines = (SongInline,)
    fieldsets = [
        (
            None, {
                'fields': ['title', 'date_of_release', 'is_single', 'is_ep']
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


@admin.register(Song)
class SongModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'length_string', 'likes', 'streams']
    readonly_fields = ['additional_artists', 'likes', 'streams']
    fieldsets = [
        (
            None, {
                'fields': ['track_no', 'title', 'album']
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

        if 'change' in request.path.split('/') and 'album' not in r_fields:
            r_fields.append('album')

        for g, field in [['aa', 'additional_artists'], ['al', 'album']]:
            if request.user.is_superuser and request.GET.get(g):
                if request.GET.get(g) == '1':
                    r_fields = [f for f in r_fields if f != field]
        return r_fields
