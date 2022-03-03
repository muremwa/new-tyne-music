from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

from core.views import master_login, master_logout, TempHomePage, master_signup

docs_description = """
    This are the API end points available on tyne music
"""

urlpatterns = [
    # /
    path('', TempHomePage.as_view(), name='home'),

    # admin/
    path('admin/', admin.site.urls),

    # core/
    path('core/', include('core.urls')),

    # music/
    path('music/', include('music.urls')),

    # staff/
    path('staff/', include('staff.urls')),

    # login/
    path('login/', master_login, name='master-login'),

    # logout/
    path('logout/', master_logout, name='master-logout'),

    # signup/
    path('signup/', master_signup, name='master-signup'),

    # docs/
    path('docs/', include_docs_urls(title='Tyne Music API docs', description=docs_description))
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
