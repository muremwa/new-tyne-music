from django.urls import path

from . import views

app_name = 'core'


urlpatterns = [
    path('accounts/<str:action>/', views.account_action, name='account-action'),
]
