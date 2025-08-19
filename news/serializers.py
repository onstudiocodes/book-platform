from rest_framework import serializers
from main.models import News, NewsImage, NewsCategory
from main.serializers import AuthorSerializer
from main.utils import time_since_custom

class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'slug']

class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage   
        fields = ['id', 'image']

class NewsSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    views_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    category = NewsCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsCategory.objects.all(), 
        source='category', 
        write_only=True,
        required=False
    )
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'description', 'content', 'author_name', 'category', 'category_id', 'published_date', 'updated_date', 'images', 'thumbnail', 'views_count', 'is_liked', 'likes_count', 'dislikes_count', 'comments_count', 'time_since_created']

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return self.context['request'].build_absolute_uri(first_image.image.url) if self.context.get('request') else first_image.image.url
        return None

    def get_likes_count(self, obj):
        # Try to get annotated value first, fallback to counting
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.likes.count()
    
    def get_dislikes_count(self, obj):
        # Try to get annotated value first, fallback to counting
        if hasattr(obj, 'dislikes_count'):
            return obj.dislikes_count
        return obj.dislikes.count()
    
    def get_comments_count(self, obj):
        # Try to get annotated value first, fallback to counting
        if hasattr(obj, 'comments_count'):
            return obj.comments_count
        return obj.comments.count()
    
    def get_views_count(self, obj):
        # Try to get annotated value first, fallback to counting
        if hasattr(obj, 'views_count'):
            return obj.views_count
        return obj.news_views.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_time_since_created(self, obj):
        return time_since_custom(obj.published_date)
