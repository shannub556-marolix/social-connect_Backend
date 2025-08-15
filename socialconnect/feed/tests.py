from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from posts.models import Post
from engagement.models import Like, Comment
from users.models import Follow
from .views import FeedView

User = get_user_model()

class FeedViewTest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # Create posts
        self.post1 = Post.objects.create(
            author=self.user1,
            content='Post by user1',
            category='general'
        )
        self.post2 = Post.objects.create(
            author=self.user2,
            content='Post by user2',
            category='technology'
        )
        self.post3 = Post.objects.create(
            author=self.user3,
            content='Post by user3',
            category='lifestyle'
        )
        self.post4 = Post.objects.create(
            author=self.user1,
            content='Another post by user1',
            category='general'
        )
        
        # Create follow relationship (user1 follows user2)
        Follow.objects.create(follower=self.user1, following=self.user2)
        
        # Create engagement
        Like.objects.create(user=self.user1, post=self.post2)
        Comment.objects.create(user=self.user1, post=self.post2, content='Great post!')
    
    def test_feed_requires_authentication(self):
        """Test that feed endpoint requires authentication"""
        response = self.client.get('/api/feed/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_feed_returns_followed_users_posts(self):
        """Test that feed returns posts from followed users"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should return posts from user1 (self) and user2 (followed)
        post_ids = [post['id'] for post in response.data['results']]
        self.assertIn(self.post1.id, post_ids)  # user1's post
        self.assertIn(self.post2.id, post_ids)  # user2's post (followed)
        self.assertIn(self.post4.id, post_ids)  # user1's another post
        self.assertNotIn(self.post3.id, post_ids)  # user3's post (not followed)
    
    def test_feed_includes_engagement_data(self):
        """Test that feed includes like/comment counts and user like status"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find post2 in results
        post2_data = None
        for post in response.data['results']:
            if post['id'] == self.post2.id:
                post2_data = post
                break
        
        self.assertIsNotNone(post2_data)
        self.assertEqual(post2_data['like_count'], 1)
        self.assertEqual(post2_data['comment_count'], 1)
        self.assertTrue(post2_data['is_liked_by_user'])  # user1 liked this post
    
    def test_feed_pagination(self):
        """Test that feed supports pagination"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/feed/?page=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
    
    def test_feed_orders_by_created_at_desc(self):
        """Test that feed orders posts by creation date descending"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        # Check that posts are ordered by created_at descending
        for i in range(len(results) - 1):
            current_post = Post.objects.get(id=results[i]['id'])
            next_post = Post.objects.get(id=results[i + 1]['id'])
            self.assertGreaterEqual(current_post.created_at, next_post.created_at)
    
    def test_feed_excludes_inactive_posts(self):
        """Test that feed excludes inactive posts"""
        # Deactivate a post
        self.post2.is_active = False
        self.post2.save()
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        post_ids = [post['id'] for post in response.data['results']]
        self.assertNotIn(self.post2.id, post_ids)  # Inactive post should not appear
