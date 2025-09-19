from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),           # signup page
    path('edit/', views.edit_profile, name='edit_profile'), # edit profile
    path('<str:username>/', views.profile_view, name='profile'), # user profiles
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"), # logout page
]
