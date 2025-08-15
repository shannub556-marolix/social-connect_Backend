from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('technology', 'Technology'),
        ('lifestyle', 'Lifestyle'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('sports', 'Sports'),
        ('entertainment', 'Entertainment'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}..."
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.filter(is_active=True).count()
    
    def can_edit(self, user):
        """Check if user can edit this post"""
        return user == self.author
    
    def can_delete(self, user):
        """Check if user can delete this post"""
        return user == self.author
