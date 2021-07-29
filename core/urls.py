from django.urls import path

from . import views

app_name = 'core'


urlpatterns = [
    # accounts/create/ or accounts/edit/ or accounts/get/?username=user
    path('accounts/<str:action>/', views.account_action, name='account-action'),

    # login/
    path('login/', views.login, name='login'),

    # profile/create/
    path('profile/create/', views.profile_create, name='profile-create'),

    # profile/edit/1/
    path('profile/edit/<int:profile_pk>/', views.profile_edit, name='profile-edit'),
]
