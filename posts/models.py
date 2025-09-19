from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image
import os

def validate_image_size(image):
    """Validate image file size (max 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(f'Image file too large ( > 5MB )')

def post_image_path(instance, filename):
    """Generate upload path for post images"""
    return f'posts/{instance.user.username}/{filename}'

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(
        upload_to=post_image_path, 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ],
        help_text='Upload an image (JPG, JPEG, PNG, WEBP) - Max size: 5MB'
    )
    caption = models.TextField(blank=True, max_length=2000, help_text='Write a caption (max 2000 characters)')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    is_active = models.BooleanField(default=True)  # For soft delete

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]

    def clean(self):
        """Model validation"""
        if not self.image and not self.caption:
            raise ValidationError('Post must have either an image or caption.')

    def save(self, *args, **kwargs):
        """Override save to resize images"""
        super().save(*args, **kwargs)
        
        if self.image:
            # Resize image if too large
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size, Image.LANCZOS)
                img.save(self.image.path)

    def total_likes(self):
        return self.likes.count()

    def is_liked_by(self, user):
        """Check if post is liked by specific user"""
        return self.likes.filter(id=user.id).exists()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post_detail', kwargs={'post_id': self.id})

    def __str__(self):
        return f"{self.user.username} - {self.caption[:50]}{'...' if len(self.caption) > 50 else ''}"


class Comment(models.Model):
    """Comment model for posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, help_text='Write a comment (max 500 characters)')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # For moderation

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} on {self.post.user.username}'s post: {self.content[:30]}..."


class Follow(models.Model):
    """Follow relationship model"""
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]

    def clean(self):
        """Prevent users from following themselves"""
        if self.follower == self.following:
            raise ValidationError('Users cannot follow themselves.')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
