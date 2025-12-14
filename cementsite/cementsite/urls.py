from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from core.sitemaps import StaticViewSitemap, ArticleSitemap
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": {"static": StaticViewSitemap, "articles": ArticleSitemap}}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
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
