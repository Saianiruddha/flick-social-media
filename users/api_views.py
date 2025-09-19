from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import UserProfile
from posts.models import Follow
from .serializers import (
    UserRegistrationSerializer, UserDetailSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserSearchSerializer,
    FollowersListSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Create user profile
        UserProfile.objects.create(user=user)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that returns user info along with tokens
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.select_related('profile').get(username=username)
                user_data = UserDetailSerializer(user, context={'request': request}).data
                response.data['user'] = user_data
            except User.DoesNotExist:
                pass
        
        return response


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        return User.objects.select_related('profile').all()
    
    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def update(self, request, *args, **kwargs):
        """Update user profile"""
        user = self.get_object()
        
        # Only allow users to update their own profile
        if user != request.user:
            return Response(
                {'error': 'You can only update your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's profile"""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def followers(self, request, username=None):
        """Get user's followers"""
        user = self.get_object()
        followers = Follow.objects.filter(
            following=user
        ).select_related('follower', 'follower__profile')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(followers, request)
        
        serializer = FollowersListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        """Get users that this user is following"""
        user = self.get_object()
        following = Follow.objects.filter(
            follower=user
        ).select_related('following', 'following__profile')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(following, request)
        
        serializer = FollowersListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, username=None):
        """Follow a user"""
        user_to_follow = self.get_object()
        
        if request.user == user_to_follow:
            return Response(
                {'error': 'You cannot follow yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            return Response({
                'message': f'Successfully followed {user_to_follow.username}',
                'is_following': True,
                'followers_count': user_to_follow.followers.count()
            })
        else:
            return Response(
                {'error': f'You are already following {user_to_follow.username}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def unfollow(self, request, username=None):
        """Unfollow a user"""
        user_to_unfollow = self.get_object()
        
        try:
            follow_obj = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow_obj.delete()
            return Response({
                'message': f'Successfully unfollowed {user_to_unfollow.username}',
                'is_following': False,
                'followers_count': user_to_unfollow.followers.count()
            })
        except Follow.DoesNotExist:
            return Response(
                {'error': f'You are not following {user_to_unfollow.username}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserSearchView(generics.ListAPIView):
    """
    API view for searching users
    """
    serializer_class = UserSearchSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if not query:
            return User.objects.none()
        
        return User.objects.filter(
            username__icontains=query
        ).select_related('profile').order_by('username')


class SuggestedUsersView(generics.ListAPIView):
    """
    API view for getting suggested users to follow
    """
    serializer_class = UserSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        following_users = user.following.values_list('following', flat=True)
        
        # Get users that current user is not following
        # Prioritize users with more followers
        suggested_users = User.objects.exclude(
            id__in=list(following_users) + [user.id]
        ).select_related('profile').order_by('-followers__count')[:20]
        
        return suggested_users


class UserStatsView(generics.GenericAPIView):
    """
    API view for getting user statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user
        
        stats = {
            'posts_count': user.posts.filter(is_active=True).count(),
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'total_likes_received': sum(
                post.total_likes() for post in user.posts.filter(is_active=True)
            ),
            'total_comments_received': sum(
                post.comments.filter(is_active=True).count() 
                for post in user.posts.filter(is_active=True)
            )
        }
        
        return Response(stats)