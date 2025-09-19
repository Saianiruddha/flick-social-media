from django.urls import path
from . import views

urlpatterns = [
    # Feed / Home
    path('', views.feed_view, name='feed'),  # default feed

    # Post actions
    path('create/', views.create_post, name='create_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),  # like/unlike
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('detail/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # Social features
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('search/', views.search_users, name='search'),
]
