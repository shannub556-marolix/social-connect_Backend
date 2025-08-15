from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model
    """
    list_display = [
        'id', 'recipient', 'sender', 'notification_type', 
        'title', 'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'created_at'
    ]
    search_fields = [
        'recipient__username', 'sender__username', 'title', 'message'
    ]
    readonly_fields = [
        'id', 'created_at', 'notification_data'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'recipient', 'sender', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message')
        }),
        ('Related Objects', {
            'fields': ('post', 'like', 'comment', 'follow'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
        ('Data', {
            'fields': ('notification_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'recipient', 'sender', 'post', 'like', 'comment', 'follow'
        )
    
    def mark_as_read(self, request, queryset):
        """Admin action to mark notifications as read"""
        count = queryset.update(is_read=True)
        self.message_user(
            request, 
            f"Successfully marked {count} notification(s) as read."
        )
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """Admin action to mark notifications as unread"""
        count = queryset.update(is_read=False)
        self.message_user(
            request, 
            f"Successfully marked {count} notification(s) as unread."
        )
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    actions = [mark_as_read, mark_as_unread]
