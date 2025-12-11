from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # all site routes live in the app
]

# CKEditor uploads (only if installed)
if "ckeditor_uploader" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("ckeditor/", include("ckeditor_uploader.urls")),
    ]

# Serve media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
