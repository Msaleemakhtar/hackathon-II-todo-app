# Quickstart Guide: Task and Tag Management API

This guide provides a quick overview of how to interact with the Task and Tag Management APIs. It assumes you have a running backend service (from `001-foundational-backend-setup`) and can obtain JWT access tokens.

## 1. Authentication

All endpoints described here require authentication. You need a valid JWT access token in the `Authorization` header as a Bearer token. Refer to the authentication API documentation (from `001-foundational-backend-setup`) to learn how to register and log in to obtain these tokens.

**Example: Obtaining a Token (assuming auth API is running at http://localhost:8000)**

```bash
# Register (if you haven't already)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d 
{
           "email": "testuser@example.com",
           "password": "securepassword"
         }

# Log in to get tokens
AUTH_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d 
{
           "email": "testuser@example.com",
           "password": "securepassword"
         })

ACCESS_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.refresh_token')

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"
```

Throughout this guide, replace `<YOUR_ACCESS_TOKEN>` with your actual access token.

## 2. Creating a Task

**Endpoint**: `POST /api/v1/tasks`

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d 
{
           "title": "Buy groceries",
           "description": "Milk, bread, eggs for breakfast.",
           "priority": "high",
           "due_date": "2025-12-25T18:00:00Z"
         }
```

## 3. Listing Tasks

**Endpoint**: `GET /api/v1/tasks`

```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

**With Filters and Pagination**:

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?status=pending&priority=high&page=1&limit=10&q=groceries&sort=-created_at" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

## 4. Creating a Tag

**Endpoint**: `POST /api/v1/tags`

```bash
curl -X POST "http://localhost:8000/api/v1/tags" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d 
{
           "name": "Shopping",
           "color": "#FF5733"
         }
```

## 5. Listing Tags

**Endpoint**: `GET /api/v1/tags`

```bash
curl -X GET "http://localhost:8000/api/v1/tags" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

## 6. Associating a Tag with a Task

First, create a task and a tag to get their IDs. Assume `TASK_ID` and `TAG_ID` are known.

**Endpoint**: `POST /api/v1/tasks/{task_id}/tags/{tag_id}`

```bash
TASK_ID=1
TAG_ID=1

curl -X POST "http://localhost:8000/api/v1/tasks/${TASK_ID}/tags/${TAG_ID}" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

This concludes the quickstart. For more details on specific endpoints, request/response schemas, and error codes, refer to the full OpenAPI specification (`task-tag-api.yaml`).
