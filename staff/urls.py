from django.urls import path

from . import views


app_name = 'staff'

urlpatterns = [
    # /
    path('', views.StaffHome.as_view(), name='home'),

    # /add_user_to_staff/
    path('add_user_to_staff/', views.AddAdminUsers.as_view(), name='add-users'),
]