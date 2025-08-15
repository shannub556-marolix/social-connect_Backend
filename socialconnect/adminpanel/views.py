from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from posts.models import Post
from .serializers import (
    AdminUserListSerializer, AdminUserDetailSerializer, AdminUserUpdateSerializer,
    AdminPostListSerializer, AdminPostDetailSerializer, AdminStatsSerializer
)
from .permissions import IsAdminUser

User = get_user_model()

class AdminPagination(PageNumberPagination):
    """Pagination for admin panel - 20 per page"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# User Management Views

class AdminUserListView(APIView):
    """
    GET /api/admin/users/
    List all users (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    pagination_class = AdminPagination
    
    def get(self, request):
        """
        Get paginated list of all users
        """
        try:
            # Get all users with related data
            users = User.objects.select_related().prefetch_related(
                'posts', 'followers', 'following'
            ).order_by('-date_joined')
            
            # Apply search filter if provided
            search = request.query_params.get('search', None)
            if search:
                users = users.filter(
                    Q(username__icontains=search) |
                    Q(email__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search)
                )
            
            # Apply role filter if provided
            role = request.query_params.get('role', None)
            if role:
                users = users.filter(role=role)
            
            # Apply status filter if provided
            is_active = request.query_params.get('is_active', None)
            if is_active is not None:
                is_active_bool = is_active.lower() == 'true'
                users = users.filter(is_active=is_active_bool)
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_users = paginator.paginate_queryset(users, request)
            
            # Serialize the users
            serializer = AdminUserListSerializer(
                paginated_users, 
                many=True, 
                context={'request': request}
            )
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching users: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminUserDetailView(APIView):
    """
    GET /api/admin/users/{user_id}/
    Get detailed user information (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request, user_id):
        """
        Get detailed information about a specific user
        """
        try:
            user = get_object_or_404(User, id=user_id)
            
            serializer = AdminUserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error fetching user details: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminUserUpdateView(APIView):
    """
    PUT /api/admin/users/{user_id}/
    Update user status (activate/deactivate, change role) (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def put(self, request, user_id):
        """
        Update user status and role
        """
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Prevent admin from deactivating themselves
            if user == request.user and not request.data.get('is_active', True):
                return Response(
                    {"detail": "You cannot deactivate your own account."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.save()
            
            return Response({
                "detail": "User updated successfully.",
                "user": AdminUserDetailSerializer(updated_user, context={'request': request}).data
            })
            
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error updating user: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Post Management Views

class AdminPostListView(APIView):
    """
    GET /api/admin/posts/
    List all posts (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    pagination_class = AdminPagination
    
    def get(self, request):
        """
        Get paginated list of all posts
        """
        try:
            # Get all posts with related data
            posts = Post.objects.select_related('author').prefetch_related(
                'likes', 'comments'
            ).order_by('-created_at')
            
            # Apply search filter if provided
            search = request.query_params.get('search', None)
            if search:
                posts = posts.filter(
                    Q(content__icontains=search) |
                    Q(author__username__icontains=search) |
                    Q(author__email__icontains=search)
                )
            
            # Apply category filter if provided
            category = request.query_params.get('category', None)
            if category:
                posts = posts.filter(category=category)
            
            # Apply status filter if provided
            is_active = request.query_params.get('is_active', None)
            if is_active is not None:
                is_active_bool = is_active.lower() == 'true'
                posts = posts.filter(is_active=is_active_bool)
            
            # Apply author filter if provided
            author_id = request.query_params.get('author_id', None)
            if author_id:
                posts = posts.filter(author_id=author_id)
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)
            
            # Serialize the posts
            serializer = AdminPostListSerializer(
                paginated_posts, 
                many=True, 
                context={'request': request}
            )
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching posts: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminPostDetailView(APIView):
    """
    GET /api/admin/posts/{post_id}/
    Get detailed post information (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request, post_id):
        """
        Get detailed information about a specific post
        """
        try:
            post = get_object_or_404(Post, id=post_id)
            
            serializer = AdminPostDetailSerializer(post, context={'request': request})
            return Response(serializer.data)
            
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error fetching post details: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminPostDeleteView(APIView):
    """
    DELETE /api/admin/posts/{post_id}/
    Delete any post (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def delete(self, request, post_id):
        """
        Delete a post (soft delete by setting is_active=False)
        """
        try:
            post = get_object_or_404(Post, id=post_id)
            
            # Soft delete the post
            post.is_active = False
            post.save()
            
            return Response({
                "detail": "Post deleted successfully.",
                "post_id": post.id
            })
            
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Error deleting post: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Statistics View

class AdminStatsView(APIView):
    """
    GET /api/admin/stats/
    Get platform statistics (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """
        Get comprehensive platform statistics
        """
        try:
            serializer = AdminStatsSerializer()
            stats = serializer.to_representation(None)
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching statistics: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
