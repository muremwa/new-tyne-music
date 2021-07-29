from django.contrib import admin

from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    max_num = 6
    show_change_link = True
    readonly_fields = ['main']

    def get_max_num(self, request, obj=None, **kwargs):
        return 1 if obj.tier == 'S' else 6

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if not obj.profile_full:
            extra = 6 - obj.profile_count

        return extra


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': ['username', 'tier']
            }
        ),
        (
            'Personal Info', {
                'fields': ['first_name', 'last_name', 'email']
            }
        ),
        (
            'Permissions', {
                'fields': ['is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions']
            }
        ),
        (
            'Important Dates', {
                'fields': ['date_joined', 'last_login']
            }
        )
    ]
    list_display = ('username', 'email', 'tier', 'is_staff', 'profile_count', 'profile_full')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'tier')
    search_fields = ('username', 'email')
    inlines = (ProfileInline,)
    actions = None


@admin.register(Profile)
class ProfileModelAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            'User', {
                'fields': ['user', 'name', 'avi']
            }
        ),
        (
            'Additional Details', {
                'fields': ['main', 'minor']
            }
        )
    ]
    readonly_fields = ['main']
    search_fields = ('name',)
    list_display = ('name', 'main', 'email', 'tier')

    def has_delete_permission(self, request, obj=None):
        perm = True

        if hasattr(obj, 'main'):
            if obj.main:
                perm = False

        return perm
