from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from posts.models import Post
from .models import Like, Comment
from .serializers import (
    LikeSerializer, CommentSerializer, CommentCreateSerializer, 
    CommentUpdateSerializer, LikeStatusSerializer
)

class CommentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, post_id):
        """
        Like a post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            # Check if user is trying to like their own post
            if request.user == post.author:
                return Response(
                    {"detail": "You cannot like your own post."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if already liked
            if Like.objects.filter(user=request.user, post=post).exists():
                return Response(
                    {"detail": "You have already liked this post."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create like
            like = Like.objects.create(user=request.user, post=post)
            serializer = LikeSerializer(like)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UnlikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, post_id):
        """
        Unlike a post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            like = get_object_or_404(Like, user=request.user, post=post)
            like.delete()
            
            return Response(
                {"detail": "Post unliked successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LikeStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, post_id):
        """
        Check if current user has liked the post and get like count
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            is_liked = Like.objects.filter(user=request.user, post=post).exists()
            like_count = post.like_count
            
            data = {
                "is_liked": is_liked,
                "like_count": like_count
            }
            
            serializer = LikeStatusSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CommentListView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = CommentPagination
    
    def get(self, request, post_id):
        """
        List comments for a post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            comments = Comment.objects.filter(post=post, is_active=True)
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_comments = paginator.paginate_queryset(comments, request)
            
            serializer = CommentSerializer(paginated_comments, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, post_id):
        """
        Add a comment to a post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            serializer = CommentCreateSerializer(
                data=request.data, 
                context={'request': request, 'post': post}
            )
            serializer.is_valid(raise_exception=True)
            comment = serializer.save()
            
            return Response(
                CommentSerializer(comment).data, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, post_id, comment_id):
        """
        Delete own comment or comment on own post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            comment = get_object_or_404(Comment, id=comment_id, post=post, is_active=True)
            
            # Check permissions
            if not comment.can_delete(request.user):
                return Response(
                    {"detail": "You can only delete your own comments or comments on your posts."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Soft delete
            comment.is_active = False
            comment.save()
            
            return Response(
                {"detail": "Comment deleted successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
