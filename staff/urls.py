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

    # staff-groups/
    path('staff-groups/', views.GroupInfoView.as_view(), name='staff-groups'),

    # help/
    path('help/', views.StaffHelpList.as_view(), name='help-list'),

    # help/article/how-to-use-staff-page/
    path('help/article/<int:article_pk>/', views.StaffHelpArticlePage.as_view(), name='help-article'),

    # help/manage/
    path('help/manage/', views.StaffArticleAdd.as_view(), name='help-add'),

    # help/manage/edit/43/
    path('help/manage/edit/<int:article_pk>/', views.StaffArticleEdit.as_view(), name='help-edit'),

    # help/manage/delete/43/
    path('help/manage/delete/<int:article_pk>/', views.StaffArticleHelpDelete.as_view(), name='help-delete'),

    # logs/
    path('staff-activity/', views.StaffLogs.as_view(), name='logs'),

    # search-artists/
    path('search-artists/', views.artists_names, name='search-artists'),

    # manage-albums/
    path('manage-albums/', views.StaffAlbumView.as_view(), name='manage-albums'),

    # manage-albums/published-status/23/
    path('manage-albums/published-status/<int:album_pk>/', views.PublishAlbums.as_view(), name='album-publish-status'),

    # manage-albums/edit/23/
    path('manage-albums/edit/<int:album_pk>/', views.AlbumEditView.as_view(), name='album-edit'),

    # manage-albums/create/
    path('manage-albums/create/', views.StaffAlbumCreateView.as_view(), name='album-create'),

]
