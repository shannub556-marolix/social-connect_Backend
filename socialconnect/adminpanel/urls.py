from django.urls import path
from .views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserUpdateView,
    AdminPostListView,
    AdminPostDetailView,
    AdminPostDeleteView,
    AdminStatsView
)

app_name = 'adminpanel'

urlpatterns = [
    # User Management
    path('users/', AdminUserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', AdminUserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/update/', AdminUserUpdateView.as_view(), name='user-update'),
    
    # Post Management
    path('posts/', AdminPostListView.as_view(), name='post-list'),
    path('posts/<int:post_id>/', AdminPostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/delete/', AdminPostDeleteView.as_view(), name='post-delete'),
    
    # Statistics
    path('stats/', AdminStatsView.as_view(), name='stats'),
]
