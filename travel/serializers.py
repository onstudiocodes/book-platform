from main.models import TravelImage, TravelCategory, TravelStory
from rest_framework import serializers
from main.serializers import AuthorSerializer
from django.utils.html import strip_tags 
from main.utils import time_since_custom


class TravelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelImage
        fields = ['id', 'image']

class TravelStorySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    desc = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    images = TravelImageSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    
    class Meta:
        model = TravelStory
        fields = ['id', 'author', 'title', 'slug', 'story', 'desc', 'category', 'location', 'latitude', 'longitude', 'duration', 'season', 'budget_level', 'published', 'created_at', 'tags', 'time_since', 'thumbnail', 'images', 'likes_count', 'dislikes_count', 'is_liked', 'is_disliked']
        
    def get_desc(self, obj):
        return strip_tags(obj.story)[:100]
    
    def get_time_since(self, obj):
        return time_since_custom(obj.created_at)
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_is_disliked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.dislikes.filter(id=request.user.id).exists()
        return False