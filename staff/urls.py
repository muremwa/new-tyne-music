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

    # manage-albums/delete/23/
    path('manage-albums/delete/<int:album_pk>/', views.AlbumDelete.as_view(), name='album-delete'),

    # manage-albums/create/
    path('manage-albums/create/', views.StaffAlbumCreateView.as_view(), name='album-create'),

    # manage-albums/disc/new/23/
    path('manage-albums/disc/new/<int:album_id>/', views.add_disc_to_album, name='new-disc'),

    # manage-albums/disc/change/34/
    path('manage-albums/disc/change/<int:disc_id>/', views.change_disc_name, name='change-disc'),

    # manage-albums/disc/delete/34/
    path('manage-albums/disc/delete/<int:disc_id>/', views.delete_disc_from_album, name='delete-disc'),

    # manage-albums/disc/34/song/new/
    path('manage-albums/disc/<int:disc_id>/song/new/', views.CreateSongView.as_view(), name='new-song'),

    # manage-albums/song/14/edit/
    path('manage-albums/song/<int:song_id>/edit/', views.EditSongView.as_view(), name='edit-song'),

    # manage-albums/song/14/delete/
    path('manage-albums/song/<int:song_id>/delete/', views.DeleteSongView.as_view(), name='delete-song'),

    # manage-artists/
    path('manage-artists/', views.StaffArtistsView.as_view(), name='manage-artists'),

    # manage-artists/edit/49/members/
    path('manage-artists/edit/<int:artist_id>/members/', views.EditArtistGroupMember.as_view(), name='group-members'),

    # manage-artists/edit/49/
    path('manage-artists/edit/<int:artist_id>/', views.EditArtist.as_view(), name='artist-edit'),

    # manage-artists/create/
    path('manage-artists/create/', views.ArtistCreate.as_view(), name='artist-create'),

    # manage-artists/delete/23/
    path('manage-artists/delete/<int:artist_id>/', views.ArtistDelete.as_view(), name='artist-delete'),

]
