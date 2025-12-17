# Phase III AI Chat Service API Reference

**Version**: 0.1.0
**Base URL**: `http://localhost:8000`

## Authentication

All endpoints (except `/health`, `/`, and `/docs`) require JWT authentication:

```http
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- Chat endpoint: 10 requests per minute per user
- Rate limit headers included in responses

---

## Endpoints

### Health & Status

#### `GET /`
Root endpoint providing API information.

**Response**: `200 OK`
```json
{
  "message": "Phase III AI Chat Service API",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`
Health check endpoint for monitoring.

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "phaseiii-backend",
  "version": "0.1.0",
  "environment": "development"
}
```

---

### Chat

#### `POST /api/{user_id}/chat`
Send a message to the AI assistant and receive a response.

**Authentication**: Required
**Rate Limit**: 10 requests/minute

**Path Parameters**:
- `user_id` (string, required): User ID from JWT token (must match token)

**Request Body**:
```json
{
  "message": "Show me my pending tasks",
  "conversation_id": 123  // optional - omit for new conversation
}
```

**Response**: `200 OK`
```json
{
  "conversation_id": 123,
  "response": "You have 3 pending tasks: 1) Buy groceries, 2) Call dentist, 3) Finish report",
  "tool_calls": [
    {
      "name": "list_tasks",
      "arguments": {"user_id": "user_123", "status": "pending"},
      "result": [...array of tasks...]
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid message content
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: user_id mismatch (path ≠ JWT)
- `404 Not Found`: Conversation not found
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: AI service temporarily unavailable

---

#### `GET /api/{user_id}/conversations/{conversation_id}`
Retrieve conversation history with all messages.

**Authentication**: Required

**Path Parameters**:
- `user_id` (string, required): User ID from JWT token
- `conversation_id` (integer, required): Conversation ID to retrieve

**Response**: `200 OK`
```json
{
  "conversation_id": 123,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Show my tasks",
      "created_at": "2025-12-17T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "You have 3 tasks...",
      "created_at": "2025-12-17T10:00:05Z"
    }
  ],
  "created_at": "2025-12-17T10:00:00Z",
  "updated_at": "2025-12-17T10:00:05Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: user_id mismatch or conversation access denied
- `404 Not Found`: Conversation not found

---

## MCP Tools (Internal)

The following tools are available to the AI assistant via MCP:

### `add_task`
Create a new task for the user.

**Parameters**:
- `user_id` (string): User ID
- `title` (string): Task title (1-200 characters)
- `description` (string, optional): Task description

**Returns**:
```json
{
  "status": "created",
  "task_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

---

### `list_tasks`
List user's tasks with optional filtering.

**Parameters**:
- `user_id` (string): User ID
- `status` (string, optional): Filter by "all", "pending", or "completed"

**Returns**: Array of tasks

---

### `complete_task`
Mark a task as completed.

**Parameters**:
- `user_id` (string): User ID
- `task_id` (integer): Task ID to complete

**Returns**:
```json
{
  "status": "completed",
  "task_id": 1,
  "title": "Buy groceries",
  "completed": true
}
```

---

### `update_task`
Update task title and/or description.

**Parameters**:
- `user_id` (string): User ID
- `task_id` (integer): Task ID to update
- `title` (string, optional): New title
- `description` (string, optional): New description

---

### `delete_task`
Delete a task.

**Parameters**:
- `user_id` (string): User ID
- `task_id` (integer): Task ID to delete

**Returns**:
```json
{
  "status": "deleted",
  "task_id": 1,
  "title": "Buy groceries"
}
```

---

## Error Codes

### Standard Error Response Format
```json
{
  "detail": "Error message or detailed object",
  "code": "ERROR_CODE",  // optional
  "suggestions": ["action1", "action2"]  // optional
}
```

### Common Error Codes
- `INVALID_MESSAGE`: Message content invalid
- `INVALID_TITLE`: Task title invalid
- `TASK_NOT_FOUND`: Task does not exist
- `CONVERSATION_NOT_FOUND`: Conversation does not exist
- `AI_SERVICE_UNAVAILABLE`: Gemini API temporarily unavailable
- `FORBIDDEN`: Access denied
- `UNAUTHORIZED`: Authentication required

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Security Features

1. **JWT Authentication**: All protected endpoints validate JWT tokens
2. **User ID Validation**: Path user_id must match JWT user_id
3. **Input Sanitization**: All user input sanitized to prevent XSS/injection
4. **Rate Limiting**: Prevents abuse with per-user limits
5. **Database Scoping**: All queries filtered by user_id
6. **Audit Logging**: Security events logged for monitoring

---

## Usage Examples

### Start a New Conversation
```bash
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my pending tasks"}'
```

### Continue Existing Conversation
```bash
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Complete task 5", "conversation_id": 123}'
```

### Get Conversation History
```bash
curl http://localhost:8000/api/user_123/conversations/123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

**Generated**: 2025-12-17
**Status**: Production Ready
