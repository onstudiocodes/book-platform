from rest_framework import serializers
from .models import News, NewsImage, Comment
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
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'userprofile', 'is_following', 'followers', 'full_name']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers_users.filter(follower=request.user).exists()
        return False
    
    def get_followers(self, obj):
        return obj.followers_users.count()
    
    def get_full_name(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile:
            return obj.userprofile.full_name or obj.username
        return obj.username


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'book', 'news', 'travel_story', 'parent', 'created_at', 'updated_at', 'likes_count', 'dislikes_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.count()