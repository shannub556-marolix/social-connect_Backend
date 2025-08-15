from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from posts.models import Post
from engagement.models import Like, Comment
from users.models import Follow
from .models import Notification

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
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
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content',
            category='general'
        )
    
    def test_follow_notification_creation(self):
        """Test creating follow notification"""
        follow = Follow.objects.create(follower=self.user2, following=self.user1)
        notification = Notification.create_follow_notification(follow)
        
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.notification_type, 'follow')
        self.assertEqual(notification.follow, follow)
        self.assertFalse(notification.is_read)
        self.assertIn(self.user2.username, notification.title)
    
    def test_like_notification_creation(self):
        """Test creating like notification"""
        like = Like.objects.create(user=self.user2, post=self.post)
        notification = Notification.create_like_notification(like)
        
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.notification_type, 'like')
        self.assertEqual(notification.like, like)
        self.assertEqual(notification.post, self.post)
        self.assertFalse(notification.is_read)
        self.assertIn(self.user2.username, notification.title)
    
    def test_comment_notification_creation(self):
        """Test creating comment notification"""
        comment = Comment.objects.create(
            user=self.user2, 
            post=self.post, 
            content='Great post!'
        )
        notification = Notification.create_comment_notification(comment)
        
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.notification_type, 'comment')
        self.assertEqual(notification.comment, comment)
        self.assertEqual(notification.post, self.post)
        self.assertFalse(notification.is_read)
        self.assertIn(self.user2.username, notification.title)
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        follow = Follow.objects.create(follower=self.user2, following=self.user1)
        notification = Notification.create_follow_notification(follow)
        
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
    
    def test_notification_data_property(self):
        """Test notification_data property"""
        follow = Follow.objects.create(follower=self.user2, following=self.user1)
        notification = Notification.create_follow_notification(follow)
        
        data = notification.notification_data
        self.assertEqual(data['id'], notification.id)
        self.assertEqual(data['type'], 'follow')
        self.assertEqual(data['is_read'], False)
        self.assertIn('sender', data)
        self.assertEqual(data['sender']['username'], self.user2.username)

class NotificationSignalsTest(TestCase):
    def setUp(self):
        """Set up test data"""
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
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content',
            category='general'
        )
    
    def test_follow_signal_creates_notification(self):
        """Test that follow signal creates notification"""
        follow = Follow.objects.create(follower=self.user2, following=self.user1)
        
        # Check that notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.follow, follow)
    
    def test_like_signal_creates_notification(self):
        """Test that like signal creates notification"""
        like = Like.objects.create(user=self.user2, post=self.post)
        
        # Check that notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.like, like)
    
    def test_comment_signal_creates_notification(self):
        """Test that comment signal creates notification"""
        comment = Comment.objects.create(
            user=self.user2, 
            post=self.post, 
            content='Great post!'
        )
        
        # Check that notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='comment'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.comment, comment)
    
    def test_self_follow_no_notification(self):
        """Test that following yourself doesn't create notification"""
        follow = Follow.objects.create(follower=self.user1, following=self.user1)
        
        # Check that no notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user1,
            notification_type='follow'
        ).first()
        
        self.assertIsNone(notification)
    
    def test_self_like_no_notification(self):
        """Test that liking your own post doesn't create notification"""
        like = Like.objects.create(user=self.user1, post=self.post)
        
        # Check that no notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user1,
            notification_type='like'
        ).first()
        
        self.assertIsNone(notification)
    
    def test_self_comment_no_notification(self):
        """Test that commenting on your own post doesn't create notification"""
        comment = Comment.objects.create(
            user=self.user1, 
            post=self.post, 
            content='My own comment!'
        )
        
        # Check that no notification was created
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user1,
            notification_type='comment'
        ).first()
        
        self.assertIsNone(notification)

class NotificationAPITest(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
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
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content',
            category='general'
        )
        
        # Create some notifications
        self.follow = Follow.objects.create(follower=self.user2, following=self.user1)
        self.like = Like.objects.create(user=self.user2, post=self.post)
        self.comment = Comment.objects.create(
            user=self.user2, 
            post=self.post, 
            content='Great post!'
        )
    
    def test_list_notifications_requires_auth(self):
        """Test that listing notifications requires authentication"""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_notifications(self):
        """Test listing notifications"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should have 3 notifications (follow, like, comment)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check that notifications are ordered by created_at descending
        notifications = response.data['results']
        self.assertEqual(notifications[0]['notification_type'], 'comment')
        self.assertEqual(notifications[1]['notification_type'], 'like')
        self.assertEqual(notifications[2]['notification_type'], 'follow')
    
    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        self.client.force_authenticate(user=self.user1)
        
        # Get a notification
        notification = Notification.objects.filter(recipient=self.user1).first()
        
        response = self.client.post(f'/api/notifications/{notification.id}/read/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        
        # Check that notification is marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post('/api/notifications/mark-all-read/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('marked_count', response.data)
        self.assertEqual(response.data['marked_count'], 3)
        
        # Check that all notifications are marked as read
        unread_count = Notification.objects.filter(
            recipient=self.user1, 
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)
    
    def test_get_notification_count(self):
        """Test getting notification counts"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/notifications/count/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 3)
        self.assertEqual(response.data['total_count'], 3)
    
    def test_cannot_mark_others_notifications(self):
        """Test that users cannot mark others' notifications as read"""
        self.client.force_authenticate(user=self.user2)
        
        # Get a notification that belongs to user1
        notification = Notification.objects.filter(recipient=self.user1).first()
        
        response = self.client.post(f'/api/notifications/{notification.id}/read/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_notification_pagination(self):
        """Test notification pagination"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/notifications/?page=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
