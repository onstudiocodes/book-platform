from rest_framework import serializers
from .models import News, NewsImage

class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['image']

class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    dislikes_count = serializers.IntegerField(source='dislikes.count', read_only=True)
    views_count = serializers.IntegerField(source='views', read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'description', 'content', 'author_name', 'category', 'published_date', 'updated_date', 'images', 'likes_count', 'dislikes_count', 'views_count']
