from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Notification
from .serializers import (
    NotificationListSerializer, 
    NotificationReadSerializer, 
    NotificationCountSerializer
)
from .utils import get_unread_notifications_count

class NotificationPagination(PageNumberPagination):
    """Pagination for notifications - 20 per page"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class NotificationListView(APIView):
    """
    GET /api/notifications/
    List notifications for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get(self, request):
        """
        Get paginated list of notifications for the current user
        """
        try:
            user = request.user
            
            # Get notifications for the current user
            notifications = Notification.objects.filter(
                recipient=user
            ).select_related('sender', 'post', 'like', 'comment', 'follow').order_by('-created_at')
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_notifications = paginator.paginate_queryset(notifications, request)
            
            # Serialize the notifications
            serializer = NotificationListSerializer(
                paginated_notifications, 
                many=True, 
                context={'request': request}
            )
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching notifications: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationReadView(APIView):
    """
    POST /api/notifications/{id}/read/
    Mark a specific notification as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, notification_id):
        """
        Mark a specific notification as read
        """
        try:
            user = request.user
            
            # Get the notification and ensure it belongs to the current user
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                recipient=user
            )
            
            # Mark as read
            notification.mark_as_read()
            
            return Response({
                "detail": "Notification marked as read successfully.",
                "notification_id": notification.id
            })
            
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error marking notification as read: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationMarkAllReadView(APIView):
    """
    POST /api/notifications/mark-all-read/
    Mark all notifications as read for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Mark all unread notifications as read
        """
        try:
            user = request.user
            
            # Get all unread notifications for the user
            unread_notifications = Notification.objects.filter(
                recipient=user,
                is_read=False
            )
            
            # Mark all as read
            count = unread_notifications.count()
            unread_notifications.update(is_read=True)
            
            return Response({
                "detail": f"Marked {count} notifications as read successfully.",
                "marked_count": count
            })
            
        except Exception as e:
            return Response(
                {"detail": f"Error marking notifications as read: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationCountView(APIView):
    """
    GET /api/notifications/count/
    Get notification counts for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get unread and total notification counts
        """
        try:
            user = request.user
            
            # Get counts
            unread_count = get_unread_notifications_count(user.id)
            total_count = Notification.objects.filter(recipient=user).count()
            
            data = {
                "unread_count": unread_count,
                "total_count": total_count
            }
            
            serializer = NotificationCountSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching notification counts: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
