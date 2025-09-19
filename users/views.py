from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.templatetags.static import static
from .models import UserProfile
from posts.models import Post
from .forms import ProfileForm, UserForm, SignUpForm


def profile_view(request, username):
    """Enhanced profile view with optimization and error handling"""
    try:
        # Get user with optimized query
        user = get_object_or_404(User.objects.select_related('profile'), username=username)
        
        # Get or create profile if it doesn't exist
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Get active posts with optimization
        posts = Post.objects.filter(
            user=user, 
            is_active=True
        ).select_related('user').prefetch_related('likes', 'comments').order_by('-created_at')
        
        # Safe image handling
        if profile.profile_image and profile.profile_image.name:
            image_url = profile.profile_image.url
        else:
            image_url = static("images/default-profile.png")
        
        # Additional profile stats
        context = {
            'profile': profile,
            'user_obj': user,  # Add user object for template
            'posts': posts,
            'profile_image_url': image_url,
            'posts_count': posts.count(),
            'followers_count': user.followers.count() if hasattr(user, 'followers') else 0,
            'following_count': user.following.count() if hasattr(user, 'following') else 0,
        }
        
        return render(request, 'users/profile.html', context)
        
    except Exception as e:
        messages.error(request, 'Profile not found or error loading profile.')
        return redirect('feed')

@login_required
def edit_profile(request):
    """Enhanced profile editing with better error handling"""
    user = request.user
    # Get or create the profile for the logged-in user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Bind forms with POST data and files
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=user)

        if profile_form.is_valid() and user_form.is_valid():
            try:
                # Save both user and profile changes
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                # Redirect to the profile page using URL name
                return redirect('profile', username=user.username)
            except Exception as e:
                messages.error(request, 'Error updating profile. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileForm(instance=profile)
        user_form = UserForm(instance=user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form
    }
    return render(request, 'users/edit_profile.html', context)




def signup(request):
    """Enhanced signup with better error handling"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create a linked UserProfile
                UserProfile.objects.create(user=user)
                # Log them in immediately
                login(request, user)
                messages.success(request, f'Welcome to InstaClone, {user.username}!')
                return redirect('feed')
            except Exception as e:
                messages.error(request, 'Error creating account. Please try again.')
                form = SignUpForm()  # Reset form on error
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})
