from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Prefetch
from django.core.exceptions import ValidationError
from .models import Post, Comment, Follow
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm

def home_view(request):
    return render(request, "home.html")

def feed_view(request):
    """Enhanced feed view with pagination and optimization"""
    # If user is authenticated, show posts from followed users first
    if request.user.is_authenticated:
        following_users = request.user.following.values_list('following', flat=True)
        
        # Get followed posts with optimized queries
        followed_posts = Post.objects.filter(
            is_active=True, 
            user__in=following_users
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes',
            Prefetch('comments', queryset=Comment.objects.filter(is_active=True).select_related('user').order_by('created_at'))
        ).order_by('-created_at')
        
        # Get other posts with optimized queries
        other_posts = Post.objects.filter(
            is_active=True
        ).exclude(
            user__in=following_users
        ).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes',
            Prefetch('comments', queryset=Comment.objects.filter(is_active=True).select_related('user').order_by('created_at'))
        ).order_by('-created_at')
        
        posts_list = list(followed_posts) + list(other_posts)
    else:
        # Get all active posts with optimized queries for non-authenticated users
        posts_list = Post.objects.filter(is_active=True).select_related(
            'user', 'user__profile'
        ).prefetch_related(
            'likes',
            Prefetch('comments', queryset=Comment.objects.filter(is_active=True).select_related('user').order_by('created_at'))
        ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 10)  # 10 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'page_obj': posts,  # For pagination template
    }
    return render(request, 'posts/feed.html', context)

def profile(request, username):
    """Enhanced profile view with pagination and optimization"""
    user_obj = get_object_or_404(User, username=username)
    
    # Get user's active posts with optimization
    posts_list = user_obj.posts.filter(is_active=True).select_related(
        'user'
    ).prefetch_related(
        'likes',
        'comments'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 12)  # 12 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # Check if current user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != user_obj:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=user_obj
        ).exists()
    
    context = {
        'profile': user_obj,
        'posts': posts,
        'page_obj': posts,
        'is_following': is_following,
        'posts_count': user_obj.posts.filter(is_active=True).count(),
        'followers_count': user_obj.followers.count(),
        'following_count': user_obj.following.count(),
    }
    return render(request, "users/profile.html", context)

@login_required
def create_post(request):
    """Enhanced post creation with proper form handling and validation"""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.full_clean()  # Run model validation
                post.save()
                messages.success(request, 'Post created successfully!')
                return redirect("feed")
            except ValidationError as e:
                messages.error(request, f'Error creating post: {e}')
            except Exception as e:
                messages.error(request, 'An error occurred while creating the post. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()
    
    return render(request, "posts/create_post.html", {'form': form})

@login_required
@require_http_methods(["POST"])
def like_post(request, post_id):
    """Enhanced like/unlike functionality with AJAX support"""
    try:
        post = get_object_or_404(Post, id=post_id, is_active=True)
        
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
            action = 'unliked'
        else:
            post.likes.add(request.user)
            liked = True
            action = 'liked'
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': post.total_likes(),
                'message': f'Post {action} successfully!'
            })
        else:
            messages.success(request, f'Post {action} successfully!')
            return redirect(request.META.get('HTTP_REFERER', 'feed'))
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            })
        else:
            messages.error(request, 'An error occurred while processing your request.')
            return redirect('feed')

@login_required
@require_http_methods(["POST"])
def delete_post(request, post_id):
    """Enhanced post deletion with proper validation"""
    try:
        post = get_object_or_404(Post, id=post_id, is_active=True)
        
        if request.user != post.user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You can only delete your own posts.'
                })
            else:
                messages.error(request, 'You can only delete your own posts.')
                return redirect('feed')
        
        # Soft delete - set is_active to False
        post.is_active = False
        post.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Post deleted successfully!'
            })
        else:
            messages.success(request, 'Post deleted successfully!')
            return redirect(request.META.get('HTTP_REFERER', 'profile'))
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while deleting the post.'
            })
        else:
            messages.error(request, 'An error occurred while deleting the post.')
            return redirect('feed')

def post_detail(request, post_id):
    """Enhanced post detail view with comments and optimization"""
    try:
        post = get_object_or_404(
            Post.objects.select_related('user', 'user__profile').prefetch_related(
                'likes',
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(is_active=True).select_related('user').order_by('created_at')
                )
            ),
            id=post_id,
            is_active=True
        )
        
        # Handle comment form submission
        if request.method == 'POST' and request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                try:
                    comment = comment_form.save(commit=False)
                    comment.post = post
                    comment.user = request.user
                    comment.save()
                    messages.success(request, 'Comment added successfully!')
                    return redirect('post_detail', post_id=post.id)
                except Exception as e:
                    messages.error(request, 'Error adding comment. Please try again.')
        else:
            comment_form = CommentForm() if request.user.is_authenticated else None
        
        context = {
            'post': post,
            'comment_form': comment_form,
            'comments': post.comments.filter(is_active=True).select_related('user'),
        }
        return render(request, 'posts/post_detail.html', context)
        
    except Exception as e:
        messages.error(request, 'Post not found or has been removed.')
        return redirect('feed')


@login_required
@require_http_methods(["POST"])
def follow_user(request, username):
    """Follow/Unfollow a user"""
    try:
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user == user_to_follow:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You cannot follow yourself.'
                })
            else:
                messages.error(request, 'You cannot follow yourself.')
                return redirect('profile', username=username)
        
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            follow_obj.delete()
            action = 'unfollowed'
            is_following = False
        else:
            action = 'followed'
            is_following = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'is_following': is_following,
                'followers_count': user_to_follow.followers.count(),
                'message': f'Successfully {action} {user_to_follow.username}!'
            })
        else:
            messages.success(request, f'Successfully {action} {user_to_follow.username}!')
            return redirect('profile', username=username)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            })
        else:
            messages.error(request, 'An error occurred while processing your request.')
            return redirect('profile', username=username)


@login_required
@require_http_methods(["POST"])
def add_comment(request, post_id):
    """Add a comment to a post via AJAX"""
    try:
        post = get_object_or_404(Post, id=post_id, is_active=True)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'user': comment.user.username,
                        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p')
                    },
                    'comments_count': post.comments.filter(is_active=True).count()
                })
            else:
                messages.success(request, 'Comment added successfully!')
                return redirect('post_detail', post_id=post.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid comment. Please try again.'
                })
            else:
                messages.error(request, 'Invalid comment. Please try again.')
                return redirect('post_detail', post_id=post.id)
                
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while adding the comment.'
            })
        else:
            messages.error(request, 'An error occurred while adding the comment.')
            return redirect('feed')


def search_users(request):
    """Search for users and posts"""
    query = request.GET.get('q', '').strip()
    users = []
    posts = []
    
    if query:
        # Search users - convert to list to avoid slicing issues
        users_queryset = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).select_related('profile')
        users = list(users_queryset[:10])  # Convert to list immediately
        
        # Search posts by caption - convert to list to avoid slicing issues
        posts_queryset = Post.objects.filter(
            Q(caption__icontains=query),
            is_active=True
        ).select_related('user', 'user__profile').order_by('-created_at')
        posts = list(posts_queryset[:10])  # Convert to list immediately
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        users_data = [{
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'profile_image': user.profile.profile_image.url if hasattr(user, 'profile') and user.profile.profile_image else '/static/images/default-profile.png'
        } for user in users]
        
        posts_data = [{
            'id': post.id,
            'caption': post.caption[:100] + '...' if len(post.caption) > 100 else post.caption,
            'user': post.user.username,
            'image': post.image.url if post.image else None,
            'created_at': post.created_at.strftime('%B %d, %Y')
        } for post in posts]
        
        return JsonResponse({
            'users': users_data,
            'posts': posts_data
        })
    
    context = {
        'query': query,
        'users': users,
        'posts': posts
    }
    return render(request, 'posts/search.html', context)
