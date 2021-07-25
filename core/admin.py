from django.contrib import admin

from .models import User, Profile


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
    search_fields = ('name',)
    list_display = ('name', 'main', 'email', 'tier')
