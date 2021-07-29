from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

docs_description = """
    This are the API end points available on tyne music
"""

urlpatterns = [
    path('admin/', admin.site.urls),

    # core/
    path('core/', include('core.urls')),

    # docs/
    path('docs/', include_docs_urls(title='Tyne Music API docs', description=docs_description))
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
