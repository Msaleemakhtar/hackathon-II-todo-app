# Data Model: Better Auth Integration

**Feature**: Better Auth Integration
**Date**: 2025-12-10
**Status**: Completed

## Overview

This document specifies the data model changes required for the Better Auth integration. The implementation maintains the existing User, Task, and Tag entities while ensuring proper authentication and data isolation between users.

## Entity Relationships

```
User (1) --- (Many) Task
User (1) --- (Many) Tag
Task (Many) --- (Many) Tag (via TaskTagLink)
```

## User Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PRIMARY KEY | UUID from Better Auth |
| email | str | UNIQUE, NOT NULL | User's email address |
| name | str | NULLABLE | User's display name |
| created_at | datetime | NOT NULL, DEFAULT now() | Account creation timestamp |

### Validation Rules
- All fields except `name` and `created_at` are required
- Email must be unique across all users
- Email format must be valid
- ID must be a valid UUID format provided by Better Auth

## Task Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PRIMARY KEY, AUTOINCREMENT | Unique task identifier |
| title | str | NOT NULL, 1-200 chars | Task title |
| description | str | NULLABLE, max 1000 chars | Detailed description |
| completed | bool | NOT NULL, DEFAULT False | Completion status |
| priority | str | NOT NULL, DEFAULT 'medium' | Enum: 'low', 'medium', 'high' |
| due_date | datetime | NULLABLE | Task due date and time |
| recurrence_rule | str | NULLABLE | iCal RRULE string |
| user_id | str | FOREIGN KEY -> User.id, NOT NULL | Task owner |
| created_at | datetime | NOT NULL, DEFAULT now() | Creation timestamp |
| updated_at | datetime | NOT NULL, DEFAULT now(), ON UPDATE | Last modification timestamp |

### Validation Rules
- Title required and 1-200 characters after trimming
- Description cannot exceed 1000 characters
- Priority must be one of: 'low', 'medium', 'high' (default: 'medium')
- Due date must be a valid ISO 8601 datetime (optional)
- Recurrence rule must be a valid iCal RRULE (optional)
- User_id must correspond to an existing user

### Indexes
- `idx_tasks_user_id` on tasks(user_id) - User task lookup
- `idx_tasks_user_completed` on tasks(user_id, completed) - Filtered task lists
- `idx_tasks_user_priority` on tasks(user_id, priority) - Priority sorting
- `idx_tasks_user_due_date` on tasks(user_id, due_date) - Due date sorting

## Tag Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PRIMARY KEY, AUTOINCREMENT | Unique tag identifier |
| name | str | NOT NULL, max 50 chars | Tag display name |
| color | str | NULLABLE, hex format | Tag color for UI display |
| user_id | str | FOREIGN KEY -> User.id, NOT NULL | Owner of the tag |
| created_at | datetime | NOT NULL, DEFAULT now() | Creation timestamp |

### Validation Rules
- Name required and 1-50 characters after trimming
- Color must be valid hex format if provided
- User_id must correspond to an existing user
- No duplicate tag names per user (UNIQUE constraint on name + user_id)

### Indexes
- `idx_tags_user_id` on tags(user_id) - User tag lookup

## TaskTagLink Entity (Junction Table)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | int | FOREIGN KEY -> Task.id, PRIMARY KEY | Task reference |
| tag_id | int | FOREIGN KEY -> Tag.id, PRIMARY KEY | Tag reference |

### Validation Rules
- task_id must correspond to an existing task
- tag_id must correspond to an existing tag
- Composite PRIMARY KEY(task_id, tag_id) prevents duplicate relationships

### Indexes
- `idx_task_tag_link_task` on task_tag_link(task_id) - Tag lookup by task
- `idx_task_tag_link_tag` on task_tag_link(tag_id) - Task lookup by tag

## Authentication-Specific Considerations

### User Identity
- User.id is populated with the UUID provided by Better Auth
- User.email is used for authentication and must match the email in Better Auth
- User.name is optional and can be populated from Better Auth if provided

### Data Isolation
- All queries must be scoped to the authenticated user's JWT user_id
- Path parameter validation ensures user_id in URL matches JWT user_id
- Foreign key constraints ensure referential integrity

### Security Requirements
- All operations require valid JWT token
- User can only access/modify their own data
- Path parameter validation prevents URL manipulation attacks