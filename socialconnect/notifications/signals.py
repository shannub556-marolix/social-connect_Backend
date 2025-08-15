from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from users.models import Follow
from engagement.models import Like, Comment
from .models import Notification
from .utils import publish_notification_event

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    Create notification when someone follows a user
    """
    if created:
        try:
            # Don't notify if user follows themselves
            if instance.follower != instance.following:
                notification = Notification.create_follow_notification(instance)
                
                # Publish to Supabase Realtime
                publish_notification_event(notification)
                
        except Exception as e:
            # Log error but don't break the follow operation
            print(f"Error creating follow notification: {e}")

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """
    Create notification when someone likes a post
    """
    if created:
        try:
            # Don't notify if user likes their own post
            if instance.user != instance.post.author:
                notification = Notification.create_like_notification(instance)
                
                # Publish to Supabase Realtime
                publish_notification_event(notification)
                
        except Exception as e:
            # Log error but don't break the like operation
            print(f"Error creating like notification: {e}")

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """
    Create notification when someone comments on a post
    """
    if created and instance.is_active:
        try:
            # Don't notify if user comments on their own post
            if instance.user != instance.post.author:
                notification = Notification.create_comment_notification(instance)
                
                # Publish to Supabase Realtime
                publish_notification_event(notification)
                
        except Exception as e:
            # Log error but don't break the comment operation
            print(f"Error creating comment notification: {e}")
