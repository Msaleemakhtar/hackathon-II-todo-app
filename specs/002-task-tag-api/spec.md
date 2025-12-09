# Feature Specification: Task and Tag Management APIs

**Feature Branch**: `002-task-tag-api`
**Created**: 2025-12-09
**Status**: Draft
**Constitution Version**: 2.2.0
**Prerequisites**: 001-foundational-backend-setup (Database schema and Authentication API must be complete)
**Input**: User description: "Generate a complete feature specification for the core Task and Tag management APIs of the Todo App. This specification covers RESTful API endpoints for creating, reading, updating, and deleting Tasks and Tags, including advanced filtering, sorting, and association logic."

---

## 1. Overview

This specification defines the RESTful API endpoints for Task and Tag management in the Todo App Phase II. It encompasses:

1. **Task Management API (P1)**: Complete CRUD operations for tasks including create, read, update, partial update, and delete endpoints.

2. **Tag Management API (P2)**: CRUD operations for tags enabling users to create, list, update, and delete their categorization labels.

3. **Task-Tag Association API (P2)**: Endpoints for managing the many-to-many relationship between tasks and tags.

4. **Enhanced Task Listing (P2)**: Advanced filtering, sorting, pagination, and full-text search capabilities for the task list endpoint.

**Security Mandate**: ALL endpoints defined in this specification **MUST** be protected by the authentication dependency created in the foundational setup (001-foundational-backend-setup). Every request **MUST** include a valid JWT access token in the Authorization header.

**Data Isolation Mandate**: Every endpoint **MUST** enforce strict data isolation. Users can ONLY interact with their own tasks and tags. Attempts to access another user's resources **MUST** result in a 404 Not Found error (to prevent resource enumeration) or 403 Forbidden where explicitly specified.

---

## 2. User Scenarios & Testing

### User Story 1 - Create a New Task (Priority: P1)

An authenticated user creates a new task to track an item they need to complete. The system validates the input, associates the task with the user, and confirms successful creation.

**Why this priority**: Task creation is the fundamental action in a todo application. Without the ability to create tasks, the application has no core value proposition. This is the most essential user journey.

**Independent Test**: Can be fully tested by sending a POST request with valid task data and verifying the task is created in the database with the correct user_id association.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a valid access token, **When** the user submits POST /api/v1/tasks with title "Buy groceries" and priority "high", **Then** the system creates the task and returns HTTP 201 Created with the complete task object including id, created_at, and updated_at timestamps.

2. **Given** an authenticated user, **When** the user submits POST /api/v1/tasks with only title "Quick task" (all optional fields omitted), **Then** the system creates the task with default values: priority="medium", completed=false, description=null, due_date=null.

3. **Given** an authenticated user, **When** the user submits POST /api/v1/tasks with an empty or whitespace-only title, **Then** the system returns HTTP 400 Bad Request with error code "INVALID_TITLE" and message "Title is required and must be 1-200 characters".

4. **Given** an authenticated user, **When** the user submits POST /api/v1/tasks with a title exceeding 200 characters, **Then** the system returns HTTP 400 Bad Request with error code "INVALID_TITLE" and message "Title is required and must be 1-200 characters".

---

### User Story 2 - View Task List (Priority: P1)

An authenticated user views their list of tasks to understand what they need to accomplish. The system displays all tasks belonging to the user with pagination support.

**Why this priority**: Viewing the task list is the second most critical feature. Users must see their tasks to manage them effectively. This enables the basic todo workflow.

**Independent Test**: Can be fully tested by creating multiple tasks for a user and verifying the GET endpoint returns only that user's tasks with correct pagination metadata.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 5 tasks, **When** the user requests GET /api/v1/tasks, **Then** the system returns HTTP 200 OK with a paginated response containing all 5 tasks and metadata: total=5, page=1, limit=20, pages=1.

2. **Given** an authenticated user with 50 tasks, **When** the user requests GET /api/v1/tasks?page=2&limit=10, **Then** the system returns tasks 11-20 with metadata: total=50, page=2, limit=10, pages=5.

3. **Given** an authenticated user with 0 tasks, **When** the user requests GET /api/v1/tasks, **Then** the system returns HTTP 200 OK with items=[], total=0, page=1, limit=20, pages=0.

4. **Given** User A with 3 tasks and User B with 2 tasks, **When** User A requests GET /api/v1/tasks, **Then** the system returns only User A's 3 tasks (data isolation).

---

### User Story 3 - View Single Task (Priority: P1)

An authenticated user views the details of a specific task to see all its information including description, due date, and associated tags.

**Why this priority**: Viewing task details is essential for understanding task context. Users need to see full task information before updating or completing it.

**Independent Test**: Can be fully tested by creating a task and verifying GET /api/v1/tasks/{task_id} returns the complete task object.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task with id=42, **When** the user requests GET /api/v1/tasks/42, **Then** the system returns HTTP 200 OK with the complete task object including all fields and associated tags.

2. **Given** an authenticated user, **When** the user requests GET /api/v1/tasks/99999 (non-existent task), **Then** the system returns HTTP 404 Not Found with error code "TASK_NOT_FOUND" and message "Task not found".

3. **Given** User A and User B where User B owns task id=10, **When** User A requests GET /api/v1/tasks/10, **Then** the system returns HTTP 404 Not Found with error code "TASK_NOT_FOUND" (prevents resource enumeration).

---

### User Story 4 - Update Task (Priority: P1)

An authenticated user updates a task to modify its title, description, priority, or due date. The system validates the changes and persists them.

**Why this priority**: Task updates are essential for the todo workflow. Users need to refine task details, change priorities, and set due dates as their plans evolve.

**Independent Test**: Can be fully tested by creating a task, sending a PUT request with modified data, and verifying the changes are persisted.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task id=42 with title "Old title", **When** the user submits PUT /api/v1/tasks/42 with title "New title", **Then** the system updates the task and returns HTTP 200 OK with the updated task object and a new updated_at timestamp.

2. **Given** an authenticated user who owns task id=42, **When** the user submits PUT /api/v1/tasks/42 with invalid priority "urgent", **Then** the system returns HTTP 400 Bad Request with error code "INVALID_PRIORITY" and message "Priority must be low, medium, or high".

3. **Given** an authenticated user, **When** the user submits PUT /api/v1/tasks/99999, **Then** the system returns HTTP 404 Not Found with error code "TASK_NOT_FOUND".

4. **Given** User A and User B where User B owns task id=10, **When** User A submits PUT /api/v1/tasks/10, **Then** the system returns HTTP 404 Not Found (data isolation).

---

### User Story 5 - Mark Task Complete/Incomplete (Priority: P1)

An authenticated user marks a task as complete or reverts it to pending. This is the core workflow action representing task completion.

**Why this priority**: Marking tasks complete is the fundamental action that delivers value - tracking what's done. This is implemented via PATCH for partial updates.

**Independent Test**: Can be fully tested by creating a task, sending a PATCH request with completed=true, and verifying the status change.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task id=42 with completed=false, **When** the user submits PATCH /api/v1/tasks/42 with {"completed": true}, **Then** the system updates only the completed field and returns HTTP 200 OK with the updated task.

2. **Given** an authenticated user who owns task id=42 with completed=true, **When** the user submits PATCH /api/v1/tasks/42 with {"completed": false}, **Then** the system reverts the task to pending status.

3. **Given** an authenticated user who owns task id=42, **When** the user submits PATCH /api/v1/tasks/42 with {"priority": "high"}, **Then** the system updates only the priority field, leaving all other fields unchanged.

---

### User Story 6 - Delete Task (Priority: P1)

An authenticated user deletes a task they no longer need to track. The system permanently removes the task and any associated tag relationships.

**Why this priority**: Task deletion is essential for list hygiene. Users must be able to remove irrelevant or completed tasks to maintain a clean workspace.

**Independent Test**: Can be fully tested by creating a task, sending DELETE request, and verifying the task no longer exists.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task id=42, **When** the user submits DELETE /api/v1/tasks/42, **Then** the system deletes the task and returns HTTP 204 No Content.

2. **Given** an authenticated user who owns task id=42 with 3 associated tags, **When** the user deletes task id=42, **Then** the task-tag associations in TaskTagLink are also deleted (cascade), but the tags themselves remain.

3. **Given** an authenticated user, **When** the user submits DELETE /api/v1/tasks/99999, **Then** the system returns HTTP 404 Not Found with error code "TASK_NOT_FOUND".

4. **Given** User A and User B where User B owns task id=10, **When** User A submits DELETE /api/v1/tasks/10, **Then** the system returns HTTP 404 Not Found (data isolation).

---

### User Story 7 - Create Tag (Priority: P2)

An authenticated user creates a tag to categorize their tasks. Tags help users organize tasks into meaningful groups.

**Why this priority**: Tags enhance task organization but are not required for basic todo functionality. This is an enhancement feature.

**Independent Test**: Can be fully tested by sending POST /api/v1/tags with tag data and verifying the tag is created.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user submits POST /api/v1/tags with name "Work" and color "#FF5733", **Then** the system creates the tag and returns HTTP 201 Created with the complete tag object.

2. **Given** an authenticated user who already has a tag named "Work", **When** the user submits POST /api/v1/tags with name "Work", **Then** the system returns HTTP 400 Bad Request with error code "TAG_ALREADY_EXISTS" and message "A tag with this name already exists".

3. **Given** an authenticated user, **When** the user submits POST /api/v1/tags with an empty name, **Then** the system returns HTTP 400 Bad Request with error code "INVALID_TAG_NAME" and message "Tag name is required and must be 1-50 characters".

---

### User Story 8 - View Tags (Priority: P2)

An authenticated user views their list of tags to see available categorization options for their tasks.

**Why this priority**: Tag listing supports the tag management workflow but depends on tag creation being available first.

**Independent Test**: Can be fully tested by creating tags and verifying GET /api/v1/tags returns all user's tags.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tags, **When** the user requests GET /api/v1/tags, **Then** the system returns HTTP 200 OK with all 3 tags belonging to the user.

2. **Given** an authenticated user with 0 tags, **When** the user requests GET /api/v1/tags, **Then** the system returns HTTP 200 OK with an empty array.

3. **Given** User A with 3 tags and User B with 2 tags, **When** User A requests GET /api/v1/tags, **Then** the system returns only User A's 3 tags (data isolation).

---

### User Story 9 - Update Tag (Priority: P2)

An authenticated user updates a tag's name or color to refine their categorization system.

**Why this priority**: Tag updates allow users to evolve their organization system without recreating tags.

**Independent Test**: Can be fully tested by creating a tag, sending PUT request, and verifying changes.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns tag id=5 with name "Work", **When** the user submits PUT /api/v1/tags/5 with name "Office", **Then** the system updates the tag and returns HTTP 200 OK.

2. **Given** an authenticated user who owns tags "Work" (id=5) and "Personal" (id=6), **When** the user submits PUT /api/v1/tags/5 with name "Personal", **Then** the system returns HTTP 400 Bad Request with error code "TAG_ALREADY_EXISTS" and message "A tag with this name already exists".

3. **Given** an authenticated user, **When** the user submits PUT /api/v1/tags/99999, **Then** the system returns HTTP 404 Not Found with error code "TAG_NOT_FOUND" and message "Tag not found".

---

### User Story 10 - Delete Tag (Priority: P2)

An authenticated user deletes a tag they no longer need. Associated task-tag relationships are removed but tasks remain.

**Why this priority**: Tag deletion is part of complete tag lifecycle management.

**Independent Test**: Can be fully tested by creating a tag, sending DELETE request, and verifying removal.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns tag id=5, **When** the user submits DELETE /api/v1/tags/5, **Then** the system deletes the tag and returns HTTP 204 No Content.

2. **Given** an authenticated user who owns tag id=5 associated with 3 tasks, **When** the user deletes tag id=5, **Then** the task-tag associations are removed but the tasks themselves remain.

3. **Given** User A and User B where User B owns tag id=10, **When** User A submits DELETE /api/v1/tags/10, **Then** the system returns HTTP 404 Not Found (data isolation).

---

### User Story 11 - Associate Tag with Task (Priority: P2)

An authenticated user adds a tag to a task to categorize it. This creates a relationship in the TaskTagLink junction table.

**Why this priority**: Tag-task association is the core value of the tagging feature, enabling categorization.

**Independent Test**: Can be fully tested by creating a task and tag, sending POST to associate them, and verifying the relationship.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task id=42 and tag id=5, **When** the user submits POST /api/v1/tasks/42/tags/5, **Then** the system creates the association and returns HTTP 201 Created with the updated task object including the tag.

2. **Given** an authenticated user who owns task id=42 already tagged with tag id=5, **When** the user submits POST /api/v1/tasks/42/tags/5 again, **Then** the system returns HTTP 200 OK (idempotent - no duplicate created).

3. **Given** an authenticated user who owns task id=42 but not tag id=99, **When** the user submits POST /api/v1/tasks/42/tags/99, **Then** the system returns HTTP 404 Not Found with error code "TAG_NOT_FOUND".

4. **Given** User A who owns task id=42 and User B who owns tag id=10, **When** User A submits POST /api/v1/tasks/42/tags/10, **Then** the system returns HTTP 404 Not Found (cannot use another user's tag).

---

### User Story 12 - Dissociate Tag from Task (Priority: P2)

An authenticated user removes a tag from a task when the categorization is no longer relevant.

**Why this priority**: Removing tags completes the tag-task management lifecycle.

**Independent Test**: Can be fully tested by associating a tag with a task, sending DELETE to remove, and verifying.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns task id=42 tagged with tag id=5, **When** the user submits DELETE /api/v1/tasks/42/tags/5, **Then** the system removes the association and returns HTTP 204 No Content.

2. **Given** an authenticated user who owns task id=42 not tagged with tag id=5, **When** the user submits DELETE /api/v1/tasks/42/tags/5, **Then** the system returns HTTP 204 No Content (idempotent).

3. **Given** an authenticated user, **When** the user submits DELETE /api/v1/tasks/99999/tags/5, **Then** the system returns HTTP 404 Not Found with error code "TASK_NOT_FOUND".

---

### User Story 13 - Filter and Search Tasks (Priority: P2)

An authenticated user filters and searches their task list to find specific tasks based on status, priority, tags, or text content.

**Why this priority**: Filtering and search become essential as the task list grows, enabling users to focus on relevant tasks.

**Independent Test**: Can be fully tested by creating tasks with various attributes and verifying filter parameters return correct subsets.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 10 tasks (5 completed, 5 pending), **When** the user requests GET /api/v1/tasks?status=completed, **Then** the system returns only the 5 completed tasks.

2. **Given** an authenticated user with tasks of various priorities, **When** the user requests GET /api/v1/tasks?priority=high, **Then** the system returns only high-priority tasks.

3. **Given** an authenticated user with tasks tagged "Work" (tag id=5), **When** the user requests GET /api/v1/tasks?tag=5, **Then** the system returns only tasks with that tag.

4. **Given** an authenticated user with tasks containing "meeting" in title or description, **When** the user requests GET /api/v1/tasks?q=meeting, **Then** the system returns tasks where title OR description contains "meeting" (case-insensitive).

5. **Given** an authenticated user, **When** the user requests GET /api/v1/tasks?status=pending&priority=high, **Then** the system returns only pending high-priority tasks (combined filters).

---

### User Story 14 - Sort Tasks (Priority: P2)

An authenticated user sorts their task list by various fields to prioritize their view.

**Why this priority**: Sorting enables users to view tasks in their preferred order (by due date, priority, etc.).

**Independent Test**: Can be fully tested by creating tasks with various values and verifying sort parameters order results correctly.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks, **When** the user requests GET /api/v1/tasks?sort=due_date, **Then** the system returns tasks sorted by due_date ascending (null dates last).

2. **Given** an authenticated user with tasks, **When** the user requests GET /api/v1/tasks?sort=-created_at, **Then** the system returns tasks sorted by created_at descending (newest first).

3. **Given** an authenticated user with tasks, **When** the user requests GET /api/v1/tasks?sort=priority, **Then** the system returns tasks sorted by priority (high > medium > low).

4. **Given** an authenticated user with tasks, **When** the user requests GET /api/v1/tasks?sort=title, **Then** the system returns tasks sorted alphabetically by title.

---

### Edge Cases

- **Empty State - No Tasks**: GET /api/v1/tasks returns {items: [], total: 0, page: 1, limit: 20, pages: 0} with HTTP 200.

- **Empty State - No Tags**: GET /api/v1/tags returns [] with HTTP 200.

- **Boundary - Title Length**: Title with exactly 200 characters is accepted; 201 characters is rejected.

- **Boundary - Description Length**: Description with exactly 1000 characters is accepted; 1001 characters returns HTTP 400 with error code "DESCRIPTION_TOO_LONG".

- **Boundary - Tag Name Length**: Tag name with exactly 50 characters is accepted; 51 characters is rejected.

- **Boundary - Pagination Limit**: limit parameter capped at 100; values above 100 are treated as 100.

- **Invalid Input - Negative Page/Limit**: page=0 or page=-1 returns HTTP 400 with error code "INVALID_PAGINATION"; limit=0 or limit=-1 also returns HTTP 400.

- **Invalid Input - Non-integer IDs**: GET /api/v1/tasks/abc returns HTTP 422 (Pydantic validation failure).

- **Invalid Input - Invalid Sort Field**: GET /api/v1/tasks?sort=invalid returns HTTP 400 with error code "INVALID_SORT_FIELD" and message "Sort field must be one of: due_date, priority, created_at, title".

- **Invalid Input - Invalid Status Filter**: GET /api/v1/tasks?status=invalid returns HTTP 400 with error code "INVALID_STATUS" and message "Status must be one of: all, pending, completed".

- **State Conflict - Concurrent Delete**: If task is deleted by another request during update, return HTTP 404.

- **Cascade Delete - Task with Tags**: Deleting a task removes its TaskTagLink entries but leaves tags intact.

- **Cascade Delete - Tag with Tasks**: Deleting a tag removes its TaskTagLink entries but leaves tasks intact.

- **Due Date Past Validation**: Creating a task with a past due_date is allowed (user may be tracking overdue items); system does NOT reject past dates.

---

## 3. Task Management API Endpoints (P1)

### 3.1 Base Configuration

- **API Version Prefix**: All endpoints prefixed with `/api/v1/`
- **Authentication**: All endpoints require `Authorization: Bearer <access_token>` header
- **Content Type**: `application/json` for request and response bodies
- **Error Format**: Consistent JSON error responses per constitution Section V

### 3.2 Create Task

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | POST                                      |
| **Path**           | /api/v1/tasks                             |
| **Authentication** | Required (Bearer token)                   |

**Request Body**:
```json
{
  "title": "string (required, 1-200 characters)",
  "description": "string (optional, max 1000 characters)",
  "priority": "string (optional, default: 'medium', enum: 'low', 'medium', 'high')",
  "due_date": "string (optional, ISO 8601 datetime)",
  "completed": "boolean (optional, default: false)"
}
```

**Success Response (201 Created)**:
```json
{
  "id": 42,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-15T10:00:00Z",
  "user_id": "uuid-string",
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T10:30:00Z",
  "tags": []
}
```

**Error Responses**:

| Status Code | Error Code           | Message                                          | Condition                          |
| ----------- | -------------------- | ------------------------------------------------ | ---------------------------------- |
| 400         | INVALID_TITLE        | Title is required and must be 1-200 characters   | Empty, whitespace-only, or >200    |
| 400         | DESCRIPTION_TOO_LONG | Description cannot exceed 1000 characters        | Description > 1000 characters      |
| 400         | INVALID_PRIORITY     | Priority must be low, medium, or high            | Invalid priority value             |
| 400         | INVALID_DUE_DATE     | Due date must be a valid ISO 8601 datetime       | Invalid date format                |
| 401         | MISSING_TOKEN        | Authentication required                          | No Authorization header            |
| 401         | TOKEN_EXPIRED        | Access token has expired                         | Expired token                      |
| 401         | INVALID_TOKEN        | Invalid authentication token                     | Malformed token                    |
| 422         | VALIDATION_ERROR     | {field-specific validation message}              | Pydantic validation failure        |

### 3.3 List Tasks

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | GET                                       |
| **Path**           | /api/v1/tasks                             |
| **Authentication** | Required (Bearer token)                   |

**Query Parameters**:

| Parameter | Type    | Default | Description                                                |
| --------- | ------- | ------- | ---------------------------------------------------------- |
| page      | integer | 1       | Page number (must be >= 1)                                 |
| limit     | integer | 20      | Items per page (1-100, capped at 100)                      |
| q         | string  | null    | Full-text search on title and description                  |
| status    | string  | "all"   | Filter: "all", "pending", "completed"                      |
| priority  | string  | null    | Filter: "low", "medium", "high"                            |
| tag       | string  | null    | Filter by tag ID (integer) or tag name (string)            |
| sort      | string  | null    | Sort field: "due_date", "priority", "created_at", "title". Prefix with "-" for descending (e.g., "-created_at") |

**Success Response (200 OK)**:
```json
{
  "items": [
    {
      "id": 42,
      "title": "Buy groceries",
      "description": "Milk, bread, eggs",
      "completed": false,
      "priority": "high",
      "due_date": "2025-12-15T10:00:00Z",
      "user_id": "uuid-string",
      "created_at": "2025-12-09T10:30:00Z",
      "updated_at": "2025-12-09T10:30:00Z",
      "tags": [
        {"id": 1, "name": "Shopping", "color": "#FF5733"}
      ]
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

**Error Responses**:

| Status Code | Error Code          | Message                                                      | Condition                  |
| ----------- | ------------------- | ------------------------------------------------------------ | -------------------------- |
| 400         | INVALID_PAGINATION  | Page and limit must be positive integers                     | page or limit <= 0         |
| 400         | INVALID_STATUS      | Status must be one of: all, pending, completed               | Invalid status value       |
| 400         | INVALID_PRIORITY    | Priority must be low, medium, or high                        | Invalid priority value     |
| 400         | INVALID_SORT_FIELD  | Sort field must be one of: due_date, priority, created_at, title | Invalid sort field     |
| 401         | MISSING_TOKEN       | Authentication required                                      | No Authorization header    |
| 401         | TOKEN_EXPIRED       | Access token has expired                                     | Expired token              |

### 3.4 Get Single Task

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | GET                                       |
| **Path**           | /api/v1/tasks/{task_id}                   |
| **Authentication** | Required (Bearer token)                   |

**Path Parameters**:

| Parameter | Type    | Description              |
| --------- | ------- | ------------------------ |
| task_id   | integer | Unique task identifier   |

**Success Response (200 OK)**:
```json
{
  "id": 42,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-15T10:00:00Z",
  "user_id": "uuid-string",
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T10:30:00Z",
  "tags": [
    {"id": 1, "name": "Shopping", "color": "#FF5733"}
  ]
}
```

**Error Responses**:

| Status Code | Error Code     | Message                     | Condition                              |
| ----------- | -------------- | --------------------------- | -------------------------------------- |
| 401         | MISSING_TOKEN  | Authentication required     | No Authorization header                |
| 401         | TOKEN_EXPIRED  | Access token has expired    | Expired token                          |
| 404         | TASK_NOT_FOUND | Task not found              | Task doesn't exist OR belongs to other |
| 422         | VALIDATION_ERROR | {validation message}      | Invalid task_id format                 |

### 3.5 Update Task (Full)

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | PUT                                       |
| **Path**           | /api/v1/tasks/{task_id}                   |
| **Authentication** | Required (Bearer token)                   |

**Request Body**:
```json
{
  "title": "string (required, 1-200 characters)",
  "description": "string (optional, max 1000 characters)",
  "priority": "string (required, enum: 'low', 'medium', 'high')",
  "due_date": "string (optional, ISO 8601 datetime or null)",
  "completed": "boolean (required)"
}
```

**Success Response (200 OK)**: Returns the complete updated task object.

**Error Responses**:

| Status Code | Error Code           | Message                                        | Condition                   |
| ----------- | -------------------- | ---------------------------------------------- | --------------------------- |
| 400         | INVALID_TITLE        | Title is required and must be 1-200 characters | Invalid title               |
| 400         | DESCRIPTION_TOO_LONG | Description cannot exceed 1000 characters      | Description too long        |
| 400         | INVALID_PRIORITY     | Priority must be low, medium, or high          | Invalid priority            |
| 401         | MISSING_TOKEN        | Authentication required                        | No Authorization header     |
| 404         | TASK_NOT_FOUND       | Task not found                                 | Not found or not owned      |

### 3.6 Update Task (Partial)

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | PATCH                                     |
| **Path**           | /api/v1/tasks/{task_id}                   |
| **Authentication** | Required (Bearer token)                   |

**Request Body** (all fields optional, only provided fields are updated):
```json
{
  "title": "string (optional, 1-200 characters)",
  "description": "string (optional, max 1000 characters or null)",
  "priority": "string (optional, enum: 'low', 'medium', 'high')",
  "due_date": "string (optional, ISO 8601 datetime or null)",
  "completed": "boolean (optional)"
}
```

**Success Response (200 OK)**: Returns the complete updated task object.

**Error Responses**: Same as PUT endpoint.

### 3.7 Delete Task

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | DELETE                                    |
| **Path**           | /api/v1/tasks/{task_id}                   |
| **Authentication** | Required (Bearer token)                   |

**Success Response (204 No Content)**: Empty response body.

**Error Responses**:

| Status Code | Error Code     | Message                     | Condition                   |
| ----------- | -------------- | --------------------------- | --------------------------- |
| 401         | MISSING_TOKEN  | Authentication required     | No Authorization header     |
| 404         | TASK_NOT_FOUND | Task not found              | Not found or not owned      |

---

## 4. Tag Management API Endpoints (P2)

### 4.1 Create Tag

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | POST                                      |
| **Path**           | /api/v1/tags                              |
| **Authentication** | Required (Bearer token)                   |

**Request Body**:
```json
{
  "name": "string (required, 1-50 characters)",
  "color": "string (optional, hex format e.g., '#FF5733')"
}
```

**Success Response (201 Created)**:
```json
{
  "id": 5,
  "name": "Work",
  "color": "#FF5733",
  "user_id": "uuid-string"
}
```

**Error Responses**:

| Status Code | Error Code         | Message                                        | Condition                      |
| ----------- | ------------------ | ---------------------------------------------- | ------------------------------ |
| 400         | INVALID_TAG_NAME   | Tag name is required and must be 1-50 characters | Empty or too long name       |
| 400         | TAG_ALREADY_EXISTS | A tag with this name already exists            | Duplicate name for user        |
| 400         | INVALID_COLOR      | Color must be a valid hex color (e.g., #FF5733) | Invalid hex format            |
| 401         | MISSING_TOKEN      | Authentication required                        | No Authorization header        |

### 4.2 List Tags

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | GET                                       |
| **Path**           | /api/v1/tags                              |
| **Authentication** | Required (Bearer token)                   |

**Success Response (200 OK)**:
```json
[
  {"id": 1, "name": "Work", "color": "#FF5733", "user_id": "uuid-string"},
  {"id": 2, "name": "Personal", "color": "#33FF57", "user_id": "uuid-string"}
]
```

**Error Responses**:

| Status Code | Error Code    | Message                  | Condition               |
| ----------- | ------------- | ------------------------ | ----------------------- |
| 401         | MISSING_TOKEN | Authentication required  | No Authorization header |

### 4.3 Update Tag

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | PUT                                       |
| **Path**           | /api/v1/tags/{tag_id}                     |
| **Authentication** | Required (Bearer token)                   |

**Request Body**:
```json
{
  "name": "string (required, 1-50 characters)",
  "color": "string (optional, hex format or null)"
}
```

**Success Response (200 OK)**: Returns the complete updated tag object.

**Error Responses**:

| Status Code | Error Code         | Message                                         | Condition                |
| ----------- | ------------------ | ----------------------------------------------- | ------------------------ |
| 400         | INVALID_TAG_NAME   | Tag name is required and must be 1-50 characters | Invalid name            |
| 400         | TAG_ALREADY_EXISTS | A tag with this name already exists             | Duplicate name for user  |
| 401         | MISSING_TOKEN      | Authentication required                         | No Authorization header  |
| 404         | TAG_NOT_FOUND      | Tag not found                                   | Not found or not owned   |

### 4.4 Delete Tag

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | DELETE                                    |
| **Path**           | /api/v1/tags/{tag_id}                     |
| **Authentication** | Required (Bearer token)                   |

**Success Response (204 No Content)**: Empty response body.

**Error Responses**:

| Status Code | Error Code    | Message                  | Condition               |
| ----------- | ------------- | ------------------------ | ----------------------- |
| 401         | MISSING_TOKEN | Authentication required  | No Authorization header |
| 404         | TAG_NOT_FOUND | Tag not found            | Not found or not owned  |

---

## 5. Task-Tag Association API Endpoints (P2)

### 5.1 Associate Tag with Task

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | POST                                      |
| **Path**           | /api/v1/tasks/{task_id}/tags/{tag_id}     |
| **Authentication** | Required (Bearer token)                   |

**Path Parameters**:

| Parameter | Type    | Description              |
| --------- | ------- | ------------------------ |
| task_id   | integer | Unique task identifier   |
| tag_id    | integer | Unique tag identifier    |

**Success Response (201 Created)**: Returns the task object with updated tags array.

**Success Response (200 OK)**: If association already exists (idempotent), returns the task object.

**Error Responses**:

| Status Code | Error Code     | Message                  | Condition                            |
| ----------- | -------------- | ------------------------ | ------------------------------------ |
| 401         | MISSING_TOKEN  | Authentication required  | No Authorization header              |
| 404         | TASK_NOT_FOUND | Task not found           | Task not found or not owned by user  |
| 404         | TAG_NOT_FOUND  | Tag not found            | Tag not found or not owned by user   |

### 5.2 Dissociate Tag from Task

| Attribute          | Value                                     |
| ------------------ | ----------------------------------------- |
| **Method**         | DELETE                                    |
| **Path**           | /api/v1/tasks/{task_id}/tags/{tag_id}     |
| **Authentication** | Required (Bearer token)                   |

**Success Response (204 No Content)**: Empty response body. Idempotent - returns 204 even if association didn't exist.

**Error Responses**:

| Status Code | Error Code     | Message                  | Condition                            |
| ----------- | -------------- | ------------------------ | ------------------------------------ |
| 401         | MISSING_TOKEN  | Authentication required  | No Authorization header              |
| 404         | TASK_NOT_FOUND | Task not found           | Task not found or not owned by user  |
| 404         | TAG_NOT_FOUND  | Tag not found            | Tag not found or not owned by user   |

---

## 6. Non-Functional & Security Requirements

### 6.1 Data Isolation

- Every database query **MUST** include `user_id = current_user.id` filter
- Users **MUST NOT** be able to read, update, or delete resources belonging to other users
- Attempts to access another user's resources **MUST** return HTTP 404 Not Found (not 403) to prevent resource enumeration
- The `user_id` field **MUST** be set from the JWT token, never from client input

### 6.2 Business Logic Architecture

- All business logic **MUST** be placed in a dedicated `/backend/src/services/` layer
- API router handlers **MUST** delegate to service layer functions
- Service functions **MUST** receive the current user context and validate ownership
- Service functions **MUST** raise appropriate exceptions that are caught and converted to HTTP responses

**Service Layer Structure**:
```
/backend/src/services/
├── task_service.py   # Task CRUD operations
├── tag_service.py    # Tag CRUD operations
└── __init__.py
```

### 6.3 Input Validation

All incoming data **MUST** be validated against Pydantic schemas with the following rules:

**Task Validation**:
- `title`: Required, string, 1-200 characters after trimming whitespace
- `description`: Optional, string or null, max 1000 characters
- `priority`: Optional, default "medium", enum ["low", "medium", "high"]
- `due_date`: Optional, valid ISO 8601 datetime or null
- `completed`: Optional, boolean, default false

**Tag Validation**:
- `name`: Required, string, 1-50 characters after trimming whitespace
- `color`: Optional, string matching hex color pattern `^#[0-9A-Fa-f]{6}$` or null

### 6.4 Performance Requirements

- API response time **MUST** be < 200ms p95 for CRUD operations (per constitution)
- List endpoints **MUST** use eager loading for tags to avoid N+1 queries
- Database queries **MUST** use the appropriate indexes defined in the constitution
- Pagination **MUST** be implemented using OFFSET/LIMIT with proper ordering for deterministic results

### 6.5 Sorting Behavior

**Priority Sorting**:
- Sort order for priority (ascending): high > medium > low (most urgent first)
- Sort order for priority (descending): low > medium > high

**Due Date Sorting**:
- Ascending: Earliest dates first, NULL values last
- Descending: Latest dates first, NULL values first

**Title Sorting**:
- Case-insensitive alphabetical ordering

### 6.6 Search Behavior

The `q` query parameter implements full-text search:
- Search is case-insensitive
- Search matches partial strings (contains)
- Search is performed on both `title` AND `description` fields (OR logic)
- Empty search string returns all results (same as no search)

---

## 7. Requirements Summary

### Functional Requirements

**Task Management (P1)**:
- **FR-001**: System MUST allow authenticated users to create tasks with title (required), description, priority, due_date, and completed status.
- **FR-002**: System MUST validate task title is 1-200 characters and return error code "INVALID_TITLE" for violations.
- **FR-003**: System MUST validate task description is max 1000 characters and return error code "DESCRIPTION_TOO_LONG" for violations.
- **FR-004**: System MUST validate priority is one of "low", "medium", "high" and return error code "INVALID_PRIORITY" for violations.
- **FR-005**: System MUST allow authenticated users to list their tasks with pagination (page, limit parameters).
- **FR-006**: System MUST allow authenticated users to retrieve a single task by ID.
- **FR-007**: System MUST allow authenticated users to update all fields of a task via PUT.
- **FR-008**: System MUST allow authenticated users to partially update task fields via PATCH.
- **FR-009**: System MUST allow authenticated users to delete their tasks.
- **FR-010**: System MUST automatically set user_id from JWT token when creating tasks.
- **FR-011**: System MUST update the updated_at timestamp on any task modification.

**Tag Management (P2)**:
- **FR-012**: System MUST allow authenticated users to create tags with name (required) and optional color.
- **FR-013**: System MUST validate tag name is 1-50 characters and return error code "INVALID_TAG_NAME" for violations.
- **FR-014**: System MUST prevent duplicate tag names per user and return error code "TAG_ALREADY_EXISTS".
- **FR-015**: System MUST allow authenticated users to list all their tags.
- **FR-016**: System MUST allow authenticated users to update tag name and color.
- **FR-017**: System MUST allow authenticated users to delete tags.

**Task-Tag Association (P2)**:
- **FR-018**: System MUST allow authenticated users to associate tags with tasks via POST /tasks/{id}/tags/{id}.
- **FR-019**: System MUST allow authenticated users to dissociate tags from tasks via DELETE /tasks/{id}/tags/{id}.
- **FR-020**: System MUST verify both task and tag belong to the authenticated user before association.
- **FR-021**: System MUST cascade delete TaskTagLink entries when a task is deleted.
- **FR-022**: System MUST cascade delete TaskTagLink entries when a tag is deleted.

**Enhanced Task Listing (P2)**:
- **FR-023**: System MUST support filtering tasks by status (all, pending, completed).
- **FR-024**: System MUST support filtering tasks by priority (low, medium, high).
- **FR-025**: System MUST support filtering tasks by tag ID or tag name.
- **FR-026**: System MUST support full-text search on title and description via `q` parameter.
- **FR-027**: System MUST support sorting by due_date, priority, created_at, and title.
- **FR-028**: System MUST support descending sort via "-" prefix (e.g., -created_at).
- **FR-029**: System MUST return paginated responses in the format: {items, total, page, limit, pages}.

**Security (All Priorities)**:
- **FR-030**: System MUST reject all requests without valid JWT access token with error code "MISSING_TOKEN".
- **FR-031**: System MUST reject requests with expired tokens with error code "TOKEN_EXPIRED".
- **FR-032**: System MUST return 404 Not Found when accessing resources owned by other users (data isolation).

### Key Entities

- **Task**: Represents a todo item. Key attributes: id (auto-generated), title (required), description, completed status, priority level, due_date, recurrence_rule, user_id (owner), timestamps. Can have many tags via TaskTagLink.

- **Tag**: Represents a categorization label. Key attributes: id (auto-generated), name (unique per user), color (hex), user_id (owner). Can be associated with many tasks via TaskTagLink.

- **TaskTagLink**: Junction entity for many-to-many relationship. Composite key of task_id and tag_id.

---

## 8. Success Criteria

### Measurable Outcomes

- **SC-001**: All Task CRUD endpoints (POST, GET, PUT, PATCH, DELETE) return responses within 200ms p95.
- **SC-002**: GET /api/v1/tasks correctly paginates 1000 tasks, returning pages of 20 items with accurate total/pages counts.
- **SC-003**: Filtering by status=pending returns ONLY tasks where completed=false (100% accuracy).
- **SC-004**: Filtering by priority=high returns ONLY high-priority tasks (100% accuracy).
- **SC-005**: Filtering by tag returns ONLY tasks associated with that tag (100% accuracy).
- **SC-006**: Search query `q=meeting` returns all tasks containing "meeting" in title OR description (case-insensitive).
- **SC-007**: Sort by `-due_date` returns tasks ordered by due_date descending with nulls first.
- **SC-008**: User A cannot retrieve, update, or delete User B's tasks (data isolation verified across all endpoints).
- **SC-009**: User A cannot use User B's tags to tag User A's tasks (cross-user tag protection).
- **SC-010**: All error responses follow the format: `{"detail": "message", "code": "ERROR_CODE"}`.
- **SC-011**: Tag CRUD operations complete in under 100ms p95.
- **SC-012**: Task-tag association/dissociation operations are idempotent (no duplicate entries, no errors on repeat).
- **SC-013**: Backend test coverage for task and tag services is >= 80%.

---

## 9. Assumptions

The following assumptions have been applied based on the constitution and specification requirements:

1. **Authentication Dependency**: The authentication system from 001-foundational-backend-setup is complete and the `get_current_user` dependency is available for use.

2. **Database Schema**: All tables (tasks, tags, task_tag_link) exist with the schema defined in the constitution.

3. **404 vs 403 for Unauthorized Access**: Return 404 Not Found (not 403 Forbidden) when users try to access other users' resources to prevent resource enumeration attacks.

4. **Tag Listing Not Paginated**: GET /api/v1/tags returns all tags without pagination. Assumption: users will have < 100 tags typically.

5. **Search Implementation**: Full-text search uses SQL ILIKE pattern matching. More sophisticated search (PostgreSQL full-text, Elasticsearch) is deferred to future phases.

6. **Sort Field Validation**: Invalid sort fields return 400 error rather than silently ignoring.

7. **Idempotent Operations**: Tag association and dissociation are idempotent to simplify client logic.

8. **Null Due Dates in Sorting**: Tasks with null due_date appear last when sorting ascending, first when descending.

9. **Color Validation**: Tag color format is hex (#RRGGBB). Invalid formats are rejected with INVALID_COLOR error.

10. **Filter Combination**: All filters (status, priority, tag, q) combine with AND logic.

---

## 10. Out of Scope

The following items are explicitly excluded from this specification:

1. **Batch Operations**: Bulk create, update, or delete of tasks/tags.
2. **Task Ordering/Positioning**: Manual drag-and-drop ordering of tasks.
3. **Subtasks**: Hierarchical task structure with parent-child relationships.
4. **Task Dependencies**: Blocking relationships between tasks.
5. **Tag Hierarchy**: Nested or parent-child tag relationships.
6. **Task Sharing**: Sharing tasks or tags with other users.
7. **Task Comments**: Adding comments or notes to tasks.
8. **Task History/Audit Log**: Tracking changes to tasks over time.
9. **Recurring Task Execution**: Automatic creation of recurring task instances (RRULE parsing is available but execution is future scope).
10. **Due Date Reminders**: Notification endpoints (handled by frontend/separate feature).
11. **File Attachments**: Attaching files to tasks.
12. **Export/Import**: Exporting or importing tasks in various formats.
13. **Frontend Implementation**: This specification covers backend API only.

---

## 11. Testing Acceptance Criteria

### 11.1 Task CRUD Tests

| Test ID   | Description                                         | Expected Result                              |
| --------- | --------------------------------------------------- | -------------------------------------------- |
| TSK-001   | Create task with valid data                         | 201 Created, task object returned            |
| TSK-002   | Create task with only title (defaults applied)      | 201 Created, priority=medium, completed=false |
| TSK-003   | Create task with empty title                        | 400, INVALID_TITLE                           |
| TSK-004   | Create task with title > 200 chars                  | 400, INVALID_TITLE                           |
| TSK-005   | Create task with description > 1000 chars           | 400, DESCRIPTION_TOO_LONG                    |
| TSK-006   | Create task with invalid priority                   | 400, INVALID_PRIORITY                        |
| TSK-007   | Create task without auth token                      | 401, MISSING_TOKEN                           |
| TSK-008   | Get task list (empty)                               | 200, {items: [], total: 0}                   |
| TSK-009   | Get task list with tasks                            | 200, paginated response                      |
| TSK-010   | Get task list page 2                                | 200, correct offset applied                  |
| TSK-011   | Get single task (exists)                            | 200, task object                             |
| TSK-012   | Get single task (not exists)                        | 404, TASK_NOT_FOUND                          |
| TSK-013   | Get other user's task                               | 404, TASK_NOT_FOUND                          |
| TSK-014   | Update task (PUT) valid data                        | 200, updated task                            |
| TSK-015   | Update task (PUT) not found                         | 404, TASK_NOT_FOUND                          |
| TSK-016   | Update task (PATCH) completed only                  | 200, only completed changed                  |
| TSK-017   | Update other user's task                            | 404, TASK_NOT_FOUND                          |
| TSK-018   | Delete task (exists)                                | 204, empty response                          |
| TSK-019   | Delete task (not exists)                            | 404, TASK_NOT_FOUND                          |
| TSK-020   | Delete other user's task                            | 404, TASK_NOT_FOUND                          |

### 11.2 Task Filtering & Sorting Tests

| Test ID   | Description                                         | Expected Result                              |
| --------- | --------------------------------------------------- | -------------------------------------------- |
| FLT-001   | Filter by status=pending                            | Only incomplete tasks returned               |
| FLT-002   | Filter by status=completed                          | Only completed tasks returned                |
| FLT-003   | Filter by status=all                                | All tasks returned                           |
| FLT-004   | Filter by priority=high                             | Only high priority tasks returned            |
| FLT-005   | Filter by tag (ID)                                  | Only tasks with that tag returned            |
| FLT-006   | Filter by tag (name)                                | Only tasks with that tag returned            |
| FLT-007   | Search q=meeting                                    | Tasks with "meeting" in title/description    |
| FLT-008   | Combined filters (status + priority)                | Correct intersection returned                |
| FLT-009   | Invalid status value                                | 400, INVALID_STATUS                          |
| FLT-010   | Sort by due_date ascending                          | Correct order, nulls last                    |
| FLT-011   | Sort by -created_at (descending)                    | Newest first                                 |
| FLT-012   | Sort by priority                                    | High > medium > low                          |
| FLT-013   | Sort by title                                       | Alphabetical order                           |
| FLT-014   | Invalid sort field                                  | 400, INVALID_SORT_FIELD                      |
| FLT-015   | Pagination page=0                                   | 400, INVALID_PAGINATION                      |
| FLT-016   | Pagination limit > 100                              | limit capped at 100                          |

### 11.3 Tag CRUD Tests

| Test ID   | Description                                         | Expected Result                              |
| --------- | --------------------------------------------------- | -------------------------------------------- |
| TAG-001   | Create tag with valid data                          | 201 Created, tag object                      |
| TAG-002   | Create tag with duplicate name                      | 400, TAG_ALREADY_EXISTS                      |
| TAG-003   | Create tag with empty name                          | 400, INVALID_TAG_NAME                        |
| TAG-004   | Create tag with name > 50 chars                     | 400, INVALID_TAG_NAME                        |
| TAG-005   | Create tag with invalid color format                | 400, INVALID_COLOR                           |
| TAG-006   | List tags (empty)                                   | 200, []                                      |
| TAG-007   | List tags (with tags)                               | 200, array of tags                           |
| TAG-008   | List tags (only user's tags)                        | 200, data isolation verified                 |
| TAG-009   | Update tag valid data                               | 200, updated tag                             |
| TAG-010   | Update tag to duplicate name                        | 400, TAG_ALREADY_EXISTS                      |
| TAG-011   | Update tag not found                                | 404, TAG_NOT_FOUND                           |
| TAG-012   | Update other user's tag                             | 404, TAG_NOT_FOUND                           |
| TAG-013   | Delete tag exists                                   | 204, empty response                          |
| TAG-014   | Delete tag not found                                | 404, TAG_NOT_FOUND                           |
| TAG-015   | Delete other user's tag                             | 404, TAG_NOT_FOUND                           |

### 11.4 Task-Tag Association Tests

| Test ID   | Description                                         | Expected Result                              |
| --------- | --------------------------------------------------- | -------------------------------------------- |
| ASC-001   | Associate tag with task                             | 201, task with tag included                  |
| ASC-002   | Associate same tag again (idempotent)               | 200, no duplicate                            |
| ASC-003   | Associate non-existent tag                          | 404, TAG_NOT_FOUND                           |
| ASC-004   | Associate tag to non-existent task                  | 404, TASK_NOT_FOUND                          |
| ASC-005   | Associate other user's tag                          | 404, TAG_NOT_FOUND                           |
| ASC-006   | Dissociate tag from task                            | 204, empty response                          |
| ASC-007   | Dissociate non-associated tag (idempotent)          | 204, empty response                          |
| ASC-008   | Delete task removes associations                    | TaskTagLink entries deleted                  |
| ASC-009   | Delete tag removes associations                     | TaskTagLink entries deleted                  |

---

## 12. Glossary

| Term           | Definition                                                                 |
| -------------- | -------------------------------------------------------------------------- |
| CRUD           | Create, Read, Update, Delete - basic data operations                       |
| Data Isolation | Security principle ensuring users can only access their own data           |
| Eager Loading  | ORM pattern loading related entities in same query to avoid N+1            |
| Full Update    | PUT operation replacing all fields of a resource                           |
| Idempotent     | Operation producing same result regardless of repeated execution           |
| Junction Table | Database table implementing many-to-many relationship                      |
| N+1 Problem    | Performance issue where N additional queries are made for N related items  |
| Partial Update | PATCH operation modifying only specified fields                            |
| Resource Enumeration | Attack technique discovering valid IDs by observing different errors |

---

## 13. References

- Constitution: `.specify/memory/constitution.md` (Version 2.2.0)
- Prerequisite Spec: `/specs/001-foundational-backend-setup/spec.md`
- Section V: Backend Architecture Standards
- Section X: Feature Scope (Phase II)
- Data Model Specification (Constitution)
- Validation Rules (Constitution)
- API Design Standards (Constitution)

---

**Specification Status**: Complete
**Clarifications Required**: 0
**Validation Iterations**: 1
**Next Step**: Proceed to `/sp.plan` for implementation planning
