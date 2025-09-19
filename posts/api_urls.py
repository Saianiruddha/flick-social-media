from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PostViewSet, FeedView, ExploreView, CommentViewSet,
    FollowViewSet, SearchAPIView, UserPostsView
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    # Feed and explore
    path('feed/', FeedView.as_view(), name='api-feed'),
    path('explore/', ExploreView.as_view(), name='api-explore'),
    
    # Search
    path('search/', SearchAPIView.as_view(), name='api-search'),
    
    # User posts
    path('user/<str:username>/', UserPostsView.as_view(), name='api-user-posts'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]