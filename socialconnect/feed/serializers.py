from rest_framework import serializers
from posts.models import Post
from engagement.models import Like
from users.models import User

class FeedPostSerializer(serializers.ModelSerializer):
    """
    Serializer for posts in the feed with engagement data
    """
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.CharField(source='author.avatar_url', read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'image_url', 'category', 'created_at', 'updated_at',
            'author_id', 'author_username', 'author_avatar', 'like_count', 'comment_count', 'is_liked_by_user'
        ]
    
    def get_like_count(self, obj):
        """Get the number of likes for this post"""
        return obj.like_count
    
    def get_comment_count(self, obj):
        """Get the number of comments for this post"""
        return obj.comment_count
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
