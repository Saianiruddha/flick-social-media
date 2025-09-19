"""
URL configuration for INSTACLONE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from posts.views import home_view
import posts.views as post_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('feed/', post_views.feed_view, name='feed'),
    path('profile/', include('users.urls')),  # all profile/edit/<username> URLs
    path('posts/', include('posts.urls')),    # posts actions
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/',LogoutView.as_view(next_page='home'),name='logout'),
    
    # API endpoints
    path('api/users/', include('users.api_urls')),
    path('api/posts/', include('posts.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
