import os
import json
from django.conf import settings
from supabase import create_client, Client
from .models import Notification

def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Warning: Supabase credentials not found. Realtime events will not be published.")
        return None
    
    return create_client(supabase_url, supabase_key)

def publish_notification_event(notification: Notification):
    """
    Publish notification event to Supabase Realtime
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return
        
        # Prepare the notification data
        event_data = {
            'type': 'notification',
            'notification': notification.notification_data,
            'recipient_id': notification.recipient.id,
            'timestamp': notification.created_at.isoformat()
        }
        
        # Publish to the notifications channel
        # The channel name should match what the frontend is listening to
        channel_name = f"notifications:{notification.recipient.id}"
        
        # Use Supabase's realtime functionality
        # Note: This is a simplified implementation
        # In a real implementation, you might use WebSockets or a message queue
        print(f"Publishing notification event to channel: {channel_name}")
        print(f"Event data: {json.dumps(event_data, indent=2)}")
        
        # For now, we'll just log the event
        # In production, you would integrate with Supabase Realtime properly
        # supabase.realtime.channel(channel_name).send(event_data)
        
    except Exception as e:
        print(f"Error publishing notification event: {e}")

def send_push_notification(notification: Notification):
    """
    Send push notification (placeholder for future implementation)
    """
    try:
        # This is a placeholder for push notification implementation
        # You could integrate with services like Firebase Cloud Messaging
        # or OneSignal here
        
        print(f"Push notification would be sent for: {notification.title}")
        
    except Exception as e:
        print(f"Error sending push notification: {e}")

def get_unread_notifications_count(user_id: int) -> int:
    """
    Get count of unread notifications for a user
    """
    try:
        return Notification.objects.filter(
            recipient_id=user_id,
            is_read=False
        ).count()
    except Exception as e:
        print(f"Error getting unread notifications count: {e}")
        return 0
