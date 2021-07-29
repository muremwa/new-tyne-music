from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import reverse
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from .forms import CoreUserCreationForm, CoreUserEditForm, ProfileCreateForm
from .serializers import UserSerializer, ProfileSerializer
from .models import User
from tyne_utils.funcs import is_string_true_or_false


EDIT_USER = 'edit'
CREATE_USER = 'create'
GET_USER = 'get'


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def account_action(request, action):
    """
        Account actions
        1. GET_USER user \n
            - url -> /core/accounts/get?username=username
            - Fetches the user with the username 'username's details
            - If you're authenticated provides details about profiles

        2. CREATE_USER \n
            -url -> /core/accounts/create/
            - Creates a new user and returns their details
            - Requires {
                            'username': 'STRING',
                            'email': 'EMAIL',
                            'password': 'STRING',
                            'password_2': 'STRING'
                        }

        2. EDIT_USER \n
            -url -> /core/accounts/create/
            - Creates a new user and returns their details
            - Requires {
                            'username': 'STRING',
                            'email': 'EMAIL',
                        } -> ANY or BOTH of the two.
    """
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
                    data_ = UserSerializer(users[0]).data

                    if not request.user.is_authenticated:
                        data_.pop('profiles')

                    resp_status = status.HTTP_200_OK
                    response.update({
                        'user': data_
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
                if request.user.is_authenticated:
                    _post_req = {
                        'success': False
                    }
                    resp_status = status.HTTP_400_BAD_REQUEST
                    data = {
                        'username': request.POST.get('username'),
                        'email': request.POST.get('email')
                    }
                    data = {key: data[key] for key in data if data[key]}

                    if data.keys():
                        form = CoreUserEditForm(data=data, user=request.user)

                        if form.is_valid():
                            form.save()
                            _post_req.update({
                                'edited': data,
                                'success': True
                            })
                            resp_status = status.HTTP_200_OK

                        else:
                            _post_req.update({'errors': form.errors})

                    response.update(_post_req)

                else:
                    response.update({
                        'success': False,
                        'error': 'user is not authenticated'
                    })
                    resp_status = status.HTTP_401_UNAUTHORIZED

    return Response(response, status=resp_status)


@api_view(['GET', 'POST'])
@permission_classes([])
def login(request):
    """
        LOGIN_URL -> /core/login/
        Username or email and password
        returns user details including token
    """
    response = {
        'url': 'user authentication'
    }
    resp_status = status.HTTP_200_OK

    if request.method == 'GET':
        response.update({
            'fields': ['username', 'email', 'password'],
            'returns': ['token', 'user_data']
        })

    elif request.method == 'POST':
        _post_resp = {
            'success': False,
            'error': 'Wrong Credentials'
        }
        resp_status = status.HTTP_400_BAD_REQUEST
        authenticated_user = None

        if request.POST.get('password'):
            if request.POST.get('email'):
                try:
                    _user = User.objects.get(email=request.POST.get('email'))
                    authenticated_user = authenticate(username=_user.username, password=request.POST.get('password'))
                except ObjectDoesNotExist:
                    pass

            elif request.POST.get('username'):
                authenticated_user = authenticate(
                    username=request.POST.get('username'),
                    password=request.POST.get('password')
                )

        if authenticated_user:
            _post_resp.pop('error')
            _post_resp.update({
                'success': True,
                'token': authenticated_user.get_user_auth_token().key,
                'details': UserSerializer(authenticated_user).data
            })
            resp_status = status.HTTP_200_OK

        response.update(_post_resp)

    return Response(response, status=resp_status)


@api_view(['GET', 'POST'])
def profile_create(request):
    """
        Create a new user profile for the authenticated user-> core/profile/create/
        ['profile_name', 'is_minor', 'profile_image']
    """
    response = {
        'url action': 'Create profiles'
    }
    response_status = status.HTTP_200_OK

    if request.method == 'GET':
        fields = ProfileCreateForm().fields_info()
        fields.pop('account')
        response.update({
            'fields': fields
        })

    elif request.method == 'POST':
        response['success'] = False
        response_status = status.HTTP_202_ACCEPTED
        _is_minor = request.POST.get('is_minor')
        data_ = {
            'profile_name': request.POST.get('profile_name'),
            'profile_image': request.FILES.get('profile_image'),
            'is_minor': is_string_true_or_false(_is_minor) if _is_minor is not None else _is_minor,
            'account': request.user.pk
        }
        data_ = {key: data_[key] for key in data_ if data_[key] is not None}
        form = ProfileCreateForm(data=data_)

        if form.is_valid():
            new_profile = form.save()
            response.update({
                'success': True,
                'profile': ProfileSerializer(new_profile).data
            })
            response_status = status.HTTP_201_CREATED
        else:
            response['errors'] = form.errors

    return Response(response, status=response_status)
