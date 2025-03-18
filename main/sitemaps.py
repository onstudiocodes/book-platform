from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Book

class StaticViewSiteMap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'
    def items(self):
        return ['main:index', 'main:trending', 'main:recent', 'main:popular']
    def location(self, obj):
        return reverse(obj)

class BookSiteMap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    def items(self):
        return Book.objects.all()
    def lastmod(self, obj):
        return obj.updated_date