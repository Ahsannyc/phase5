# Todo App API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000` (development) | `https://api.example.com` (production)
**Authentication**: JWT Bearer Token

## Overview

The Todo App API is a RESTful API built with FastAPI that provides:
- User authentication and authorization
- Task management (CRUD operations)
- AI-powered chat interface for natural language task management
- Conversation management for chat history

## Quick Links

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Auth Endpoints](#auth-endpoints)
  - [Task Endpoints](#task-endpoints)
  - [Chat Endpoints](#chat-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Authentication

### JWT Token Flow

1. **Signup**: Create new account → receive JWT token
2. **Login**: Submit credentials → receive JWT token
3. **Use Token**: Include in Authorization header for protected endpoints

### Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- Access tokens expire after 24 hours
- Refresh tokens valid for 7 days
- Expired tokens return `401 Unauthorized`

---

## Endpoints

### Auth Endpoints

#### POST /api/auth/signup

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-02-08T10:00:00Z",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `400 Bad Request`: Invalid email or weak password
- `409 Conflict`: Email already registered

---

#### POST /api/auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials

---

#### POST /api/auth/refresh

Refresh expired access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### POST /api/auth/logout

Logout user (invalidates token).

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

### Task Endpoints

#### GET /api/tasks

List all tasks for authenticated user.

**Query Parameters:**
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Number of tasks to return (default: 10, max: 100)
- `completed` (bool): Filter by completion status (optional)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Complete project",
    "description": "Finish Phase 4 deployment",
    "completed": true,
    "created_at": "2026-02-07T15:30:00Z",
    "updated_at": "2026-02-08T09:45:00Z"
  }
]
```

**Authentication**: Required (Bearer token)
**Errors:**
- `401 Unauthorized`: Missing or invalid token

---

#### POST /api/tasks

Create a new task.

**Request:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

**Response** (201 Created):
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-08T10:15:00Z",
  "updated_at": "2026-02-08T10:15:00Z"
}
```

**Errors:**
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Invalid token

---

#### GET /api/tasks/{task_id}

Get specific task by ID.

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:00:00Z"
}
```

**Errors:**
- `404 Not Found`: Task doesn't exist or doesn't belong to user
- `401 Unauthorized`: Invalid token

---

#### PUT /api/tasks/{task_id}

Update a task.

**Request:**
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": true
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": true,
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:20:00Z"
}
```

**Errors:**
- `404 Not Found`: Task doesn't exist
- `401 Unauthorized`: Invalid token

---

#### DELETE /api/tasks/{task_id}

Delete a task.

**Response** (204 No Content):
```
(empty response body)
```

**Errors:**
- `404 Not Found`: Task doesn't exist
- `401 Unauthorized`: Invalid token

---

### Chat Endpoints

#### POST /api/chat/send

Send message to AI chatbot and receive response.

**Request:**
```json
{
  "content": "create a task to buy groceries",
  "conversation_id": null
}
```

**Response** (200 OK):
```json
{
  "conversation_id": 1,
  "message_id": 1,
  "content": "✅ Task added: 'buy groceries' (ID: 3)",
  "role": "assistant"
}
```

**Features:**
- Natural language task management
- Conversation history tracking
- Intent parsing (add task, list tasks, complete task, etc.)
- LLM fallback for general conversation

**Errors:**
- `400 Bad Request`: Empty message
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Conversation doesn't exist

---

#### GET /api/chat/conversations

List all conversations for authenticated user.

**Query Parameters:**
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Number of conversations to return (default: 50)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": null,
    "created_at": "2026-02-08T10:15:00Z"
  },
  {
    "id": 2,
    "title": "Daily Tasks Discussion",
    "created_at": "2026-02-08T09:30:00Z"
  }
]
```

**Authentication**: Required
**Errors:**
- `401 Unauthorized`: Invalid token

---

#### GET /api/chat/conversations/{conversation_id}/messages

Get all messages in a conversation.

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "role": "user",
    "content": "create a task to buy groceries",
    "created_at": "2026-02-08T10:15:00Z",
    "tool_calls": null
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "✅ Task added: 'buy groceries' (ID: 3)",
    "created_at": "2026-02-08T10:15:05Z",
    "tool_calls": null
  }
]
```

**Authentication**: Required
**Errors:**
- `404 Not Found`: Conversation doesn't exist or doesn't belong to user
- `401 Unauthorized`: Invalid token

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error description",
  "status_code": 400,
  "error_code": "INVALID_REQUEST"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error - Server error |

---

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Max requests
  - `X-RateLimit-Remaining`: Requests left
  - `X-RateLimit-Reset`: Reset timestamp

---

## Examples

### Example 1: Create Task via Chat

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }' | jq -r .access_token)

# 2. Send chat message
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "content": "add task call dentist tomorrow at 2pm"
  }' | jq .

# Expected response:
# {
#   "conversation_id": 1,
#   "message_id": 1,
#   "content": "✅ Task added: 'call dentist tomorrow at 2pm' (ID: 4)",
#   "role": "assistant"
# }
```

### Example 2: List Tasks

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks | jq .
```

### Example 3: Complete Task

```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "completed": true
  }' | jq .
```

### Example 3: Interactive Swagger UI

```
Open http://localhost:8000/docs in browser
- Try out endpoints interactively
- View request/response schemas
- Test with real data
```

---

## Webhooks (Coming Soon)

Subscribe to events:
- Task created
- Task completed
- Task deleted
- User invited

---

## SDK Libraries

### Python
```python
from todo_client import TodoClient

client = TodoClient(base_url="http://localhost:8000", token=access_token)
tasks = client.tasks.list()
task = client.tasks.create(title="New task")
```

### JavaScript/TypeScript
```typescript
import { TodoClient } from 'todo-client';

const client = new TodoClient({
  baseURL: 'http://localhost:8000',
  token: accessToken
});

const tasks = await client.tasks.list();
const task = await client.tasks.create({ title: 'New task' });
```

---

## Support

- **Issues**: https://github.com/your-org/todo-app/issues
- **Discussions**: https://github.com/your-org/todo-app/discussions
- **Email**: support@example.com

---

## Changelog

### v1.0.0 (2026-02-08)
- Initial release
- Authentication (signup/login)
- Task CRUD operations
- Chat API with NLP intent parsing
- Conversation management

