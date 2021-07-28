from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import reverse

from .forms import CoreUserCreationForm, CoreUserEditForm
from .serializers import UserSerializer
from .models import User


EDIT_USER = 'edit'
CREATE_USER = 'create'
GET_USER = 'get'


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def account_action(request, action):
    response = {
        'url': 'account action'
    }
    resp_status = status.HTTP_202_ACCEPTED

    if action not in [EDIT_USER, CREATE_USER, GET_USER]:
        response.update({
            '404 Error': f'{action} not supported',
            'urls_supported': [
                reverse('core:account-action', kwargs={'action': CREATE_USER}),
                reverse('core:account-action', kwargs={'action': EDIT_USER}),
                "{}?username=user".format(reverse('core:account-action', kwargs={'action': GET_USER}))
            ]
        })
        resp_status = status.HTTP_404_NOT_FOUND

    else:
        if request.method == 'GET':
            if action == GET_USER:
                response.update({
                    'action': 'Retrieve user'
                })
                username = request.GET.get('username', '')
                users = User.objects.filter(username=username)

                if users.count() < 1:
                    resp_status = status.HTTP_404_NOT_FOUND
                    response.update({
                        'user': f'User \'{username}\' not found'
                    })

                else:
                    resp_status = status.HTTP_200_OK
                    response.update({
                        'user': UserSerializer(users[0]).data
                    })

            else:
                form = CoreUserCreationForm() if action == CREATE_USER else CoreUserEditForm(user=None)
                response.update({
                    'action': 'Create a new user' if action == CREATE_USER else 'Edit an existing user',
                    'login_required': True if action == EDIT_USER else False,
                    'fields': form.fields_info()
                })

        elif request.method == 'POST':
            # create a user
            if action == CREATE_USER:
                form = CoreUserCreationForm(data=request.POST)

                if form.is_valid():
                    user_data = form.save()
                    response.update({
                        'success': True,
                        'new_user': UserSerializer(user_data.get('new_user', {})).data,
                        'user_token': user_data.get('token_key')
                    })
                    resp_status = status.HTTP_201_CREATED

                else:
                    response.update({
                        'success': False,
                        'errors': form.errors
                    })

                response.update({
                    'action': 'Create user'
                })

            elif action == EDIT_USER:
                response.update({
                    'message': 'Coming soon'
                })

    return Response(response, status=resp_status)
