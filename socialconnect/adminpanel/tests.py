from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from posts.models import Post
from engagement.models import Like, Comment
from users.models import Follow
from .permissions import IsAdminUser

User = get_user_model()

class AdminPermissionsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.permission = IsAdminUser()
    
    def test_admin_user_has_permission(self):
        """Test that admin users have permission"""
        request = type('Request', (), {'user': self.admin_user})()
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_regular_user_no_permission(self):
        """Test that regular users don't have permission"""
        request = type('Request', (), {'user': self.regular_user})()
        self.assertFalse(self.permission.has_permission(request, None))
    
    def test_unauthenticated_user_no_permission(self):
        """Test that unauthenticated users don't have permission"""
        request = type('Request', (), {'user': None})()
        self.assertFalse(self.permission.has_permission(request, None))

class AdminUserManagementTest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create regular users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role='user'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
            role='user'
        )
        
        # Create posts for users
        self.post1 = Post.objects.create(
            author=self.user1,
            content='Test post by user1',
            category='general'
        )
        self.post2 = Post.objects.create(
            author=self.user2,
            content='Test post by user2',
            category='technology'
        )
    
    def test_list_users_requires_admin(self):
        """Test that listing users requires admin permission"""
        # Test without authentication
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_admin_success(self):
        """Test that admin can list users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)  # admin + 2 users
    
    def test_list_users_with_filters(self):
        """Test listing users with filters"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test role filter
        response = self.client.get('/api/admin/users/?role=user')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # only users
        
        # Test search filter
        response = self.client.get('/api/admin/users/?search=user1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # only user1
    
    def test_get_user_detail_requires_admin(self):
        """Test that getting user details requires admin permission"""
        # Test without authentication
        response = self.client.get(f'/api/admin/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/admin/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_detail_admin_success(self):
        """Test that admin can get user details"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/admin/users/{self.user1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        self.assertEqual(response.data['email'], 'user1@test.com')
        self.assertEqual(response.data['role'], 'user')
        self.assertIn('followers_count', response.data)
        self.assertIn('following_count', response.data)
        self.assertIn('posts_count', response.data)
    
    def test_update_user_requires_admin(self):
        """Test that updating users requires admin permission"""
        # Test without authentication
        response = self.client.put(f'/api/admin/users/{self.user1.id}/update/', {
            'is_active': False
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(f'/api/admin/users/{self.user1.id}/update/', {
            'is_active': False
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_user_admin_success(self):
        """Test that admin can update user status"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(f'/api/admin/users/{self.user1.id}/update/', {
            'is_active': False,
            'role': 'admin'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        
        # Check that user was updated
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)
        self.assertEqual(self.user1.role, 'admin')
    
    def test_admin_cannot_deactivate_self(self):
        """Test that admin cannot deactivate their own account"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(f'/api/admin/users/{self.admin_user.id}/update/', {
            'is_active': False
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot deactivate your own account', response.data['detail'])

class AdminPostManagementTest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create regular user
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role='user'
        )
        
        # Create posts
        self.post1 = Post.objects.create(
            author=self.user1,
            content='Test post 1',
            category='general'
        )
        self.post2 = Post.objects.create(
            author=self.user1,
            content='Test post 2',
            category='technology'
        )
    
    def test_list_posts_requires_admin(self):
        """Test that listing posts requires admin permission"""
        # Test without authentication
        response = self.client.get('/api/admin/posts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/admin/posts/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_posts_admin_success(self):
        """Test that admin can list posts"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_posts_with_filters(self):
        """Test listing posts with filters"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test category filter
        response = self.client.get('/api/admin/posts/?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search filter
        response = self.client.get('/api/admin/posts/?search=Test post 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_post_detail_requires_admin(self):
        """Test that getting post details requires admin permission"""
        # Test without authentication
        response = self.client.get(f'/api/admin/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/admin/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_post_detail_admin_success(self):
        """Test that admin can get post details"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/admin/posts/{self.post1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test post 1')
        self.assertEqual(response.data['author_username'], 'user1')
        self.assertEqual(response.data['category'], 'general')
    
    def test_delete_post_requires_admin(self):
        """Test that deleting posts requires admin permission"""
        # Test without authentication
        response = self.client.delete(f'/api/admin/posts/{self.post1.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/admin/posts/{self.post1.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_post_admin_success(self):
        """Test that admin can delete posts"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/admin/posts/{self.post1.id}/delete/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        
        # Check that post was soft deleted
        self.post1.refresh_from_db()
        self.assertFalse(self.post1.is_active)

class AdminStatsTest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Create regular users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            role='user'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
            role='user'
        )
        
        # Create posts
        self.post1 = Post.objects.create(
            author=self.user1,
            content='Test post 1',
            category='general'
        )
        self.post2 = Post.objects.create(
            author=self.user2,
            content='Test post 2',
            category='technology'
        )
        
        # Create engagement
        self.like = Like.objects.create(user=self.user2, post=self.post1)
        self.comment = Comment.objects.create(
            user=self.user2, 
            post=self.post1, 
            content='Great post!'
        )
    
    def test_get_stats_requires_admin(self):
        """Test that getting stats requires admin permission"""
        # Test without authentication
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with regular user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/admin/stats/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_stats_admin_success(self):
        """Test that admin can get statistics"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('total_posts', response.data)
        self.assertIn('active_users_today', response.data)
        self.assertIn('active_posts_today', response.data)
        self.assertIn('total_likes', response.data)
        self.assertIn('total_comments', response.data)
        self.assertIn('users_created_today', response.data)
        self.assertIn('posts_created_today', response.data)
        
        # Check specific values
        self.assertEqual(response.data['total_users'], 3)  # admin + 2 users
        self.assertEqual(response.data['total_posts'], 2)
        self.assertEqual(response.data['total_likes'], 1)
        self.assertEqual(response.data['total_comments'], 1)
