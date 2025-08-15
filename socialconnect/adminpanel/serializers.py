from rest_framework import serializers
from django.contrib.auth import get_user_model
from posts.models import Post
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users in admin panel
    """
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active', 'is_email_verified',
            'date_joined', 'last_login', 'followers_count', 'following_count', 
            'posts_count', 'privacy_setting'
        ]

class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user information in admin panel
    """
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    total_likes_received = serializers.SerializerMethodField()
    total_comments_received = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active', 'is_email_verified',
            'date_joined', 'last_login', 'bio', 'avatar_url', 'website', 'location',
            'privacy_setting', 'followers_count', 'following_count', 'posts_count',
            'total_likes_received', 'total_comments_received'
        ]
    
    def get_total_likes_received(self, obj):
        """Get total likes received by user's posts"""
        return sum(post.like_count for post in obj.posts.filter(is_active=True))
    
    def get_total_comments_received(self, obj):
        """Get total comments received by user's posts"""
        return sum(post.comment_count for post in obj.posts.filter(is_active=True))

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user status in admin panel
    """
    class Meta:
        model = User
        fields = ['is_active', 'role']
    
    def validate_role(self, value):
        """Validate role assignment"""
        if value not in ['user', 'admin']:
            raise serializers.ValidationError("Invalid role. Must be 'user' or 'admin'.")
        return value

class AdminPostListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing posts in admin panel
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'author_username', 'author_email', 'category',
            'image_url', 'created_at', 'updated_at', 'is_active', 'like_count', 'comment_count'
        ]

class AdminPostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed post information in admin panel
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'author_username', 'author_email', 'category',
            'image_url', 'created_at', 'updated_at', 'is_active', 'like_count', 'comment_count'
        ]

class AdminStatsSerializer(serializers.Serializer):
    """
    Serializer for admin statistics
    """
    total_users = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    active_posts_today = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    users_created_today = serializers.IntegerField()
    posts_created_today = serializers.IntegerField()
    
    def to_representation(self, instance):
        """Calculate and return statistics"""
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        # User statistics
        total_users = User.objects.count()
        active_users_today = User.objects.filter(last_login__gte=today_start).count()
        users_created_today = User.objects.filter(date_joined__gte=today_start).count()
        
        # Post statistics
        total_posts = Post.objects.filter(is_active=True).count()
        active_posts_today = Post.objects.filter(
            is_active=True, 
            created_at__gte=today_start
        ).count()
        posts_created_today = Post.objects.filter(created_at__gte=today_start).count()
        
        # Engagement statistics
        total_likes = sum(post.like_count for post in Post.objects.filter(is_active=True))
        total_comments = sum(post.comment_count for post in Post.objects.filter(is_active=True))
        
        return {
            'total_users': total_users,
            'total_posts': total_posts,
            'active_users_today': active_users_today,
            'active_posts_today': active_posts_today,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'users_created_today': users_created_today,
            'posts_created_today': posts_created_today,
        }
