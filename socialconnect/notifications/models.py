from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from posts.models import Post
from engagement.models import Like, Comment
from users.models import Follow

User = get_user_model()

class Notification(models.Model):
    """
    Notification model for user notifications
    """
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
    ]
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications',
        null=True, 
        blank=True
    )
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    
    # Related objects (optional based on notification type)
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    like = models.ForeignKey(
        Like, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    follow = models.ForeignKey(
        Follow, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    
    # Notification content
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"
    
    @property
    def notification_data(self):
        """Return structured data for the notification"""
        data = {
            'id': self.id,
            'type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'sender': {
                'id': self.sender.id,
                'username': self.sender.username,
                'avatar_url': self.sender.avatar_url,
            } if self.sender else None,
        }
        
        # Add type-specific data
        if self.notification_type == 'like' and self.post:
            data['post'] = {
                'id': self.post.id,
                'content': self.post.content[:100] + '...' if len(self.post.content) > 100 else self.post.content,
            }
        elif self.notification_type == 'comment' and self.post:
            data['post'] = {
                'id': self.post.id,
                'content': self.post.content[:100] + '...' if len(self.post.content) > 100 else self.post.content,
            }
            if self.comment:
                data['comment'] = {
                    'id': self.comment.id,
                    'content': self.comment.content[:100] + '...' if len(self.comment.content) > 100 else self.comment.content,
                }
        
        return data
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    @classmethod
    def create_follow_notification(cls, follow_instance):
        """Create a follow notification"""
        return cls.objects.create(
            recipient=follow_instance.following,
            sender=follow_instance.follower,
            notification_type='follow',
            follow=follow_instance,
            title=f"{follow_instance.follower.username} started following you",
            message=f"{follow_instance.follower.username} started following you"
        )
    
    @classmethod
    def create_like_notification(cls, like_instance):
        """Create a like notification"""
        return cls.objects.create(
            recipient=like_instance.post.author,
            sender=like_instance.user,
            notification_type='like',
            post=like_instance.post,
            like=like_instance,
            title=f"{like_instance.user.username} liked your post",
            message=f"{like_instance.user.username} liked your post: {like_instance.post.content[:50]}..."
        )
    
    @classmethod
    def create_comment_notification(cls, comment_instance):
        """Create a comment notification"""
        return cls.objects.create(
            recipient=comment_instance.post.author,
            sender=comment_instance.user,
            notification_type='comment',
            post=comment_instance.post,
            comment=comment_instance,
            title=f"{comment_instance.user.username} commented on your post",
            message=f"{comment_instance.user.username} commented: {comment_instance.content[:50]}..."
        )
