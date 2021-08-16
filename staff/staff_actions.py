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
    }
]
