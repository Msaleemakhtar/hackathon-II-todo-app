# API Usage Contracts for Task Dashboard UI

This document outlines the backend API endpoints that the frontend dashboard will consume. These endpoints are defined and implemented in the `002-task-tag-api` feature.

## Authentication

Authentication is handled by the `auth-sdk` package and the authentication endpoints from `001-foundational-backend-setup`. The frontend will use an `axios` interceptor to manage JWT access and refresh tokens.

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

## Task Endpoints

All endpoints require authentication.

### List Tasks

- **Endpoint**: `GET /api/v1/tasks`
- **Description**: Fetches all tasks for the authenticated user.
- **Query Params**:
  - `q`: Search term (string)
  - `status`: `'pending'` or `'completed'`
  - `priority`: `'low'`, `'medium'`, or `'high'`
  - `tag`: Tag name (string)
  - `sort`: Sort key (e.g., `due_date`, `-priority`)
  - `page`: Page number for pagination
  - `limit`: Items per page
- **Response Body**: A paginated list of `Task` objects.

### Create Task

- **Endpoint**: `POST /api/v1/tasks`
- **Description**: Creates a new task.
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string | null",
    "priority": "'low' | 'medium' \| 'high'",
    "due_date": "string (ISO 8601) | null",
    "tags": ["string"]
  }
  ```
- **Response Body**: The newly created `Task` object.

### Get Task

- **Endpoint**: `GET /api/v1/tasks/{task_id}`
- **Description**: Retrieves a single task by its ID.
- **Response Body**: A single `Task` object.

### Update Task

- **Endpoint**: `PUT /api/v1/tasks/{task_id}`
- **Description**: Updates an existing task.
- **Request Body**: Same as the create request body.
- **Response Body**: The updated `Task` object.

### Delete Task

- **Endpoint**: `DELETE /api/v1/tasks/{task_id}`
- **Description**: Deletes a task.
- **Response**: `204 No Content` on success.

### Mark Task Complete/Incomplete

- **Endpoint**: `PATCH /api/v1/tasks/{task_id}`
- **Description**: Toggles the completion status of a task.
- **Request Body**:
  ```json
  {
    "completed": true
  }
  ```
- **Response Body**: The updated `Task` object.

## Tag Endpoints

All endpoints require authentication.

### List Tags

- **Endpoint**: `GET /api/v1/tags`
- **Description**: Fetches all tags for the authenticated user.
- **Response Body**: An array of `Tag` objects.

### Create Tag

- **Endpoint**: `POST /api/v1/tags`
- **Description**: Creates a new tag.
- **Request Body**:
  ```json
  {
    "name": "string",
    "color": "string (hex) | null"
  }
  ```
- **Response Body**: The newly created `Tag` object.
