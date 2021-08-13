from django.urls import path

from . import views


app_name = 'staff'

urlpatterns = [
    # /
    path('', views.StaffHome.as_view(), name='home'),

    # /add_user_to_staff/
    path('add_user_to_staff/', views.AddAdminUsers.as_view(), name='add-users'),

    # help/
    path('help/', views.StaffHelpList.as_view(), name='help-list'),

    # help/how-to-use-staff-page/
    path('help/<slug:article_slug>/', views.StaffHelpArticlePage.as_view(), name='help-article'),
]