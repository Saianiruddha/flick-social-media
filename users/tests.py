from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.exceptions import ValidationError
from PIL import Image
import io
from .models import UserProfile
from .forms import SignUpForm, ProfileForm, UserForm
from posts.models import Post, Follow


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
    
    def test_profile_creation(self):
        """Test creating a user profile"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertFalse(self.profile.is_private)
        self.assertTrue(self.profile.email_notifications)
    
    def test_profile_str_method(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(self.profile), expected)
    
    def test_get_posts_count(self):
        """Test get_posts_count method"""
        # Initially no posts
        self.assertEqual(self.profile.get_posts_count(), 0)
        
        # Create a post
        Post.objects.create(user=self.user, caption='Test post')
        self.assertEqual(self.profile.get_posts_count(), 1)
        
        # Create an inactive post
        Post.objects.create(user=self.user, caption='Inactive post', is_active=False)
        self.assertEqual(self.profile.get_posts_count(), 1)  # Should still be 1
    
    def test_get_followers_count(self):
        """Test get_followers_count method"""
        # Create another user to follow
        follower = User.objects.create_user(
            username='follower',
            email='follower@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=follower)
        
        # Initially no followers
        self.assertEqual(self.profile.get_followers_count(), 0)
        
        # Create a follow relationship
        Follow.objects.create(follower=follower, following=self.user)
        self.assertEqual(self.profile.get_followers_count(), 1)
    
    def test_get_following_count(self):
        """Test get_following_count method"""
        # Create another user to follow
        following = User.objects.create_user(
            username='following',
            email='following@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=following)
        
        # Initially not following anyone
        self.assertEqual(self.profile.get_following_count(), 0)
        
        # Create a follow relationship
        Follow.objects.create(follower=self.user, following=following)
        self.assertEqual(self.profile.get_following_count(), 1)
    
    def test_is_following(self):
        """Test is_following method"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=other_user)
        
        # Initially not following
        self.assertFalse(self.profile.is_following(other_user))
        
        # Create a follow relationship
        Follow.objects.create(follower=self.user, following=other_user)
        self.assertTrue(self.profile.is_following(other_user))
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        expected_url = reverse('profile', kwargs={'username': self.user.username})
        self.assertEqual(self.profile.get_absolute_url(), expected_url)


class UserViewTest(TestCase):
    """Test cases for User views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_profile_view(self):
        """Test profile view"""
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
    
    def test_profile_view_nonexistent_user(self):
        """Test profile view for non-existent user"""
        response = self.client.get(reverse('profile', kwargs={'username': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)
    
    def test_edit_profile_view_authenticated(self):
        """Test edit profile view when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_profile_view_unauthenticated(self):
        """Test edit profile view when not authenticated"""
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_signup_view_get(self):
        """Test signup view GET request"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
    
    def test_signup_view_post_valid(self):
        """Test signup view with valid data"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        
        # Check that user and profile were created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class UserFormTest(TestCase):
    """Test cases for User forms"""
    
    def test_signup_form_valid(self):
        """Test signup form with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_signup_form_password_mismatch(self):
        """Test signup form with password mismatch"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match.', str(form.errors))
    
    def test_signup_form_invalid_username(self):
        """Test signup form with invalid username"""
        form_data = {
            'username': 'ab',  # Too short
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_signup_form_duplicate_username(self):
        """Test signup form with duplicate username"""
        # Create existing user
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='password123'
        )
        
        form_data = {
            'username': 'testuser',  # Duplicate username
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This username is already taken.', str(form.errors))
    
    def test_signup_form_duplicate_email(self):
        """Test signup form with duplicate email"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='password123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Duplicate email
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This email address is already registered.', str(form.errors))
    
    def create_test_image(self):
        """Create a test image for upload"""
        image = Image.new('RGB', (100, 100), color='blue')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_profile.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_profile_form_valid(self):
        """Test profile form with valid data"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.create(user=user)
        
        form_data = {
            'bio': 'Updated bio',
            'location': 'Test City',
            'website': 'https://example.com',
            'is_private': False,
            'email_notifications': True
        }
        image = self.create_test_image()
        form = ProfileForm(data=form_data, files={'profile_image': image}, instance=profile)
        self.assertTrue(form.is_valid())
    
    def test_profile_form_invalid_website(self):
        """Test profile form with invalid website URL"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.create(user=user)
        
        form_data = {
            'bio': 'Test bio',
            'website': 'invalid-url'  # Invalid URL format
        }
        form = ProfileForm(data=form_data, instance=profile)
        self.assertFalse(form.is_valid())
    
    def test_user_form_valid(self):
        """Test user form with valid data"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        form = UserForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
    
    def test_user_form_duplicate_username(self):
        """Test user form with duplicate username"""
        # Create existing users
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'existinguser',  # Duplicate username
            'email': 'test@example.com'
        }
        form = UserForm(data=form_data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn('This username is already taken.', str(form.errors))
