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
    }
]
