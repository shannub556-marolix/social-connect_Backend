from rest_framework import serializers
from .models import Like, Comment
from users.serializers import UserSerializer

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_active']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['post'] = self.context['post']
        return super().create(validated_data)

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate(self, data):
        comment = self.instance
        user = self.context['request'].user
        
        if not comment.can_edit(user):
            raise serializers.ValidationError("You can only edit your own comments.")
        
        return data

class LikeStatusSerializer(serializers.Serializer):
    is_liked = serializers.BooleanField()
    like_count = serializers.IntegerField()
