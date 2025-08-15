from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer, PostListSerializer
)
from .utils import process_post_image_upload

class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Create a new post with optional image upload
        """
        try:
            # Handle image upload if provided
            image_url = None
            if 'image' in request.FILES:
                # Create a temporary post to get an ID for image naming
                temp_post = Post.objects.create(
                    author=request.user,
                    content=request.data.get('content', ''),
                    category=request.data.get('category', 'general')
                )
                
                try:
                    image_url = process_post_image_upload(request.FILES['image'], temp_post.id)
                    # Update the temporary post with the image URL
                    temp_post.image_url = image_url
                    temp_post.save()
                    return Response(PostSerializer(temp_post).data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    # If image upload fails, delete the temporary post
                    temp_post.delete()
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create post without image
            serializer = PostCreateSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            post = serializer.save()
            
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, post_id):
        """
        Retrieve a specific post by ID
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, post_id):
        """
        Update own post
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            # Check if user can edit this post
            if not post.can_edit(request.user):
                return Response({"detail": "You can only edit your own posts."}, status=status.HTTP_403_FORBIDDEN)
            
            # Handle image upload if provided
            if 'image' in request.FILES:
                try:
                    image_url = process_post_image_upload(request.FILES['image'], post.id)
                    request.data['image_url'] = image_url
                except Exception as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = PostUpdateSerializer(post, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            updated_post = serializer.save()
            
            return Response(PostSerializer(updated_post).data)
            
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, post_id):
        """
        Partial update of own post
        """
        return self.put(request, post_id)
    
    def delete(self, request, post_id):
        """
        Delete own post (soft delete by setting is_active=False)
        """
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            # Check if user can delete this post
            if not post.can_delete(request.user):
                return Response({"detail": "You can only delete your own posts."}, status=status.HTTP_403_FORBIDDEN)
            
            # Soft delete
            post.is_active = False
            post.save()
            
            return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

class PostListView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = PostPagination
    
    def get(self, request):
        """
        List posts (public, paginated) with optional filtering
        """
        try:
            # Get query parameters
            category = request.query_params.get('category')
            author_id = request.query_params.get('author')
            search = request.query_params.get('search')
            
            # Start with active posts
            queryset = Post.objects.filter(is_active=True)
            
            # Apply filters
            if category:
                queryset = queryset.filter(category=category)
            
            if author_id:
                queryset = queryset.filter(author_id=author_id)
            
            if search:
                queryset = queryset.filter(
                    Q(content__icontains=search) | 
                    Q(author__username__icontains=search)
                )
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(queryset, request)
            
            serializer = PostListSerializer(paginated_posts, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MyPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
    
    def get(self, request):
        """
        Get current user's posts
        """
        try:
            queryset = Post.objects.filter(author=request.user, is_active=True)
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(queryset, request)
            
            serializer = PostListSerializer(paginated_posts, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
