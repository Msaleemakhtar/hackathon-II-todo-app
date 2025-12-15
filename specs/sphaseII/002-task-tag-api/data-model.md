# Data Model for 002-task-tag-api

This data model defines the entities and their relationships for the Task and Tag management features, based on the feature specification and the project's constitution.

## 1. User Entity (from Constitution)

The `User` entity is managed by the authentication system and is referenced by `Task` and `Tag` for data ownership.

| Field      | Type     | Constraints                          | Description                         |
|------------|----------|--------------------------------------|-------------------------------------|
| id         | `str`    | PRIMARY KEY                          | User ID from Better Auth            |
| email      | `str`    | UNIQUE, NOT NULL                     | User's email address                |
| name       | `str`    | NULLABLE                             | User's display name                 |
| created_at | `datetime` | NOT NULL, DEFAULT `now()`            | Account creation timestamp          |

## 2. Tag Entity (SQLModel)

Represents a categorization label for tasks.

| Field    | Type     | Constraints                          | Description                         |
|----------|----------|--------------------------------------|-------------------------------------|
| id       | `int`    | PRIMARY KEY, AUTOINCREMENT           | Unique tag identifier               |
| name     | `str`    | NOT NULL, max 50 chars               | Tag display name                    |
| color    | `str`    | NULLABLE, hex format                 | Tag color for UI display            |
| user_id  | `str`    | FOREIGN KEY -> User.id, NOT NULL     | Owner of the tag                    |

**Constraints**:
- `UNIQUE(name, user_id)`: No duplicate tag names per user.

## 3. Task Entity (SQLModel)

Represents a todo item.

| Field           | Type         | Constraints                          | Description                         |
|-----------------|--------------|--------------------------------------|-------------------------------------|
| id              | `int`        | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier              |
| title           | `str`        | NOT NULL, 1-200 chars                | Task title                          |
| description     | `str`        | NULLABLE, max 1000 chars             | Detailed description                |
| completed       | `bool`       | NOT NULL, DEFAULT `False`            | Completion status                   |
| priority        | `str`        | NOT NULL, DEFAULT `'medium'`         | Enum: `'low'`, `'medium'`, `'high'` |
| due_date        | `datetime`   | NULLABLE                             | Task due date and time              |
| recurrence_rule | `str`        | NULLABLE                             | iCal RRULE string                   |
| user_id         | `str`        | FOREIGN KEY -> User.id, NOT NULL     | Task owner                          |
| created_at      | `datetime`   | NOT NULL, DEFAULT `now()`            | Creation timestamp                  |
| updated_at      | `datetime`   | NOT NULL, DEFAULT `now()`, ON UPDATE | Last modification timestamp         |
| tags            | `List[Tag]`  | Many-to-Many via TaskTagLink         | Associated tags                     |

## 4. TaskTagLink Entity (Junction Table for Many-to-Many)

Links `Task` and `Tag` entities.

| Field   | Type  | Constraints                          | Description                         |
|---------|-------|--------------------------------------|-------------------------------------|
| task_id | `int` | FOREIGN KEY -> Task.id, PRIMARY KEY  | Reference to the Task               |
| tag_id  | `int` | FOREIGN KEY -> Tag.id, PRIMARY KEY   | Reference to the Tag                |

**Constraints**:
- Composite `PRIMARY KEY(task_id, tag_id)`

## 5. Database Indexes (from Constitution)

The following indexes are crucial for performance, especially with data isolation and filtering.

- `idx_tasks_user_id` on `tasks(user_id)`
- `idx_tasks_user_completed` on `tasks(user_id, completed)`
- `idx_tasks_user_priority` on `tasks(user_id, priority)`
- `idx_tasks_user_due_date` on `tasks(user_id, due_date)`
- `idx_tags_user_id` on `tags(user_id)`
- `idx_task_tag_link_task` on `task_tag_link(task_id)`
- `idx_task_tag_link_tag` on `task_tag_link(tag_id)`
