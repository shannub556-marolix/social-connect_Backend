from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from posts.models import Post

User = get_user_model()

class Like(models.Model):
    """
    Like model for post engagement
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.author.username}'s post"
    
    def clean(self):
        """Prevent users from liking their own posts"""
        if self.user == self.post.author:
            raise ValidationError("Users cannot like their own posts.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Comment(models.Model):
    """
    Comment model for post engagement
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.author.username}'s post"
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return user == self.user
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return user == self.user or user == self.post.author
