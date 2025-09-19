from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile
from posts.models import Follow


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password and confirm password don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    profile_image = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'profile_image', 'birth_date', 'location', 'website',
            'is_private', 'email_notifications', 'posts_count',
            'followers_count', 'following_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'posts_count', 'followers_count', 'following_count']
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
        return None
    
    def get_posts_count(self, obj):
        return obj.get_posts_count()
    
    def get_followers_count(self, obj):
        return obj.get_followers_count()
    
    def get_following_count(self, obj):
        return obj.get_following_count()


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer including profile"""
    profile = UserProfileSerializer(read_only=True)
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active', 'profile', 'is_following', 'is_followed_by'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']
    
    def get_is_following(self, obj):
        """Check if current user is following this user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False
    
    def get_is_followed_by(self, obj):
        """Check if this user is following current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return Follow.objects.filter(follower=obj, following=request.user).exists()
        return False


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserSearchSerializer(serializers.ModelSerializer):
    """Simplified serializer for user search results"""
    profile_image = serializers.SerializerMethodField()
    bio = serializers.CharField(source='profile.bio', read_only=True)
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image', 'bio', 'followers_count', 'is_following']
    
    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url)
        return None
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class FollowersListSerializer(serializers.ModelSerializer):
    """Serializer for followers/following lists"""
    follower = UserSearchSerializer(read_only=True)
    following = UserSearchSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']