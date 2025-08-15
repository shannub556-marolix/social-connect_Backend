from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification objects
    """
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.CharField(source='sender.avatar_url', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read', 'created_at',
            'sender_username', 'sender_avatar', 'post', 'like', 'comment', 'follow'
        ]
        read_only_fields = [
            'id', 'notification_type', 'title', 'message', 'created_at',
            'sender_username', 'sender_avatar', 'post', 'like', 'comment', 'follow'
        ]

class NotificationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing notifications with additional data
    """
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.CharField(source='sender.avatar_url', read_only=True)
    notification_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read', 'created_at',
            'sender_username', 'sender_avatar', 'notification_data'
        ]
    
    def get_notification_data(self, obj):
        """Get structured notification data"""
        return obj.notification_data

class NotificationReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read
    """
    is_read = serializers.BooleanField(default=True)

class NotificationCountSerializer(serializers.Serializer):
    """
    Serializer for notification counts
    """
    unread_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
