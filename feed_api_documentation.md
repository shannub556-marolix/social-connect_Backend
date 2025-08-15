# Feed API Documentation

## Overview
The Feed API provides personalized post feeds for authenticated users, showing posts from users they follow plus their own posts.

## Base URL
```
/api/feed/
```

## Authentication
All feed endpoints require JWT authentication. Include the Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### GET /api/feed/
Retrieve the personalized feed for the authenticated user.

**Method:** GET  
**Authentication:** Required  
**Permissions:** Authenticated users only

#### Query Parameters
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of posts per page (default: 20, max: 50)

#### Response Format
```json
{
    "count": 45,
    "next": "http://localhost:8000/api/feed/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "This is a post content...",
            "image_url": "https://example.com/image.jpg",
            "category": "technology",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "author_username": "john_doe",
            "author_avatar": "https://example.com/avatar.jpg",
            "like_count": 5,
            "comment_count": 3,
            "is_liked_by_user": true
        }
    ]
}
```

#### Response Fields
- `count`: Total number of posts in the feed
- `next`: URL for the next page (null if no next page)
- `previous`: URL for the previous page (null if no previous page)
- `results`: Array of post objects

#### Post Object Fields
- `id`: Unique post identifier
- `content`: Post text content
- `image_url`: URL of attached image (null if no image)
- `category`: Post category (general, technology, lifestyle, etc.)
- `created_at`: Post creation timestamp
- `updated_at`: Last update timestamp
- `author_username`: Username of post author
- `author_avatar`: Avatar URL of post author
- `like_count`: Number of likes on the post
- `comment_count`: Number of comments on the post
- `is_liked_by_user`: Boolean indicating if current user liked this post

#### Feed Logic
The feed includes posts from:
1. Users that the authenticated user follows
2. The authenticated user's own posts

Posts are ordered by creation date (newest first) and only active posts are included.

#### Error Responses

**401 Unauthorized**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**500 Internal Server Error**
```json
{
    "detail": "Error fetching feed: <error_message>"
}
```

## Example Usage

### cURL
```bash
curl -X GET \
  http://localhost:8000/api/feed/ \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -H 'Content-Type: application/json'
```

### JavaScript (Fetch API)
```javascript
const response = await fetch('/api/feed/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});

const data = await response.json();
console.log(data.results); // Array of posts
```

### Python (requests)
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/feed/', headers=headers)
data = response.json()
posts = data['results']
```

## Pagination
The feed supports pagination with the following parameters:
- Default page size: 20 posts
- Maximum page size: 50 posts
- Page numbers start from 1

Example pagination URLs:
- First page: `/api/feed/`
- Second page: `/api/feed/?page=2`
- Custom page size: `/api/feed/?page_size=10`

## Performance Considerations
- The API uses `select_related` and `prefetch_related` for optimal database queries
- Posts are filtered by active status and author relationships
- Engagement data (likes/comments) is efficiently loaded in a single query
- Pagination helps manage large datasets

## Testing
Run the feed tests with:
```bash
python manage.py test feed.tests
```

## Integration Notes
- The feed integrates with existing User, Post, Like, and Comment models
- Follow relationships are managed through the Follow model in the users app
- The feed respects user privacy settings and post visibility
- All engagement data is real-time and reflects current state
