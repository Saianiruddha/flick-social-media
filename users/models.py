from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

def validate_profile_image_size(image):
    """Validate profile image file size (max 2MB)"""
    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise ValidationError(f'Profile image file too large ( > 2MB )')

def profile_image_path(instance, filename):
    """Generate upload path for profile images"""
    return f'profiles/{instance.user.username}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(
        blank=True, 
        max_length=500, 
        help_text='Tell us about yourself (max 500 characters)'
    )
    profile_image = models.ImageField(
        upload_to=profile_image_path,
        default='profiles/default-profile.png',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_profile_image_size
        ],
        help_text='Upload a profile picture (JPG, JPEG, PNG, WEBP) - Max size: 2MB'
    )
    birth_date = models.DateField(null=True, blank=True, help_text='Your birth date (optional)')
    location = models.CharField(max_length=100, blank=True, help_text='Your location (optional)')
    website = models.URLField(blank=True, help_text='Your website URL (optional)')
    is_private = models.BooleanField(default=False, help_text='Make your account private')
    email_notifications = models.BooleanField(default=True, help_text='Receive email notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        """Override save to resize profile images"""
        super().save(*args, **kwargs)
        
        if self.profile_image and self.profile_image.name != 'profiles/default-profile.png':
            # Resize image if too large
            img = Image.open(self.profile_image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size, Image.LANCZOS)
                img.save(self.profile_image.path)

    def get_followers_count(self):
        """Get the number of followers"""
        return self.user.followers.count()

    def get_following_count(self):
        """Get the number of users being followed"""
        return self.user.following.count()

    def get_posts_count(self):
        """Get the number of posts"""
        return self.user.posts.filter(is_active=True).count()

    def is_following(self, user):
        """Check if this user is following another user"""
        return self.user.following.filter(following=user).exists()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('profile', kwargs={'username': self.user.username})

    def __str__(self):
        return f"{self.user.username}'s profile"


# Import the notification models
from .notifications import Notification

