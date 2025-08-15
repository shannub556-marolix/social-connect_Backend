# Notifications API Documentation

## 📋 Overview

The Notifications API provides real-time notification functionality for social interactions including follows, likes, and comments. The system automatically creates notifications when users interact with each other and provides endpoints to manage notification states.

## 🏗️ Architecture

### Models
- **Notification**: Core notification model with support for different types
- **Signals**: Automatic notification creation on Follow, Like, and Comment events
- **Supabase Realtime**: Real-time event publishing for instant notifications

### Notification Types
- **follow**: When someone follows a user
- **like**: When someone likes a post
- **comment**: When someone comments on a post

## 🔐 API Endpoints

### Base URL
```
/api/notifications/
```

### Authentication
All endpoints require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

## 📡 Endpoints

### 1. List Notifications

#### GET /api/notifications/
Retrieve paginated list of notifications for the authenticated user.

**Response (200 OK)**:
```json
{
    "count": 15,
    "next": "http://localhost:8000/api/notifications/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "notification_type": "like",
            "title": "john_doe liked your post",
            "message": "john_doe liked your post: This is a great post about...",
            "is_read": false,
            "created_at": "2024-01-15T10:30:00Z",
            "sender_username": "john_doe",
            "sender_avatar": "https://example.com/avatar.jpg",
            "notification_data": {
                "id": 1,
                "type": "like",
                "title": "john_doe liked your post",
                "message": "john_doe liked your post: This is a great post about...",
                "is_read": false,
                "created_at": "2024-01-15T10:30:00Z",
                "sender": {
                    "id": 2,
                    "username": "john_doe",
                    "avatar_url": "https://example.com/avatar.jpg"
                },
                "post": {
                    "id": 5,
                    "content": "This is a great post about technology and innovation..."
                }
            }
        }
    ]
}
```

#### Query Parameters
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of notifications per page (default: 20, max: 50)

### 2. Mark Notification as Read

#### POST /api/notifications/{id}/read/
Mark a specific notification as read.

**Response (200 OK)**:
```json
{
    "detail": "Notification marked as read successfully.",
    "notification_id": 1
}
```

**Error Responses**:
- `404 Not Found`: Notification not found or doesn't belong to user

### 3. Mark All Notifications as Read

#### POST /api/notifications/mark-all-read/
Mark all unread notifications as read for the authenticated user.

**Response (200 OK)**:
```json
{
    "detail": "Marked 5 notifications as read successfully.",
    "marked_count": 5
}
```

### 4. Get Notification Counts

#### GET /api/notifications/count/
Get unread and total notification counts for the authenticated user.

**Response (200 OK)**:
```json
{
    "unread_count": 3,
    "total_count": 15
}
```

## 🔔 Automatic Notification Creation

The system automatically creates notifications when certain events occur:

### Follow Notifications
- **Trigger**: When a user follows another user
- **Recipient**: The user being followed
- **Content**: "{follower_username} started following you"

### Like Notifications
- **Trigger**: When a user likes a post
- **Recipient**: The post author
- **Content**: "{user_username} liked your post: {post_content}..."
- **Note**: No notification if user likes their own post

### Comment Notifications
- **Trigger**: When a user comments on a post
- **Recipient**: The post author
- **Content**: "{user_username} commented: {comment_content}..."
- **Note**: No notification if user comments on their own post

## 🚀 Supabase Realtime Integration

The notifications system integrates with Supabase Realtime for instant updates:

### Event Structure
```json
{
    "type": "notification",
    "notification": {
        "id": 1,
        "type": "like",
        "title": "john_doe liked your post",
        "message": "john_doe liked your post: This is a great post...",
        "is_read": false,
        "created_at": "2024-01-15T10:30:00Z",
        "sender": {
            "id": 2,
            "username": "john_doe",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        "post": {
            "id": 5,
            "content": "This is a great post about technology..."
        }
    },
    "recipient_id": 1,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Channel Naming
Notifications are published to user-specific channels:
```
notifications:{user_id}
```

### Frontend Integration
```javascript
// Example frontend integration with Supabase Realtime
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subscribe to notifications channel
const channel = supabase
    .channel(`notifications:${userId}`)
    .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'notifications',
        filter: `recipient_id=eq.${userId}`
    }, (payload) => {
        console.log('New notification:', payload.new)
        // Handle new notification
    })
    .subscribe()
```

## 📊 Notification Data Structure

### Notification Object
```json
{
    "id": 1,
    "notification_type": "like|follow|comment",
    "title": "Notification title",
    "message": "Detailed notification message",
    "is_read": false,
    "created_at": "2024-01-15T10:30:00Z",
    "sender_username": "john_doe",
    "sender_avatar": "https://example.com/avatar.jpg",
    "notification_data": {
        // Structured data with type-specific information
    }
}
```

### Type-Specific Data

#### Follow Notifications
```json
{
    "notification_data": {
        "sender": {
            "id": 2,
            "username": "john_doe",
            "avatar_url": "https://example.com/avatar.jpg"
        }
    }
}
```

#### Like Notifications
```json
{
    "notification_data": {
        "sender": {
            "id": 2,
            "username": "john_doe",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        "post": {
            "id": 5,
            "content": "Post content preview..."
        }
    }
}
```

#### Comment Notifications
```json
{
    "notification_data": {
        "sender": {
            "id": 2,
            "username": "john_doe",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        "post": {
            "id": 5,
            "content": "Post content preview..."
        },
        "comment": {
            "id": 10,
            "content": "Comment content preview..."
        }
    }
}
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Follow a user (should create notification)
- [ ] Like a post (should create notification)
- [ ] Comment on a post (should create notification)
- [ ] List notifications (with pagination)
- [ ] Mark individual notification as read
- [ ] Mark all notifications as read
- [ ] Get notification counts
- [ ] Verify no self-notifications for own actions

### API Testing Examples

#### List Notifications
```bash
curl -X GET \
  http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer <your_token>"
```

#### Mark Notification as Read
```bash
curl -X POST \
  http://localhost:8000/api/notifications/1/read/ \
  -H "Authorization: Bearer <your_token>"
```

#### Mark All as Read
```bash
curl -X POST \
  http://localhost:8000/api/notifications/mark-all-read/ \
  -H "Authorization: Bearer <your_token>"
```

#### Get Counts
```bash
curl -X GET \
  http://localhost:8000/api/notifications/count/ \
  -H "Authorization: Bearer <your_token>"
```

## 🔧 Configuration

### Environment Variables
```bash
# Supabase Configuration (for realtime)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Database Migration
```bash
python manage.py makemigrations notifications
python manage.py migrate
```

## 📈 Performance Considerations

- **Indexing**: Optimized database indexes for fast queries
- **Pagination**: Default 20 notifications per page
- **Select Related**: Efficient database queries with related data
- **Signal Optimization**: Non-blocking notification creation
- **Real-time Events**: Asynchronous event publishing

## 🔒 Security Features

- **Authentication Required**: All endpoints require JWT authentication
- **User Isolation**: Users can only access their own notifications
- **Permission Checks**: Proper validation for notification ownership
- **Error Handling**: Comprehensive error responses and logging

## 🚀 Quick Start

### 1. Database Setup
```bash
python manage.py makemigrations notifications
python manage.py migrate
```

### 2. Test Notifications
```bash
# Create a follow relationship
curl -X POST http://localhost:8000/api/auth/follow/2/ \
  -H "Authorization: Bearer <your_token>"

# Check notifications
curl http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer <your_token>"
```

### 3. Frontend Integration
```javascript
// Subscribe to real-time notifications
const channel = supabase
    .channel(`notifications:${userId}`)
    .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'notifications',
        filter: `recipient_id=eq.${userId}`
    }, (payload) => {
        // Handle new notification
        showNotification(payload.new)
    })
    .subscribe()
```

## 📝 Notes

1. **Self-Actions**: No notifications are created for users' own actions
2. **Real-time**: Notifications are published to Supabase Realtime for instant updates
3. **Pagination**: Notifications are paginated for performance
4. **Data Integrity**: Proper foreign key relationships and constraints
5. **Performance**: Optimized queries with proper indexing
6. **Security**: Proper authentication and permission checks
7. **Error Handling**: Comprehensive error messages and status codes
8. **Scalability**: Designed for high-traffic applications
9. **Testing**: Comprehensive test coverage for all functionality
10. **Documentation**: Complete API documentation and examples
