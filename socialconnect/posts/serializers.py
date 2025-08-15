from rest_framework import serializers
from .models import Post
from users.serializers import UserSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'author', 'image_url', 'category',
            'created_at', 'updated_at', 'is_active', 'like_count', 'comment_count'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'like_count', 'comment_count']

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'image_url', 'category']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content', 'image_url', 'category']
    
    def validate(self, data):
        post = self.instance
        user = self.context['request'].user
        
        if not post.can_edit(user):
            raise serializers.ValidationError("You can only edit your own posts.")
        
        return data

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'author', 'image_url', 'category',
            'created_at', 'like_count', 'comment_count'
        ]
