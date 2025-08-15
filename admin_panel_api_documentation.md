# Admin Panel API Documentation

## 📋 Overview

The Admin Panel API provides comprehensive administrative functionality for managing users, posts, and viewing platform statistics. All endpoints require admin-level authentication and are designed for platform administrators.

## 🏗️ Architecture

### Features
- **User Management**: List, view details, and manage user accounts
- **Post Management**: List, view details, and delete posts
- **Statistics**: Comprehensive platform analytics and metrics
- **Admin-Only Access**: Custom permission system for admin users

### Security
- **Role-Based Access**: Only users with `role='admin'` can access endpoints
- **JWT Authentication**: Secure token-based authentication
- **Permission Validation**: Custom permission classes for admin access

## 🔐 API Endpoints

### Base URL
```
/api/admin/
```

### Authentication
All endpoints require JWT authentication with admin role:
```
Authorization: Bearer <your_jwt_token>
```

**Note**: The user must have `role='admin'` in their profile to access these endpoints.

## 📡 Endpoints

### User Management

#### 1. List All Users

**GET** `/api/admin/users/`

Retrieve paginated list of all users in the system.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of users per page (default: 20, max: 100)
- `search` (optional): Search users by username, email, first_name, or last_name
- `role` (optional): Filter by user role ('user' or 'admin')
- `is_active` (optional): Filter by active status ('true' or 'false')

**Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/admin/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": true,
            "is_email_verified": true,
            "date_joined": "2024-01-15T10:30:00Z",
            "last_login": "2024-01-20T15:45:00Z",
            "followers_count": 25,
            "following_count": 18,
            "posts_count": 12,
            "privacy_setting": "public"
        }
    ]
}
```

#### 2. Get User Details

**GET** `/api/admin/users/{user_id}/`

Retrieve detailed information about a specific user.

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "is_email_verified": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T15:45:00Z",
    "bio": "Software developer passionate about technology",
    "avatar_url": "https://example.com/avatar.jpg",
    "website": "https://johndoe.dev",
    "location": "San Francisco, CA",
    "privacy_setting": "public",
    "followers_count": 25,
    "following_count": 18,
    "posts_count": 12,
    "total_likes_received": 156,
    "total_comments_received": 89
}
```

#### 3. Update User Status

**PUT** `/api/admin/users/{user_id}/update/`

Update user status (activate/deactivate) and role.

**Request Body:**
```json
{
    "is_active": false,
    "role": "admin"
}
```

**Response (200 OK):**
```json
{
    "detail": "User updated successfully.",
    "user": {
        // Updated user details
    }
}
```

**Error Responses:**
- `400 Bad Request`: Cannot deactivate own account
- `404 Not Found`: User not found

### Post Management

#### 1. List All Posts

**GET** `/api/admin/posts/`

Retrieve paginated list of all posts in the system.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of posts per page (default: 20, max: 100)
- `search` (optional): Search posts by content or author username/email
- `category` (optional): Filter by post category
- `is_active` (optional): Filter by active status ('true' or 'false')
- `author_id` (optional): Filter by specific author ID

**Response (200 OK):**
```json
{
    "count": 500,
    "next": "http://localhost:8000/api/admin/posts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "This is a great post about technology...",
            "author_username": "john_doe",
            "author_email": "john@example.com",
            "category": "technology",
            "image_url": "https://example.com/image.jpg",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "is_active": true,
            "like_count": 25,
            "comment_count": 8
        }
    ]
}
```

#### 2. Get Post Details

**GET** `/api/admin/posts/{post_id}/`

Retrieve detailed information about a specific post.

**Response (200 OK):**
```json
{
    "id": 1,
    "content": "This is a great post about technology and innovation...",
    "author_username": "john_doe",
    "author_email": "john@example.com",
    "category": "technology",
    "image_url": "https://example.com/image.jpg",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_active": true,
    "like_count": 25,
    "comment_count": 8
}
```

#### 3. Delete Post

**DELETE** `/api/admin/posts/{post_id}/delete/`

Delete a post (soft delete by setting is_active=False).

**Response (200 OK):**
```json
{
    "detail": "Post deleted successfully.",
    "post_id": 1
}
```

### Statistics

#### 1. Get Platform Statistics

**GET** `/api/admin/stats/`

Retrieve comprehensive platform statistics and metrics.

**Response (200 OK):**
```json
{
    "total_users": 150,
    "total_posts": 500,
    "active_users_today": 45,
    "active_posts_today": 23,
    "total_likes": 1250,
    "total_comments": 890,
    "users_created_today": 5,
    "posts_created_today": 12
}
```

**Statistics Explained:**
- `total_users`: Total number of registered users
- `total_posts`: Total number of active posts
- `active_users_today`: Users who logged in today
- `active_posts_today`: Posts created today
- `total_likes`: Total likes across all posts
- `total_comments`: Total comments across all posts
- `users_created_today`: New user registrations today
- `posts_created_today`: New posts created today

## 🔒 Security Features

### Admin Permission System
- **Custom Permission Class**: `IsAdminUser` ensures only admin users can access endpoints
- **Role Validation**: Checks user's `role` field equals 'admin'
- **Authentication Required**: All endpoints require valid JWT token
- **Self-Protection**: Admins cannot deactivate their own accounts

### Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
    "detail": "User not found."
}
```

**400 Bad Request:**
```json
{
    "detail": "You cannot deactivate your own account."
}
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Create admin user account
- [ ] Test admin authentication
- [ ] List all users with pagination
- [ ] Search and filter users
- [ ] Get user details
- [ ] Update user status (activate/deactivate)
- [ ] Change user role
- [ ] List all posts with pagination
- [ ] Search and filter posts
- [ ] Get post details
- [ ] Delete posts
- [ ] View platform statistics
- [ ] Test permission restrictions

### API Testing Examples

#### Create Admin User
```bash
# First, create a user and then update their role to admin via Django shell
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
user.role = 'admin'
user.save()
```

#### List Users
```bash
curl -X GET \
  http://localhost:8000/api/admin/users/ \
  -H "Authorization: Bearer <admin_jwt_token>"
```

#### Update User Status
```bash
curl -X PUT \
  http://localhost:8000/api/admin/users/1/update/ \
  -H "Authorization: Bearer <admin_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false, "role": "user"}'
```

#### List Posts
```bash
curl -X GET \
  http://localhost:8000/api/admin/posts/ \
  -H "Authorization: Bearer <admin_jwt_token>"
```

#### Delete Post
```bash
curl -X DELETE \
  http://localhost:8000/api/admin/posts/1/delete/ \
  -H "Authorization: Bearer <admin_jwt_token>"
```

#### Get Statistics
```bash
curl -X GET \
  http://localhost:8000/api/admin/stats/ \
  -H "Authorization: Bearer <admin_jwt_token>"
```

## 🔧 Configuration

### Environment Setup
No additional environment variables required beyond the standard Django configuration.

### Database Migration
```bash
python manage.py makemigrations adminpanel
python manage.py migrate
```

## 📈 Performance Considerations

- **Pagination**: Default 20 items per page, configurable up to 100
- **Optimized Queries**: Uses `select_related` and `prefetch_related` for efficient data loading
- **Search Indexing**: Database indexes on searchable fields
- **Caching Ready**: Statistics can be cached for better performance

## 🚀 Quick Start

### 1. Create Admin User
```bash
# Create a superuser or update existing user role
python manage.py createsuperuser
# Then update the role to 'admin' in Django shell
```

### 2. Test Admin Access
```bash
# Get JWT token for admin user
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### 3. Test Admin Endpoints
```bash
# List users
curl -X GET http://localhost:8000/api/admin/users/ \
  -H "Authorization: Bearer <admin_token>"

# Get statistics
curl -X GET http://localhost:8000/api/admin/stats/ \
  -H "Authorization: Bearer <admin_token>"
```

## 📝 Notes

1. **Admin Role Required**: All endpoints require user with `role='admin'`
2. **Soft Delete**: Post deletion uses soft delete (sets `is_active=False`)
3. **Self-Protection**: Admins cannot deactivate their own accounts
4. **Comprehensive Statistics**: Real-time platform metrics and analytics
5. **Search & Filtering**: Advanced filtering capabilities for users and posts
6. **Pagination**: Efficient pagination for large datasets
7. **Error Handling**: Comprehensive error responses and validation
8. **Security**: Role-based access control with JWT authentication
9. **Performance**: Optimized queries and database indexing
10. **Testing**: Complete test coverage for all functionality
