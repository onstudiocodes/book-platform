from rest_framework import serializers
from main.models import News, NewsImage
from main.serializers import AuthorSerializer


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage   
        fields = ['image']

class NewsSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    views_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    category = serializers.StringRelatedField()
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'description', 'content', 'author_name', 'category', 'published_date', 'updated_date', 'images', 'views_count', 'is_liked', 'likes_count', 'dislikes_count', 'comments_count']


    def get_views_count(self, obj):
        return obj.views  # Direct field, no need for `.count()`
    
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
