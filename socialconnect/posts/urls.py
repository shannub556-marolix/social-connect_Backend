from django.urls import path
from .views import (
    PostCreateView, PostDetailView, PostListView, MyPostsView
)

urlpatterns = [
    # Post CRUD operations
    path("", PostListView.as_view(), name="post_list"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("my/", MyPostsView.as_view(), name="my_posts"),
    path("<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
]
