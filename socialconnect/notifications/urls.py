from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationMarkAllReadView,
    NotificationCountView
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('count/', NotificationCountView.as_view(), name='notification-count'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='mark-all-read'),
    path('<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
]
