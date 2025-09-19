from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    UserRegistrationView, CustomTokenObtainPairView, UserProfileViewSet,
    UserSearchView, SuggestedUsersView, UserStatsView
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User search and suggestions
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('suggested/', SuggestedUsersView.as_view(), name='suggested-users'),
    
    # User statistics
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('stats/<str:username>/', UserStatsView.as_view(), name='user-stats-detail'),
    
    # Profile ViewSet URLs
    path('', include(router.urls)),
]