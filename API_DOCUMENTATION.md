# INSTACLONE API Documentation

This document describes the REST API endpoints available for the Instagram clone project built with Django Rest Framework.

## Base URL

All API endpoints are available under:
```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Authentication Headers
For authenticated requests, include the JWT token in the Authorization header:
```
Authorization: Bearer <your-access-token>
```

## User Endpoints (`/api/users/`)

### Authentication

#### Register a new user
```
POST /api/users/register/
```

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2023-12-20T10:30:00Z"
}
```

#### Login
```
POST /api/users/login/
```

**Request Body:**
```json
{
    "username": "newuser",
    "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "profile": {
            "bio": "",
            "profile_picture": null,
            "followers_count": 0,
            "following_count": 0
        }
    }
}
```

#### Refresh Token
```
POST /api/users/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Profiles

#### Get current user profile
```
GET /api/users/profiles/me/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
        "bio": "My bio here",
        "profile_picture": "/media/profiles/profile.jpg",
        "website": "https://example.com",
        "phone": "+1234567890"
    },
    "followers_count": 10,
    "following_count": 5,
    "posts_count": 3,
    "is_following": false
}
```

#### Update current user profile
```
PUT /api/users/profiles/update_me/
PATCH /api/users/profiles/update_me/
```

**Request Body:**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    "bio": "Updated bio",
    "website": "https://newwebsite.com"
}
```

#### Get specific user profile
```
GET /api/users/profiles/{username}/
```

#### Change Password
```
POST /api/users/profiles/change_password/
```

**Request Body:**
```json
{
    "old_password": "oldpassword",
    "new_password": "newsecurepassword"
}
```

### Follow System

#### Follow a user
```
POST /api/users/profiles/{username}/follow/
```

**Response (200 OK):**
```json
{
    "message": "Successfully followed username",
    "is_following": true,
    "followers_count": 11
}
```

#### Unfollow a user
```
DELETE /api/users/profiles/{username}/unfollow/
```

**Response (200 OK):**
```json
{
    "message": "Successfully unfollowed username",
    "is_following": false,
    "followers_count": 10
}
```

#### Get user's followers
```
GET /api/users/profiles/{username}/followers/
```

#### Get users that user is following
```
GET /api/users/profiles/{username}/following/
```

### Search & Discovery

#### Search users
```
GET /api/users/search/?q={search_term}
```

**Response (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "full_name": "John Doe",
            "profile_picture": "/media/profiles/john.jpg",
            "is_following": false
        }
    ]
}
```

#### Get suggested users
```
GET /api/users/suggested/
```

### User Statistics

#### Get current user stats
```
GET /api/users/stats/
```

#### Get specific user stats
```
GET /api/users/stats/{username}/
```

**Response (200 OK):**
```json
{
    "posts_count": 15,
    "followers_count": 100,
    "following_count": 50,
    "total_likes_received": 250,
    "total_comments_received": 75
}
```

## Post Endpoints (`/api/posts/`)

### Post Management

#### Create a new post
```
POST /api/posts/posts/
```

**Request Body (multipart/form-data):**
```
image: [file]
caption: "My new post caption"
```

**Response (201 Created):**
```json
{
    "id": 1,
    "user": {
        "username": "john_doe",
        "profile_picture": "/media/profiles/john.jpg"
    },
    "image": "/media/posts/image.jpg",
    "caption": "My new post caption",
    "created_at": "2023-12-20T10:30:00Z",
    "likes_count": 0,
    "comments_count": 0,
    "is_liked": false,
    "comments": []
}
```

#### Get all posts (paginated)
```
GET /api/posts/posts/
```

#### Get specific post
```
GET /api/posts/posts/{post_id}/
```

#### Update post (owner only)
```
PUT /api/posts/posts/{post_id}/
PATCH /api/posts/posts/{post_id}/
```

#### Delete post (owner only)
```
DELETE /api/posts/posts/{post_id}/
```

### Post Interactions

#### Like/Unlike a post
```
POST /api/posts/posts/{post_id}/like/
```

**Response (200 OK):**
```json
{
    "message": "Post liked",
    "is_liked": true,
    "likes_count": 15
}
```

#### Add comment to post
```
POST /api/posts/posts/{post_id}/comment/
```

**Request Body:**
```json
{
    "text": "Great post!"
}
```

#### Get post comments
```
GET /api/posts/posts/{post_id}/comments/
```

### Comments Management

#### Update comment (owner only)
```
PUT /api/posts/comments/{comment_id}/
PATCH /api/posts/comments/{comment_id}/
```

#### Delete comment (owner only)
```
DELETE /api/posts/comments/{comment_id}/
```

### Feed & Discovery

#### Get user feed
```
GET /api/posts/feed/
```
Returns posts from users that the authenticated user follows.

#### Get explore posts
```
GET /api/posts/explore/
```
Returns popular/public posts for discovery.

#### Get posts by specific user
```
GET /api/posts/user/{username}/
```

### Search

#### Search posts and users
```
GET /api/posts/search/?q={search_term}
```

**Response (200 OK):**
```json
{
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "full_name": "John Doe",
            "profile_picture": "/media/profiles/john.jpg"
        }
    ],
    "posts": [
        {
            "id": 1,
            "image": "/media/posts/image.jpg",
            "caption": "Matching caption",
            "user": {
                "username": "jane_doe"
            }
        }
    ]
}
```

### Follow System (Posts App)

#### Follow a user
```
POST /api/posts/follows/
```

**Request Body:**
```json
{
    "following": 2
}
```

#### Get follow relationships
```
GET /api/posts/follows/
```

## Error Responses

### Authentication Errors
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Validation Errors
```json
{
    "field_name": [
        "This field is required."
    ]
}
```

### Permission Errors
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Not Found Errors
```json
{
    "detail": "Not found."
}
```

## Pagination

Most list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

**Response format:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/posts/posts/?page=3",
    "previous": "http://localhost:8000/api/posts/posts/?page=1",
    "results": [...]
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour

## CORS

Cross-Origin Resource Sharing (CORS) is configured to allow requests from:
- `http://localhost:3000` (for React development)
- `http://127.0.0.1:3000`
- Add your frontend URLs to `CORS_ALLOWED_ORIGINS` in settings.py

## Example Usage with JavaScript

### Login and get token
```javascript
const response = await fetch('http://localhost:8000/api/users/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});

const data = await response.json();
const accessToken = data.access;
```

### Make authenticated request
```javascript
const response = await fetch('http://localhost:8000/api/posts/feed/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
    }
});

const feedData = await response.json();
```

### Upload a post with image
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('caption', 'My caption');

const response = await fetch('http://localhost:8000/api/posts/posts/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
    },
    body: formData
});
```

## Testing with curl

### Register new user
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "password_confirm": "testpassword"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword"
  }'
```

### Get feed (with token)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/posts/feed/
```

This completes the comprehensive REST API for your Instagram clone project. The API provides full functionality for user management, posts, comments, likes, follows, and search features.