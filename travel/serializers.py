from main.models import TravelImage, TravelCategory, TravelStory
from rest_framework import serializers
from main.serializers import AuthorSerializer
from django.utils.html import strip_tags 

class TravelStorySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    desc = serializers.SerializerMethodField()
    class Meta:
        model = TravelStory
        fields = ['author', 'title', 'desc']
    def get_desc(self, obj):
        return strip_tags(obj.story)[:100]