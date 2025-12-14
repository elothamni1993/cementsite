from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            "home",
            "blog_list",
            "premium_list",
            "pricing",
        ]

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("article_detail", kwargs={"slug": obj.slug})
