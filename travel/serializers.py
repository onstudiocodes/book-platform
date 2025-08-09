from main.models import TravelImage, TravelCategory, TravelStory
from rest_framework import serializers
from main.serializers import AuthorSerializer
from django.utils.html import strip_tags 
from main.utils import time_since_custom


class TravelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelImage

class TravelStorySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    desc = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    class Meta:
        model = TravelStory
        fields = ['author', 'title','slug', 'desc', 'tags', 'time_since', 'thumbnail']
    def get_desc(self, obj):
        return strip_tags(obj.story)[:100]
    def get_time_since(self, obj):
        return time_since_custom(obj.created_at)