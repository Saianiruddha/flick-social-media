from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.exceptions import ValidationError
from PIL import Image
import io
from .models import Post, Comment, Follow
from users.models import UserProfile


class PostModelTest(TestCase):
    """Test cases for Post model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user2)
    
    def test_post_creation(self):
        """Test creating a post with caption only"""
        post = Post.objects.create(
            user=self.user,
            caption='Test post caption'
        )
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.caption, 'Test post caption')
        self.assertTrue(post.is_active)
        self.assertEqual(post.total_likes(), 0)
    
    def test_post_str_method(self):
        """Test Post string representation"""
        post = Post.objects.create(
            user=self.user,
            caption='Test post with a long caption that should be truncated'
        )
        expected = f"{self.user.username} - Test post with a long caption that should be t..."
        self.assertEqual(str(post), expected)
    
    def test_post_likes(self):
        """Test post like functionality"""
        post = Post.objects.create(
            user=self.user,
            caption='Test post'
        )
        
        # Initially no likes
        self.assertEqual(post.total_likes(), 0)
        self.assertFalse(post.is_liked_by(self.user2))
        
        # Add a like
        post.likes.add(self.user2)
        self.assertEqual(post.total_likes(), 1)
        self.assertTrue(post.is_liked_by(self.user2))
    
    def test_post_validation(self):
        """Test post validation - requires caption or image"""
        post = Post(user=self.user)
        with self.assertRaises(ValidationError):
            post.full_clean()
    
    def test_post_get_absolute_url(self):
        """Test post get_absolute_url method"""
        post = Post.objects.create(
            user=self.user,
            caption='Test post'
        )
        expected_url = reverse('post_detail', kwargs={'post_id': post.id})
        self.assertEqual(post.get_absolute_url(), expected_url)


class CommentModelTest(TestCase):
    """Test cases for Comment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.post = Post.objects.create(
            user=self.user,
            caption='Test post'
        )
    
    def test_comment_creation(self):
        """Test creating a comment"""
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Test comment')
        self.assertTrue(comment.is_active)
    
    def test_comment_str_method(self):
        """Test Comment string representation"""
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='This is a test comment that is longer than thirty characters'
        )
        expected = f"{self.user.username} on {self.post.user.username}'s post: This is a test comment that i..."
        self.assertEqual(str(comment), expected)


class FollowModelTest(TestCase):
    """Test cases for Follow model"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user1)
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user2)
    
    def test_follow_creation(self):
        """Test creating a follow relationship"""
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)
    
    def test_follow_str_method(self):
        """Test Follow string representation"""
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        expected = f"{self.user1.username} follows {self.user2.username}"
        self.assertEqual(str(follow), expected)
    
    def test_follow_validation_self_follow(self):
        """Test that users cannot follow themselves"""
        follow = Follow(follower=self.user1, following=self.user1)
        with self.assertRaises(ValidationError):
            follow.full_clean()
    
    def test_unique_follow_constraint(self):
        """Test that duplicate follows are not allowed"""
        Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        # Try to create duplicate - should raise integrity error
        with self.assertRaises(Exception):
            Follow.objects.create(
                follower=self.user1,
                following=self.user2
            )


class PostViewTest(TestCase):
    """Test cases for Post views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.post = Post.objects.create(
            user=self.user,
            caption='Test post'
        )
    
    def test_feed_view(self):
        """Test feed view"""
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test post')
    
    def test_post_detail_view(self):
        """Test post detail view"""
        response = self.client.get(reverse('post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test post')
    
    def test_create_post_view_authenticated(self):
        """Test create post view when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_post_view_unauthenticated(self):
        """Test create post view when not authenticated"""
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_like_post_authenticated(self):
        """Test liking a post when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)  # Redirect after like
        
        # Check that like was added
        self.post.refresh_from_db()
        self.assertEqual(self.post.total_likes(), 1)
    
    def test_like_post_unauthenticated(self):
        """Test liking a post when not authenticated"""
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_search_view(self):
        """Test search view"""
        response = self.client.get(reverse('search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Results')


class PostFormTest(TestCase):
    """Test cases for Post forms"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
    
    def create_test_image(self):
        """Create a test image for upload"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_post_form_with_caption(self):
        """Test post form with caption only"""
        from .forms import PostForm
        form_data = {'caption': 'Test caption'}
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_post_form_with_image(self):
        """Test post form with image only"""
        from .forms import PostForm
        image = self.create_test_image()
        form = PostForm(data={}, files={'image': image})
        self.assertTrue(form.is_valid())
    
    def test_post_form_empty(self):
        """Test post form with no data - should be invalid"""
        from .forms import PostForm
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('Please provide either a caption or an image for your post.', str(form.errors))
