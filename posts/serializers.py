from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Follow
from users.models import UserProfile


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested use"""
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']
    
    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url)
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = UserBasicSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    user = UserBasicSerializer(read_only=True)
    total_likes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'image', 'caption', 'created_at', 'updated_at',
            'total_likes', 'total_comments', 'is_liked', 'comments', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_total_likes(self, obj):
        return obj.total_likes()
    
    def get_total_comments(self, obj):
        return obj.comments.filter(is_active=True).count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating posts"""
    
    class Meta:
        model = Post
        fields = ['image', 'caption']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at', 'follower']
    
    def create(self, validated_data):
        validated_data['follower'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        request = self.context['request']
        following_user = data.get('following')
        
        if request.user == following_user:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        if Follow.objects.filter(follower=request.user, following=following_user).exists():
            raise serializers.ValidationError("You are already following this user.")
        
        return data


class FeedPostSerializer(serializers.ModelSerializer):
    """Optimized serializer for feed posts"""
    user = UserBasicSerializer(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    recent_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'image', 'caption', 'created_at',
            'total_likes', 'total_comments', 'is_liked', 'recent_comments'
        ]
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False
    
    def get_recent_comments(self, obj):
        recent_comments = obj.comments.filter(is_active=True).order_by('-created_at')[:3]
        return CommentSerializer(recent_comments, many=True, context=self.context).data


class SearchSerializer(serializers.Serializer):
    """Serializer for search results"""
    users = UserBasicSerializer(many=True, read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    query = serializers.CharField(read_only=True)
    total_results = serializers.IntegerField(read_only=True)