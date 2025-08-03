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


