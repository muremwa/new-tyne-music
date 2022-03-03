from django.urls import reverse_lazy


staff_actions = [
    {
        'name': 'Add Staff User',
        'id': 'add_staff',
        'url': reverse_lazy('staff:add-users'),
        'description': 'Add a user as staff, Curator moderator etc.',
        'permissions': [
            'auth.change_group', 'auth.view_group', 'auth.change_permission', 'auth.view_permission',
            'core.change_user', 'core.view_user'
        ]
    },
    {
        'name': 'Add Help Article',
        'id': 'create_help_article',
        'url': reverse_lazy("staff:help-add"),
        'description': 'Add help articles for all of tyne music.',
        'permissions': [
            'staff.add_helparticle',
        ]
    },
    {
        'name': 'List staff members',
        'id': 'ls_staff',
        'url': reverse_lazy('staff:staff-view'),
        'description': 'Lists all staff members and you get to view their permissions and groups',
        'permissions': [
            'core.view_user', 'auth.view_group', 'auth.view_permission'
        ]
    },
    {
        'name': 'Manage Albums',
        'id': 'manage_albums',
        'url': reverse_lazy('staff:manage-albums'),
        'description': 'Add, view, edit, publish or delete albums',
        'permissions': [
            'music.add_album', 'music.view_album', 'music.change_album', 'music.delete_album'
        ]
    },
    {
        'name': 'New Album',
        'id': 'create_album',
        'url': reverse_lazy('staff:album-create'),
        'description': 'Add a new album',
        'permissions': [
            'music.add_album', 'music.view_album',
        ]
    },
    {
        'name': 'Manage Artists',
        'id': 'manage_artists',
        'url': reverse_lazy('staff:manage-artists'),
        'description': 'Add, view, edit or delete artists',
        'permissions': [
            'music.add_artist', 'music.view_artist', 'music.change_artist', 'music.delete_artist'
        ]
    },
    {
        'name': 'New Artist',
        'id': 'create_artist',
        'url': reverse_lazy('staff:artist-create'),
        'description': 'Add a new artist',
        'permissions': [
            'music.add_artist', 'music.view_artist'
        ]
    },
    {
        'name': 'View all groups',
        'id': 'view_all_groups',
        'url': reverse_lazy("staff:staff-groups"),
        'description': 'View all groups, their members, and permission allocated',
        'permissions': [
            'auth.change_group', 'core.change_user'
        ]
    },
    {
        'name': 'View creators',
        'id': 'view_all_creators',
        'url': reverse_lazy("staff:manage-creators"),
        'description': 'View all creators and their curators',
        'permissions': ['music.view_creator']
    }
]

superuser_actions = [
    {
        'name': 'View staff activity',
        'id': 'view_staff_activity',
        'url': reverse_lazy("staff:logs"),
        'description': 'View records of activity by staff and who or what they affected',
    },
]
