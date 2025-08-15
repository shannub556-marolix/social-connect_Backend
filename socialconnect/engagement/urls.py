from django.urls import path
from .views import (
    LikePostView, UnlikePostView, LikeStatusView,
    CommentListView, CommentCreateView, CommentDetailView
)

urlpatterns = [
    # Like endpoints
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like_post"),
    path("posts/<int:post_id>/unlike/", UnlikePostView.as_view(), name="unlike_post"),
    path("posts/<int:post_id>/like-status/", LikeStatusView.as_view(), name="like_status"),
    
    # Comment endpoints
    path("posts/<int:post_id>/comments/", CommentListView.as_view(), name="comment_list"),
    path("posts/<int:post_id>/comments/create/", CommentCreateView.as_view(), name="comment_create"),
    path("posts/<int:post_id>/comments/<int:comment_id>/", CommentDetailView.as_view(), name="comment_detail"),
]
