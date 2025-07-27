from rest_framework import serializers
from .models import News, NewsImage
from accounts.models import User, UserProfile, UserFollow

class FollowerSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField()
    class Meta:
        model = UserFollow
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    is_following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'userprofile', 'is_following', 'followers']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers_users.filter(follower=request.user).exists()
        return False
    def get_followers(self, obj):
        return obj.followers_users.count()


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage   
        fields = ['image']

class NewsSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    category = serializers.StringRelatedField()

    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'description', 'content', 'author_name', 'category', 'published_date', 'updated_date', 'images', 'likes_count', 'dislikes_count', 'views_count', 'comments_count', 'is_liked']

    def get_likes_count(self, obj):
        return getattr(obj, 'likes_count', 0)

    def get_dislikes_count(self, obj):
        return getattr(obj, 'dislikes_count', 0)

    def get_views_count(self, obj):
        return obj.views  # Direct field, no need for `.count()`
    
    def get_comments_count(self, obj):
        return getattr(obj, 'comments_count', 0)
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
