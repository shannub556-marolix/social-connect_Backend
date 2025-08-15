# Posts System Documentation

## 📋 Overview

The Posts system provides comprehensive post management functionality including creating, reading, updating, and deleting posts with optional image uploads. The system supports categories, pagination, search, and filtering capabilities.

## 🏗️ Architecture

### Models
- **Post**: Main post model with content, author, image, category, and metadata
- **User**: Extended user model with posts relationship

### Key Features
- Post CRUD operations (Create, Read, Update, Delete)
- Image upload with Supabase Storage integration
- Category-based organization
- Pagination and search functionality
- Soft delete (is_active flag)
- Author-based permissions

## 🔐 API Endpoints

### 1. Post Management

#### Create Post
```
POST /api/posts/create/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```
**Description**: Create a new post with optional image upload

**Request Body (Form Data)**:
```
content: "Your post content here"
category: "technology" (optional, default: "general")
image: [file upload - JPEG/PNG, max 5MB] (optional)
```

**Response (201 Created)**:
```json
{
    "id": 1,
    "content": "Your post content here",
    "author": {
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
    "image_url": "https://supabase-url/storage/v1/object/public/posts/1/uuid-filename.jpg",
    "category": "technology",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_active": true,
    "like_count": 0,
    "comment_count": 0
}
```

#### Get Post by ID
```
GET /api/posts/{post_id}/
```
**Description**: Retrieve a specific post by ID

**Response (200 OK)**:
```json
{
    "id": 1,
    "content": "Your post content here",
    "author": {
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
    "image_url": "https://supabase-url/storage/v1/object/public/posts/1/uuid-filename.jpg",
    "category": "technology",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_active": true,
    "like_count": 0,
    "comment_count": 0
}
```

#### Update Post
```
PUT /api/posts/{post_id}/
PATCH /api/posts/{post_id}/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```
**Description**: Update own post (content, category, image)

**Request Body (Form Data)**:
```
content: "Updated post content"
category: "lifestyle" (optional)
image: [file upload - JPEG/PNG, max 5MB] (optional)
```

**Response (200 OK)**: Returns updated post object

**Error Responses**:
- `403 Forbidden`: "You can only edit your own posts."
- `404 Not Found`: "Post not found."

#### Delete Post
```
DELETE /api/posts/{post_id}/
Authorization: Bearer <access_token>
```
**Description**: Delete own post (soft delete)

**Response (204 No Content)**:
```json
{
    "detail": "Post deleted successfully."
}
```

**Error Responses**:
- `403 Forbidden`: "You can only delete your own posts."
- `404 Not Found`: "Post not found."

### 2. Post Discovery

#### List Posts (Public)
```
GET /api/posts/
```
**Description**: List all public posts with pagination and filtering

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `category`: Filter by category
- `author`: Filter by author ID
- `search`: Search in content and author username

**Response (200 OK)**:
```json
{
    "count": 25,
    "next": "http://127.0.0.1:8000/api/posts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "Your post content here",
            "author": {
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
            "image_url": "https://supabase-url/storage/v1/object/public/posts/1/uuid-filename.jpg",
            "category": "technology",
            "created_at": "2024-01-15T10:30:00Z",
            "like_count": 0,
            "comment_count": 0
        }
    ]
}
```

#### Get My Posts
```
GET /api/posts/my/
Authorization: Bearer <access_token>
```
**Description**: Get current user's posts

**Response (200 OK)**: Same paginated format as list posts

## 🗄️ Database Models

### Post Model
```python
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('technology', 'Technology'),
        ('lifestyle', 'Lifestyle'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('sports', 'Sports'),
        ('entertainment', 'Entertainment'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    def can_edit(self, user):
        return user == self.author
    
    def can_delete(self, user):
        return user == self.author
```

## 🛠️ Implementation Details

### Image Upload System
- **Storage**: Supabase Storage with S3-compatible API
- **File Validation**: Size (max 5MB), format (JPEG/PNG), content validation
- **File Naming**: `posts/{post_id}/{uuid}.{extension}`
- **Error Handling**: Comprehensive validation and upload error handling

### Environment Variables Required
```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=posts
```

### Supabase Storage Setup
1. Create storage bucket named `posts`
2. Configure RLS policies or disable RLS for testing
3. Set bucket to public (optional, for direct image access)

### Pagination
- **Default page size**: 10 posts per page
- **Maximum page size**: 100 posts per page
- **Query parameter**: `page_size` to customize

### Search and Filtering
- **Search**: Content and author username (case-insensitive)
- **Category filter**: Filter by post category
- **Author filter**: Filter by specific author ID
- **Combined filters**: Multiple filters can be applied together

## 🔧 Error Handling

### Common Error Responses
- **400 Bad Request**: Validation errors, file upload issues
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Permission denied (editing/deleting others' posts)
- **404 Not Found**: Post doesn't exist
- **500 Internal Server Error**: Server-side issues

### Error Response Format
```json
{
    "detail": "Human-readable error message"
}
```

## 📊 Performance Considerations

### Database Optimization
- Indexes on frequently queried fields (author, category, created_at)
- Efficient pagination with proper ordering
- Computed properties for counts

### File Upload Optimization
- Memory-based upload handling for small files
- Temporary file handling for larger files
- Async upload processing (future enhancement)

## 🔮 Future Enhancements

### Planned Features
1. **Like System**: Post likes and reactions
2. **Comment System**: Post comments and replies
3. **Post Sharing**: Share posts with other users
4. **Post Scheduling**: Schedule posts for future publication
5. **Post Analytics**: View counts, engagement metrics
6. **Post Templates**: Predefined post templates
7. **Hashtag System**: Tag-based post organization

### Technical Improvements
1. **Caching**: Redis-based caching for popular posts
2. **CDN Integration**: Global image delivery
3. **Real-time Updates**: WebSocket integration for live post updates
4. **Search Enhancement**: Full-text search with Elasticsearch
5. **Image Processing**: Automatic image optimization and resizing

## 🧪 Testing

### Manual Testing Checklist
- [ ] Post creation (with and without images)
- [ ] Post retrieval by ID
- [ ] Post updates (content, category, image)
- [ ] Post deletion (soft delete)
- [ ] Post listing with pagination
- [ ] Search functionality
- [ ] Category filtering
- [ ] Author filtering
- [ ] Image upload validation
- [ ] Permission checks (edit/delete own posts only)
- [ ] Error handling scenarios

### API Testing Tools
- Postman collections available
- Comprehensive error logging
- Debug endpoints for troubleshooting

## 📚 Related Documentation
- User Profiles Module Documentation
- Authentication Module Documentation
- Supabase Integration Guide
- API Error Codes Reference
- Frontend Integration Guide

## 🚀 Quick Start

### 1. Environment Setup
```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=posts
```

### 2. Database Migration
```bash
python manage.py makemigrations posts
python manage.py migrate
```

### 3. Test Endpoints
```bash
# Create a post
curl -X POST http://127.0.0.1:8000/api/posts/create/ \
  -H "Authorization: Bearer <your_token>" \
  -F "content=Hello World!" \
  -F "category=general"

# List posts
curl http://127.0.0.1:8000/api/posts/

# Get specific post
curl http://127.0.0.1:8000/api/posts/1/
```

## 📝 Notes

1. **Image Upload**: Uses Supabase Storage with the same pattern as avatar uploads
2. **Soft Delete**: Posts are marked as inactive rather than physically deleted
3. **Permissions**: Users can only edit/delete their own posts
4. **Categories**: Predefined categories for better organization
5. **Pagination**: Efficient pagination for large post lists
6. **Search**: Basic search functionality in content and author names
