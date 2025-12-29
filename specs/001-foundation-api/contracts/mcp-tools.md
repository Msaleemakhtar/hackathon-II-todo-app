# MCP Tools API Contract

**Feature**: 001-foundation-api
**Date**: 2025-12-30
**Protocol**: Model Context Protocol (MCP)
**Total Tools**: 17 (5 enhanced + 12 new)

## Overview

This document defines the contract for all 17 MCP tools in the Phase V advanced task management system. Tools follow MCP protocol conventions with typed parameters and structured responses.

---

## Tool Categories

### Core Task Management (5 Enhanced)
1. `add_task` - Create new task with advanced fields
2. `list_tasks` - Retrieve tasks with filtering and search
3. `update_task` - Modify task with advanced fields
4. `delete_task` - Remove task
5. `get_task` - Retrieve single task by ID

### Category Management (4 New)
6. `create_category` - Create new category
7. `list_categories` - Retrieve all user categories
8. `update_category` - Modify category
9. `delete_category` - Remove category

### Tag Management (6 New)
10. `create_tag` - Create new tag
11. `list_tags` - Retrieve all user tags
12. `update_tag` - Modify tag
13. `delete_tag` - Remove tag
14. `add_tag_to_task` - Assign tag to task
15. `remove_tag_from_task` - Remove tag from task

### Advanced Features (2 New)
16. `search_tasks` - Full-text search across task titles/descriptions
17. `set_reminder` - Configure reminder for task

---

## Core Task Management Tools (Enhanced)

### 1. add_task (ENHANCED)

**Description**: Create a new task with advanced features (priority, due date, category, tags, recurrence)

**Input Schema**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional)",
  "priority": "enum (optional, default: 'medium')",
  "due_date": "ISO 8601 datetime (optional)",
  "category_id": "integer (optional)",
  "tag_ids": "array<integer> (optional, max 10)",
  "recurrence_rule": "string (optional, iCal RRULE format)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "user_id": "string",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "priority": "enum (low|medium|high|urgent)",
  "due_date": "ISO 8601 datetime | null",
  "category_id": "integer | null",
  "category": {
    "id": "integer",
    "name": "string",
    "color": "string | null"
  } | null,
  "tags": [
    {
      "id": "integer",
      "name": "string",
      "color": "string | null"
    }
  ],
  "recurrence_rule": "string | null",
  "reminder_sent": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Error Codes**:
- `400` - Invalid input (title too long, invalid priority, invalid RRULE, invalid due_date format, too many tags)
- `404` - Category or tag not found
- `403` - Category or tag belongs to different user
- `500` - Database error

**Example Usage**:
```python
# Create high priority task with due date and tags
result = await mcp_client.call_tool("add_task", {
    "title": "Prepare Q1 presentation",
    "description": "Create slides for board meeting",
    "priority": "high",
    "due_date": "2025-01-15T17:00:00-05:00",
    "category_id": 5,
    "tag_ids": [1, 3, 7]  # #urgent, #presentation, #board
})
```

---

### 2. list_tasks (ENHANCED)

**Description**: Retrieve tasks with filtering, sorting, and pagination

**Input Schema**:
```json
{
  "status": "enum (optional: 'all'|'pending'|'completed', default: 'all')",
  "priority": "enum (optional: 'low'|'medium'|'high'|'urgent')",
  "category_id": "integer (optional)",
  "tag_ids": "array<integer> (optional)",
  "due_before": "ISO 8601 datetime (optional)",
  "due_after": "ISO 8601 datetime (optional)",
  "sort_by": "enum (optional: 'created_at'|'updated_at'|'due_date'|'priority'|'title', default: 'created_at')",
  "sort_order": "enum (optional: 'asc'|'desc', default: 'desc')",
  "limit": "integer (optional, default: 50, max: 100)",
  "offset": "integer (optional, default: 0)"
}
```

**Output Schema**:
```json
{
  "tasks": [
    {
      "id": "integer",
      "title": "string",
      "description": "string | null",
      "completed": "boolean",
      "priority": "enum",
      "due_date": "ISO 8601 datetime | null",
      "category": { "id": "integer", "name": "string", "color": "string | null" } | null,
      "tags": [ { "id": "integer", "name": "string", "color": "string | null" } ],
      "recurrence_rule": "string | null",
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ],
  "total": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

**Filtering Logic**:
- Multiple filters use AND logic between different filter types
- `tag_ids` filter uses OR logic (task matches if it has ANY of the specified tags)
- `status='pending'` returns tasks where `completed=false`
- `status='completed'` returns tasks where `completed=true`
- `status='all'` returns all tasks

**Error Codes**:
- `400` - Invalid input (invalid sort_by, limit > 100, negative offset)
- `404` - Category or tag not found
- `500` - Database error

---

### 3. update_task (ENHANCED)

**Description**: Update task fields (partial updates supported)

**Input Schema**:
```json
{
  "task_id": "integer (required)",
  "title": "string (optional, 1-200 chars)",
  "description": "string | null (optional)",
  "completed": "boolean (optional)",
  "priority": "enum (optional)",
  "due_date": "ISO 8601 datetime | null (optional)",
  "category_id": "integer | null (optional)",
  "recurrence_rule": "string | null (optional)"
}
```

**Output Schema**: Same as `add_task` output

**Behavior**:
- Only provided fields are updated (partial update)
- Setting `category_id=null` removes category assignment
- Setting `due_date=null` removes due date
- `tag_ids` are updated via separate `add_tag_to_task` / `remove_tag_from_task` tools
- `updated_at` timestamp is automatically updated

**Error Codes**:
- `400` - Invalid input
- `404` - Task, category not found
- `403` - Task or category belongs to different user
- `500` - Database error

---

### 4. delete_task (UNCHANGED)

**Description**: Delete a task by ID

**Input Schema**:
```json
{
  "task_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "deleted_task_id": "integer"
}
```

**Behavior**:
- Deletes task and all associated tag relationships (CASCADE)
- Idempotent: deleting non-existent task returns 404

**Error Codes**:
- `404` - Task not found
- `403` - Task belongs to different user
- `500` - Database error

---

### 5. get_task (UNCHANGED)

**Description**: Retrieve a single task by ID with full details

**Input Schema**:
```json
{
  "task_id": "integer (required)"
}
```

**Output Schema**: Same as `add_task` output

**Error Codes**:
- `404` - Task not found
- `403` - Task belongs to different user
- `500` - Database error

---

## Category Management Tools (New)

### 6. create_category

**Description**: Create a new category

**Input Schema**:
```json
{
  "name": "string (required, 1-50 chars, unique per user)",
  "color": "string (optional, hex format #RRGGBB)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "user_id": "string",
  "name": "string",
  "color": "string | null",
  "created_at": "ISO 8601 datetime"
}
```

**Error Codes**:
- `400` - Invalid input (name too long, invalid color format, duplicate name, 50-category limit exceeded)
- `409` - Category with this name already exists for user
- `500` - Database error

---

### 7. list_categories

**Description**: Retrieve all categories for the authenticated user

**Input Schema**:
```json
{
  "sort_by": "enum (optional: 'name'|'created_at', default: 'created_at')",
  "sort_order": "enum (optional: 'asc'|'desc', default: 'asc')"
}
```

**Output Schema**:
```json
{
  "categories": [
    {
      "id": "integer",
      "name": "string",
      "color": "string | null",
      "task_count": "integer",
      "created_at": "ISO 8601 datetime"
    }
  ],
  "total": "integer"
}
```

**Behavior**:
- `task_count` is computed via JOIN (count of tasks in each category)
- Returns empty array if no categories exist

---

### 8. update_category

**Description**: Update category name or color

**Input Schema**:
```json
{
  "category_id": "integer (required)",
  "name": "string (optional, 1-50 chars)",
  "color": "string | null (optional)"
}
```

**Output Schema**: Same as `create_category` output

**Error Codes**:
- `400` - Invalid input
- `404` - Category not found
- `403` - Category belongs to different user
- `409` - New name conflicts with existing category
- `500` - Database error

---

### 9. delete_category

**Description**: Delete a category (sets category_id=NULL on associated tasks)

**Input Schema**:
```json
{
  "category_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "deleted_category_id": "integer",
  "tasks_affected": "integer"
}
```

**Behavior**:
- Sets `category_id=NULL` on all tasks in this category (ON DELETE SET NULL)
- Tasks remain but lose category assignment

**Error Codes**:
- `404` - Category not found
- `403` - Category belongs to different user
- `500` - Database error

---

## Tag Management Tools (New)

### 10. create_tag

**Description**: Create a new tag

**Input Schema**:
```json
{
  "name": "string (required, 1-30 chars, unique per user)",
  "color": "string (optional, hex format #RRGGBB)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "user_id": "string",
  "name": "string",
  "color": "string | null",
  "created_at": "ISO 8601 datetime"
}
```

**Error Codes**:
- `400` - Invalid input (name too long, invalid color format, duplicate name, 100-tag limit exceeded)
- `409` - Tag with this name already exists for user
- `500` - Database error

---

### 11. list_tags

**Description**: Retrieve all tags for the authenticated user

**Input Schema**:
```json
{
  "sort_by": "enum (optional: 'name'|'created_at', default: 'created_at')",
  "sort_order": "enum (optional: 'asc'|'desc', default: 'asc')"
}
```

**Output Schema**:
```json
{
  "tags": [
    {
      "id": "integer",
      "name": "string",
      "color": "string | null",
      "task_count": "integer",
      "created_at": "ISO 8601 datetime"
    }
  ],
  "total": "integer"
}
```

**Behavior**:
- `task_count` is computed via JOIN (count of tasks with each tag)

---

### 12. update_tag

**Description**: Update tag name or color

**Input Schema**:
```json
{
  "tag_id": "integer (required)",
  "name": "string (optional, 1-30 chars)",
  "color": "string | null (optional)"
}
```

**Output Schema**: Same as `create_tag` output

**Error Codes**:
- `400` - Invalid input
- `404` - Tag not found
- `403` - Tag belongs to different user
- `409` - New name conflicts with existing tag
- `500` - Database error

---

### 13. delete_tag

**Description**: Delete a tag (removes from all tasks)

**Input Schema**:
```json
{
  "tag_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "deleted_tag_id": "integer",
  "tasks_affected": "integer"
}
```

**Behavior**:
- Deletes all task-tag associations (ON DELETE CASCADE)
- Tasks remain but lose this tag

---

### 14. add_tag_to_task

**Description**: Assign a tag to a task

**Input Schema**:
```json
{
  "task_id": "integer (required)",
  "tag_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "task_id": "integer",
  "tag_id": "integer"
}
```

**Behavior**:
- Idempotent: adding same tag twice succeeds (no duplicate entry due to PRIMARY KEY)
- Enforces 10-tag limit per task

**Error Codes**:
- `400` - 10-tag limit exceeded
- `404` - Task or tag not found
- `403` - Task or tag belongs to different user
- `500` - Database error

---

### 15. remove_tag_from_task

**Description**: Remove a tag from a task

**Input Schema**:
```json
{
  "task_id": "integer (required)",
  "tag_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "task_id": "integer",
  "tag_id": "integer"
}
```

**Behavior**:
- Idempotent: removing non-existent tag succeeds (no error)

**Error Codes**:
- `404` - Task or tag not found
- `403` - Task or tag belongs to different user
- `500` - Database error

---

## Advanced Feature Tools (New)

### 16. search_tasks

**Description**: Full-text search across task titles and descriptions with relevance ranking

**Input Schema**:
```json
{
  "query": "string (required, search keywords)",
  "category_id": "integer (optional, filter results by category)",
  "priority": "enum (optional, filter results by priority)",
  "tag_ids": "array<integer> (optional, filter results by tags)",
  "limit": "integer (optional, default: 20, max: 100)",
  "offset": "integer (optional, default: 0)"
}
```

**Output Schema**:
```json
{
  "tasks": [
    {
      "id": "integer",
      "title": "string",
      "description": "string | null",
      "completed": "boolean",
      "priority": "enum",
      "due_date": "ISO 8601 datetime | null",
      "category": { "id": "integer", "name": "string", "color": "string | null" } | null,
      "tags": [ { "id": "integer", "name": "string", "color": "string | null" } ],
      "relevance_score": "float",
      "created_at": "ISO 8601 datetime"
    }
  ],
  "total": "integer",
  "query": "string"
}
```

**Behavior**:
- Uses PostgreSQL `ts_rank()` for relevance scoring
- Title matches rank higher than description matches
- Results sorted by relevance score (descending)
- Filters (category, priority, tags) use AND logic with search query
- Empty query returns all tasks (sorted by created_at)

**Error Codes**:
- `400` - Invalid input
- `500` - Database error

---

### 17. set_reminder

**Description**: Configure a reminder for a task (stores reminder metadata; actual notification sending deferred to 002-event-streaming)

**Input Schema**:
```json
{
  "task_id": "integer (required)",
  "remind_before_minutes": "integer (required, minutes before due_date)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "task_id": "integer",
  "remind_at": "ISO 8601 datetime"
}
```

**Behavior**:
- Requires task to have `due_date` set
- Calculates `remind_at = due_date - remind_before_minutes`
- Stores reminder metadata (implementation TBD in 002-event-streaming)
- This tool in 001 only validates inputs; actual reminder logic in future feature

**Error Codes**:
- `400` - Task has no due_date or invalid remind_before_minutes
- `404` - Task not found
- `403` - Task belongs to different user
- `500` - Database error

---

## Common Response Patterns

### Success Response
```json
{
  "success": true,
  "data": { /* tool-specific output */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable error message",
    "field": "optional_field_name"
  }
}
```

### Error Code Mapping

| HTTP Status | MCP Error Code | Description |
|-------------|----------------|-------------|
| 400 | INVALID_INPUT | Validation failed (bad format, missing required fields) |
| 401 | UNAUTHORIZED | Missing or invalid JWT token |
| 403 | FORBIDDEN | User attempting to access resource owned by another user |
| 404 | NOT_FOUND | Resource (task, category, tag) not found |
| 409 | CONFLICT | Duplicate name (category/tag with same name already exists) |
| 422 | VALIDATION_ERROR | Business rule violation (10-tag limit, 50-category limit, etc.) |
| 500 | INTERNAL_ERROR | Database error or unexpected server error |

---

## Authentication & Authorization

All MCP tools require:
1. **JWT Token**: Valid Better Auth JWT token in request context
2. **User Scoping**: All database queries filtered by `user_id` from JWT (NOT path parameter)
3. **Path Validation**: For endpoints with `user_id` in path, JWT user_id must match

Example FastAPI dependency:
```python
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Extract and validate user ID from JWT token."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id
```

---

## Testing Requirements

Each MCP tool MUST have:
1. **Unit tests** for tool function logic
2. **Integration tests** with test database
3. **Error case tests** for all error codes
4. **Multi-user isolation tests** (User A cannot access User B's data)
5. **Validation tests** for all input constraints

Minimum test coverage: **80%** for all MCP tool functions.

---

**End of API Contract**
