from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from .serializers import Library


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_library(request):
    profile_pk = request.GET.get('p')

    if profile_pk and profile_pk.isdigit() and request.user.tier == 'F':
        try:
            profile = request.user.profile_set.get(pk=int(profile_pk))
        except ObjectDoesNotExist:
            raise Http404

    else:
        profile = request.user.main_profile

    lib = Library(profile)

    return Response(lib.data)
