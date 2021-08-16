from django.urls import path

from . import views


app_name = 'staff'

urlpatterns = [
    # /
    path('', views.StaffHome.as_view(), name='home'),

    # /add_user_to_staff/
    path('manage-staff-user/', views.AddAdminUsers.as_view(), name='add-users'),

    # staff-roles/
    path('staff-roles/', views.StaffRolesView.as_view(), name='staff-view'),

    # help/
    path('help/', views.StaffHelpList.as_view(), name='help-list'),

    # help/article/how-to-use-staff-page/
    path('help/article/<slug:article_slug>/', views.StaffHelpArticlePage.as_view(), name='help-article'),

    # help/manage/
    path('help/manage/', views.StaffArticleAdd.as_view(), name='help-add'),

    # help/manage/edit/43/
    path('help/manage/edit/<int:article_pk>/', views.StaffArticleEdit.as_view(), name='help-edit'),

    # help/manage/delete/43/
    path('help/manage/delete/<int:article_pk>/', views.StaffArticleHelpDelete.as_view(), name='help-delete'),

]
