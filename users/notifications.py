from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    """Model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} {self.notification_type} for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


# Utility functions for creating notifications
def create_notification(recipient, sender, notification_type, message, content_object=None):
    """Create a new notification"""
    # Don't create notifications for self-actions
    if recipient == sender:
        return None
    
    # Check if user wants email notifications
    if hasattr(recipient, 'profile') and recipient.profile.email_notifications:
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            message=message,
            content_object=content_object
        )
        
        # Optionally send email notification here
        # send_email_notification(notification)
        
        return notification
    
    return None


def create_like_notification(post, user):
    """Create notification for post like"""
    message = f"{user.username} liked your post"
    return create_notification(
        recipient=post.user,
        sender=user,
        notification_type='like',
        message=message,
        content_object=post
    )


def create_comment_notification(comment, user):
    """Create notification for comment"""
    message = f"{user.username} commented on your post"
    return create_notification(
        recipient=comment.post.user,
        sender=user,
        notification_type='comment',
        message=message,
        content_object=comment
    )


def create_follow_notification(followed_user, follower):
    """Create notification for follow"""
    message = f"{follower.username} started following you"
    return create_notification(
        recipient=followed_user,
        sender=follower,
        notification_type='follow',
        message=message
    )


def get_unread_notification_count(user):
    """Get count of unread notifications for user"""
    return user.notifications.filter(is_read=False).count()


def mark_all_notifications_read(user):
    """Mark all notifications as read for user"""
    user.notifications.filter(is_read=False).update(is_read=True)