from django.urls import path

from . import views

app_name = 'core'


urlpatterns = [
    # accounts/create/ or accounts/edit/ or accounts/get/?username=user
    path('accounts/<str:action>/', views.account_action, name='account-action'),

    # login/
    path('login/', views.login, name='login'),
]
