from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch, Count
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Follow
from .serializers import (
    PostSerializer, PostCreateSerializer, FeedPostSerializer,
    CommentSerializer, FollowSerializer, SearchSerializer, UserBasicSerializer
)
from users.serializers import UserSearchSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts
    """
    queryset = Post.objects.filter(is_active=True).select_related(
        'user', 'user__profile'
    ).prefetch_related(
        'likes', 
        Prefetch('comments', queryset=Comment.objects.filter(is_active=True).select_related('user'))
    ).annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', filter=Q(comments__is_active=True), distinct=True)
    )
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['caption', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'list':
            return FeedPostSerializer
        return PostSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        user = request.user
        
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
            message = 'Post unliked successfully'
        else:
            post.likes.add(user)
            liked = True
            message = 'Post liked successfully'
        
        return Response({
            'liked': liked,
            'total_likes': post.total_likes(),
            'message': message
        })
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get comments for a post"""
        post = self.get_object()
        comments = post.comments.filter(is_active=True).select_related('user').order_by('created_at')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(comments, request)
        
        serializer = CommentSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_comment(self, request, pk=None):
        """Add a comment to a post"""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedView(generics.ListAPIView):
    """
    API view for user's personalized feed
    """
    serializer_class = FeedPostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        following_users = user.following.values_list('following', flat=True)
        
        # Get posts from followed users and own posts
        followed_posts = Post.objects.filter(
            Q(user__in=following_users) | Q(user=user),
            is_active=True
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes'
        ).annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', filter=Q(comments__is_active=True), distinct=True)
        ).order_by('-created_at')
        
        return followed_posts


class ExploreView(generics.ListAPIView):
    """
    API view for exploring posts from all users
    """
    serializer_class = FeedPostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Post.objects.filter(
            is_active=True
        ).select_related(
            'user', 'user__profile'
        ).annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', filter=Q(comments__is_active=True), distinct=True)
        ).order_by('-total_likes', '-created_at')


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(
            is_active=True
        ).select_related('user', 'post')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Only allow deletion of own comments
        if instance.user != self.request.user:
            return Response(
                {'error': 'You can only delete your own comments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        instance.is_active = False
        instance.save()


class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing follow relationships
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user
        ).select_related('following', 'following__profile')
    
    def create(self, request, *args, **kwargs):
        """Follow a user"""
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
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
            serializer = self.get_serializer(follow_obj)
            return Response(
                {
                    'message': f'Successfully followed {user_to_follow.username}',
                    'follow': serializer.data
                }, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': f'You are already following {user_to_follow.username}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['delete'])
    def unfollow(self, request):
        """Unfollow a user"""
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_unfollow = User.objects.get(username=username)
            follow_obj = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow_obj.delete()
            return Response(
                {'message': f'Successfully unfollowed {user_to_unfollow.username}'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Follow.DoesNotExist:
            return Response(
                {'error': f'You are not following {username}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class SearchAPIView(generics.GenericAPIView):
    """
    API view for searching users and posts
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'users': [],
                'posts': [],
                'query': '',
                'total_results': 0
            })
        
        # Search users
        users_queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile')[:10]
        
        # Search posts
        posts_queryset = Post.objects.filter(
            Q(caption__icontains=query),
            is_active=True
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related('likes', 'comments').annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', filter=Q(comments__is_active=True), distinct=True)
        ).order_by('-created_at')[:10]
        
        # Serialize results
        users_serializer = UserSearchSerializer(
            users_queryset, 
            many=True, 
            context={'request': request}
        )
        posts_serializer = PostSerializer(
            posts_queryset, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'users': users_serializer.data,
            'posts': posts_serializer.data,
            'query': query,
            'total_results': len(users_serializer.data) + len(posts_serializer.data)
        })


class UserPostsView(generics.ListAPIView):
    """
    API view for getting posts by a specific user
    """
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        
        return Post.objects.filter(
            user=user,
            is_active=True
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related('likes', 'comments').annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', filter=Q(comments__is_active=True), distinct=True)
        ).order_by('-created_at')