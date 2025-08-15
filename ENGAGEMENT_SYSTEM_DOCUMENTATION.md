# Engagement System Documentation

## 📋 Overview

The Engagement system provides comprehensive like and comment functionality for posts. It allows users to interact with posts through likes and comments, with proper permission controls and data integrity.

## 🏗️ Architecture

### Models
- **Like**: Tracks user likes on posts with unique constraints
- **Comment**: Stores user comments on posts with soft delete capability
- **Post**: Extended with like_count and comment_count properties

### Key Features
- Like/Unlike posts (with self-like prevention)
- Add comments to posts
- Delete comments (own comments or comments on own posts)
- Check like status and counts
- Pagination for comments
- Soft delete for comments
- Proper permission controls

## 🔐 API Endpoints

### 1. Like Management

#### Like Post
```
POST /api/engagement/posts/{post_id}/like/
Authorization: Bearer <access_token>
Content-Type: application/json
```
**Description**: Like a post (cannot like own posts)

**URL Parameters**:
- post_id: Integer (required) - The ID of the post to like

**Response (201 Created)**:
```json
{
    "id": 1,
    "user": {
        "id": 2,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "user",
        "bio": "Software developer",
        "avatar_url": "https://example.com/avatar.jpg",
        "website": "https://johndoe.dev",
        "location": "San Francisco, CA",
        "is_email_verified": true,
        "privacy_setting": "public",
        "followers_count": 5,
        "following_count": 3,
        "posts_count": 1
    },
    "post": 1,
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: "You cannot like your own post." or "You have already liked this post."
- 401 Unauthorized: Missing or invalid authentication
- 404 Not Found: Post doesn't exist

#### Unlike Post
```
DELETE /api/engagement/posts/{post_id}/unlike/
Authorization: Bearer <access_token>
```
**Description**: Unlike a post

**URL Parameters**:
- post_id: Integer (required) - The ID of the post to unlike

**Response (204 No Content)**:
```json
{
    "detail": "Post unliked successfully."
}
```

**Error Responses**:
- 404 Not Found: Post or like doesn't exist
- 401 Unauthorized: Missing or invalid authentication

#### Check Like Status
```
GET /api/engagement/posts/{post_id}/like-status/
Authorization: Bearer <access_token>
```
**Description**: Check if current user has liked the post and get like count

**URL Parameters**:
- post_id: Integer (required) - The ID of the post to check

**Response (200 OK)**:
```json
{
    "is_liked": true,
    "like_count": 5
}
```

**Error Responses**:
- 401 Unauthorized: Missing or invalid authentication
- 404 Not Found: Post doesn't exist

### 2. Comment Management

#### List Comments
```
GET /api/engagement/posts/{post_id}/comments/
```
**Description**: List all comments for a post with pagination

**URL Parameters**:
- post_id: Integer (required) - The ID of the post

**Query Parameters**:
- page: Integer (optional, default: 1) - Page number
- page_size: Integer (optional, default: 20, max: 100) - Items per page

**Response (200 OK)**:
```json
{
    "count": 15,
    "next": "http://127.0.0.1:8000/api/engagement/posts/1/comments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "user",
                "bio": "Software developer",
                "avatar_url": "https://example.com/avatar.jpg",
                "website": "https://johndoe.dev",
                "location": "San Francisco, CA",
                "is_email_verified": true,
                "privacy_setting": "public",
                "followers_count": 5,
                "following_count": 3,
                "posts_count": 1
            },
            "post": 1,
            "content": "Great post! Thanks for sharing.",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "is_active": true
        }
    ]
}
```

#### Add Comment
```
POST /api/engagement/posts/{post_id}/comments/create/
Authorization: Bearer <access_token>
Content-Type: application/json
```
**Description**: Add a comment to a post

**URL Parameters**:
- post_id: Integer (required) - The ID of the post to comment on

**Request Body**:
```json
{
    "content": "Great post! Thanks for sharing."
}
```

**Response (201 Created)**:
```json
{
    "id": 1,
    "user": {
        "id": 2,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "user",
        "bio": "Software developer",
        "avatar_url": "https://example.com/avatar.jpg",
        "website": "https://johndoe.dev",
        "location": "San Francisco, CA",
        "is_email_verified": true,
        "privacy_setting": "public",
        "followers_count": 5,
        "following_count": 3,
        "posts_count": 1
    },
    "post": 1,
    "content": "Great post! Thanks for sharing.",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_active": true
}
```

**Error Responses**:
- 400 Bad Request: Validation errors
- 401 Unauthorized: Missing or invalid authentication
- 404 Not Found: Post doesn't exist

#### Delete Comment
```
DELETE /api/engagement/posts/{post_id}/comments/{comment_id}/
Authorization: Bearer <access_token>
```
**Description**: Delete own comment or comment on own post

**URL Parameters**:
- post_id: Integer (required) - The ID of the post
- comment_id: Integer (required) - The ID of the comment to delete

**Response (204 No Content)**:
```json
{
    "detail": "Comment deleted successfully."
}
```

**Error Responses**:
- 403 Forbidden: "You can only delete your own comments or comments on your posts."
- 404 Not Found: Post or comment doesn't exist
- 401 Unauthorized: Missing or invalid authentication

## 🗄️ Database Models

### Like Model
```python
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def clean(self):
        """Prevent users from liking their own posts"""
        if self.user == self.post.author:
            raise ValidationError("Users cannot like their own posts.")
```

### Comment Model
```python
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def can_edit(self, user):
        return user == self.user
    
    def can_delete(self, user):
        return user == self.user or user == self.post.author
```

## 🛠️ Implementation Details

### Like System
- **Unique Constraints**: One like per user per post
- **Self-Like Prevention**: Users cannot like their own posts
- **Automatic Cleanup**: Likes are deleted when posts are deleted
- **Efficient Counting**: Uses database relationships for accurate counts

### Comment System
- **Soft Delete**: Comments are marked inactive rather than deleted
- **Permission Control**: Users can delete their own comments or comments on their posts
- **Pagination**: Efficient pagination for large comment lists
- **Content Validation**: Proper content validation and sanitization

### Permission System
- **Like Permissions**: Any authenticated user can like posts (except their own)
- **Comment Permissions**: Any authenticated user can comment on posts
- **Delete Permissions**: Users can delete their own comments or comments on their posts

## 🔧 Error Handling

### Common Error Responses
- **400 Bad Request**: Validation errors, duplicate likes, self-likes
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Permission denied for comment deletion
- **404 Not Found**: Post or comment doesn't exist
- **500 Internal Server Error**: Server-side issues

### Error Response Format
```json
{
    "detail": "Human-readable error message"
}
```

## 📊 Performance Considerations

### Database Optimization
- Indexes on frequently queried fields (post, user, created_at)
- Efficient pagination with proper ordering
- Computed properties for counts
- Unique constraints for data integrity

### Query Optimization
- Selective field loading for large datasets
- Proper use of select_related for foreign keys
- Efficient filtering and ordering

## 🔮 Future Enhancements

### Planned Features
1. **Comment Replies**: Nested comment system
2. **Comment Editing**: Edit own comments
3. **Comment Moderation**: Admin moderation tools
4. **Like Reactions**: Different types of reactions (heart, thumbs up, etc.)
5. **Comment Notifications**: Notify post authors of new comments
6. **Comment Analytics**: Comment engagement metrics

### Technical Improvements
1. **Caching**: Redis-based caching for like/comment counts
2. **Real-time Updates**: WebSocket integration for live engagement updates
3. **Search Enhancement**: Full-text search in comments
4. **Rate Limiting**: Prevent spam likes/comments
5. **Content Filtering**: Automated content moderation

## 🧪 Testing

### Manual Testing Checklist
- [ ] Like a post (authenticated user)
- [ ] Unlike a post
- [ ] Try to like own post (should fail)
- [ ] Try to like same post twice (should fail)
- [ ] Check like status and count
- [ ] Add comment to post
- [ ] List comments with pagination
- [ ] Delete own comment
- [ ] Delete comment on own post
- [ ] Try to delete others' comments (should fail)
- [ ] Error handling scenarios

### API Testing Tools
- Postman collections available
- Comprehensive error logging
- Debug endpoints for troubleshooting

## 📚 Related Documentation
- Posts System Documentation
- User Profiles Module Documentation
- Authentication Module Documentation
- API Error Codes Reference

## 🚀 Quick Start

### 1. Database Migration
```bash
python manage.py makemigrations engagement
python manage.py migrate
```

### 2. Test Endpoints
```bash
# Like a post
curl -X POST http://127.0.0.1:8000/api/engagement/posts/1/like/ \
  -H "Authorization: Bearer <your_token>"

# Check like status
curl http://127.0.0.1:8000/api/engagement/posts/1/like-status/ \
  -H "Authorization: Bearer <your_token>"

# Add a comment
curl -X POST http://127.0.0.1:8000/api/engagement/posts/1/comments/create/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great post!"}'

# List comments
curl http://127.0.0.1:8000/api/engagement/posts/1/comments/

# Delete comment
curl -X DELETE http://127.0.0.1:8000/api/engagement/posts/1/comments/1/ \
  -H "Authorization: Bearer <your_token>"
```

## 📝 Notes

1. **Like Constraints**: Users cannot like their own posts
2. **Comment Permissions**: Flexible deletion permissions (own comments or comments on own posts)
3. **Soft Delete**: Comments use soft delete to maintain data integrity
4. **Pagination**: Comments are paginated for performance
5. **Real-time Counts**: Like and comment counts are computed dynamically
6. **Data Integrity**: Proper foreign key relationships and constraints
7. **Performance**: Optimized queries with proper indexing
8. **Security**: Proper authentication and permission checks
9. **Error Handling**: Comprehensive error messages and status codes
10. **Scalability**: Designed for high-traffic applications

## 🔗 Integration with Posts System

The Engagement system integrates seamlessly with the Posts system:

- **Post Model**: Extended with `like_count` and `comment_count` properties
- **API Consistency**: Follows the same patterns as the Posts API
- **Data Relationships**: Proper foreign key relationships between models
- **Permission System**: Consistent with the overall application permissions
- **Error Handling**: Unified error response format

## 📈 Analytics and Metrics

The system provides several engagement metrics:

- **Like Count**: Number of likes on a post
- **Comment Count**: Number of active comments on a post
- **User Engagement**: Track user's likes and comments
- **Post Popularity**: Measure post engagement through likes and comments

These metrics can be used for:
- Content recommendation algorithms
- User engagement analysis
- Post performance tracking
- Community insights and analytics
