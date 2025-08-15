from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from posts.models import Post
from users.models import User, Follow
from .serializers import FeedPostSerializer

class FeedPagination(PageNumberPagination):
    """Pagination for feed posts - 20 per page"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class FeedView(APIView):
    """
    GET /api/feed/
    Fetch posts from followed users + self, ordered by creation date descending
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = FeedPagination
    
    def get(self, request):
        """
        Get personalized feed for the authenticated user
        """
        try:
            user = request.user
            
            # Get users that the current user follows
            following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
            
            # Create a list of users to include in feed (followed users + self)
            feed_users = list(following_users) + [user.id]
            
            # Query posts from these users, ordered by creation date descending
            posts = Post.objects.filter(
                author__id__in=feed_users,
                is_active=True
            ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
            
            # Apply pagination
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)
            
            # Serialize the posts with engagement data
            serializer = FeedPostSerializer(
                paginated_posts, 
                many=True, 
                context={'request': request}
            )
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error fetching feed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
