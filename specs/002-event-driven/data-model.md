# Data Model: Event-Driven Architecture

**Feature**: 002-event-driven
**Date**: 2026-01-01
**Status**: Complete

## Overview

This document defines the data models for event-driven task management, including enhanced task entities, event schemas, and service entities.

---

## Database Entities

### 1. Enhanced Task Model

**Table**: `tasks_phaseiii` (enhanced from Feature 001)

**Purpose**: Store task data with advanced features (priority, due dates, recurrence, search)

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks_phaseiii"

    # Primary key
    id: int = Field(primary_key=True)

    # User association (JWT scoped)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Core fields
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)

    # Advanced fields (NEW in Feature 001)
    priority: Optional[str] = Field(default=None, index=True)  # 'low', 'medium', 'high'
    due_date: Optional[datetime] = Field(default=None, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id", index=True)

    # Event-driven fields (NEW in this feature)
    recurrence_rule: Optional[str] = Field(default=None)  # iCalendar RRULE format
    reminder_sent: bool = Field(default=False, index=True)

    # Full-text search (NEW in Feature 001)
    search_vector: Optional[str] = Field(
        sa_column=Column(TSVECTOR, nullable=True)
    )

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)  # Soft delete

    # Metadata
    class Config:
        arbitrary_types_allowed = True
```

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks_phaseiii(user_id);
CREATE INDEX idx_tasks_completed ON tasks_phaseiii(completed);
CREATE INDEX idx_tasks_priority ON tasks_phaseiii(priority);
CREATE INDEX idx_tasks_due_date ON tasks_phaseiii(due_date);
CREATE INDEX idx_tasks_reminder_sent ON tasks_phaseiii(reminder_sent);
CREATE INDEX idx_tasks_category_id ON tasks_phaseiii(category_id);
CREATE INDEX idx_tasks_search USING GIN(search_vector);  -- Full-text search

-- Composite index for reminder query optimization
CREATE INDEX idx_tasks_reminder_query
ON tasks_phaseiii(due_date, reminder_sent, completed)
WHERE deleted_at IS NULL;
```

**Constraints**:
```sql
ALTER TABLE tasks_phaseiii
ADD CONSTRAINT check_priority
CHECK (priority IN ('low', 'medium', 'high') OR priority IS NULL);

ALTER TABLE tasks_phaseiii
ADD CONSTRAINT check_reminder_sent_requires_due_date
CHECK (reminder_sent = false OR due_date IS NOT NULL);
```

**Trigger** (auto-update search_vector):
```sql
CREATE TRIGGER task_search_update
BEFORE INSERT OR UPDATE ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger_column(
    search_vector,
    'pg_catalog.english',
    title,
    description
);
```

---

## Event Schemas (Pydantic Models)

All events use Pydantic v2 for validation and serialization to JSON for Kafka.

### Base Event

```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4

class BaseEvent(BaseModel):
    """Base event with common metadata"""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int
    schema_version: str = "1.0"

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "event_type": "task.created",
                "timestamp": "2025-01-15T10:30:00Z",
                "user_id": 42,
                "schema_version": "1.0"
            }]
        }
    }
```

### 1. TaskCreatedEvent

**Topic**: `task-events`
**Purpose**: Published when a new task is created via `add_task` MCP tool

```python
from typing import List, Optional

class TaskCreatedEvent(BaseEvent):
    event_type: str = Field(default="task.created", frozen=True)
    task_id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None  # 'low', 'medium', 'high'
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None  # iCalendar RRULE
    category_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "abc123",
                "event_type": "task.created",
                "timestamp": "2025-01-15T10:30:00Z",
                "user_id": 42,
                "task_id": 101,
                "title": "Weekly team meeting",
                "priority": "high",
                "due_date": "2025-01-20T14:00:00Z",
                "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
                "category_id": 5,
                "tag_ids": [1, 3]
            }]
        }
    }
```

### 2. TaskCompletedEvent

**Topic**: `task-recurrence`
**Purpose**: Published when a task is marked complete, triggers recurring task generation

```python
class TaskCompletedEvent(BaseEvent):
    event_type: str = Field(default="task.completed", frozen=True)
    task_id: int
    recurrence_rule: Optional[str] = None
    completed_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "def456",
                "event_type": "task.completed",
                "timestamp": "2025-01-15T16:45:00Z",
                "user_id": 42,
                "task_id": 101,
                "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
                "completed_at": "2025-01-15T16:45:00Z"
            }]
        }
    }
```

### 3. TaskUpdatedEvent

**Topic**: `task-events`
**Purpose**: Published when task metadata is modified via `update_task` MCP tool

```python
class TaskUpdatedEvent(BaseEvent):
    event_type: str = Field(default="task.updated", frozen=True)
    task_id: int
    updated_fields: dict  # Field name -> new value mapping

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "ghi789",
                "event_type": "task.updated",
                "timestamp": "2025-01-15T11:00:00Z",
                "user_id": 42,
                "task_id": 101,
                "updated_fields": {
                    "due_date": "2025-01-22T14:00:00Z",
                    "priority": "medium"
                }
            }]
        }
    }
```

### 4. TaskDeletedEvent

**Topic**: `task-events`
**Purpose**: Published when a task is deleted via `delete_task` MCP tool

```python
class TaskDeletedEvent(BaseEvent):
    event_type: str = Field(default="task.deleted", frozen=True)
    task_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "jkl012",
                "event_type": "task.deleted",
                "timestamp": "2025-01-15T12:00:00Z",
                "user_id": 42,
                "task_id": 101
            }]
        }
    }
```

### 5. ReminderSentEvent

**Topic**: `task-reminders`
**Purpose**: Published when a reminder notification is sent for a task

```python
class ReminderSentEvent(BaseEvent):
    event_type: str = Field(default="reminder.sent", frozen=True)
    task_id: int
    reminder_time: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_id": "mno345",
                "event_type": "reminder.sent",
                "timestamp": "2025-01-20T13:00:00Z",
                "user_id": 42,
                "task_id": 101,
                "reminder_time": "2025-01-20T13:00:00Z"
            }]
        }
    }
```

---

## Service Entities (Conceptual)

### 1. Notification Service

**Purpose**: Kafka consumer that monitors tasks with approaching due dates and sends reminders

**State**:
- Consumer group: `notification-service-group`
- Topics: `task-events`, `task-reminders`
- Processing logic: Poll database every 5 seconds for tasks due within 1 hour

**Data Flow**:
```
Database Query (every 5s)
  → SELECT * FROM tasks_phaseiii
    WHERE due_date <= now() + INTERVAL '1 hour'
      AND reminder_sent = false
      AND completed = false
      AND deleted_at IS NULL
  → Log reminder: "🔔 REMINDER: Task 'X' due in N minutes"
  → UPDATE tasks_phaseiii SET reminder_sent = true WHERE id = ?
  → Publish ReminderSentEvent to task-reminders topic
```

**Deployment**:
- Kubernetes Deployment: `notification-deployment.yaml`
- Replicas: 1 (MVP, avoid duplicate reminders)
- Resources: 200m CPU, 256Mi RAM
- Health checks: `/health` endpoint (checks Kafka + DB connectivity)

### 2. Recurring Task Service

**Purpose**: Kafka consumer that regenerates recurring tasks when completed

**State**:
- Consumer group: `recurring-task-service-group`
- Topics: `task-recurrence`
- Processing logic: Parse RRULE, calculate next occurrence, create new task

**Data Flow**:
```
TaskCompletedEvent from task-recurrence topic
  → Parse recurrence_rule with dateutil.rrule
  → Calculate next occurrence date
  → IF next occurrence is in the future:
      → Create new task in database with:
        - Same title, description, priority, category, tags, recurrence_rule
        - New due_date = next occurrence
        - completed = false, reminder_sent = false
      → Publish TaskCreatedEvent to task-events topic
  → ELSE (next occurrence in past or invalid RRULE):
      → Log error and skip
```

**Deployment**:
- Kubernetes Deployment: `recurring-deployment.yaml`
- Replicas: 1 (MVP, simplifies idempotency)
- Resources: 200m CPU, 256Mi RAM
- Health checks: `/health` endpoint

### 3. Search Service (Conceptual)

**Purpose**: Encapsulate full-text search logic for the `search_tasks` MCP tool

**State**:
- Stateless (queries database directly)
- No Kafka integration (synchronous query)

**Data Flow**:
```
search_tasks(user_id, query)
  → Convert query to tsquery: plainto_tsquery('english', query)
  → Execute SQL:
      SELECT * FROM tasks_phaseiii
      WHERE user_id = ? AND search_vector @@ tsquery
      ORDER BY ts_rank(search_vector, tsquery) DESC
      LIMIT 50
  → Return ranked results
```

**Implementation**:
- Function in `app/services/search_service.py`
- No separate deployment (part of backend service)

---

## Kafka Infrastructure

### Topic Configuration

| Topic | Partitions | Retention | Replication | Purpose |
|-------|-----------|-----------|-------------|---------|
| `task-events` | 3 | 7 days | 1 | Task lifecycle events (create, update, delete) |
| `task-reminders` | 1 | 1 day | 1 | Reminder notifications (audit trail) |
| `task-recurrence` | 1 | 7 days | 1 | Recurring task regeneration |

**Partition Strategy**:
- `task-events`: 3 partitions for parallel processing, keyed by `task_id` (ensures ordering per task)
- `task-reminders`: 1 partition (sequential processing, low volume)
- `task-recurrence`: 1 partition (sequential processing, ensures FIFO)

**Retention Policy**:
- `task-events`: 7 days (allows event replay for debugging)
- `task-reminders`: 1 day (audit trail only, low storage)
- `task-recurrence`: 7 days (allows reprocessing if service was down)

### Consumer Groups

| Group ID | Service | Topics | Offset Strategy |
|----------|---------|--------|-----------------|
| `notification-service-group` | Notification Service | `task-events`, `task-reminders` | Commit after each message |
| `recurring-task-service-group` | Recurring Task Service | `task-recurrence` | Commit after each message |

---

## Relationships

```
User (1) ─────< tasks_phaseiii (N)
                     │
                     │ (search_vector for FTS)
                     │
                     │ (triggers events)
                     ├──> TaskCreatedEvent ──> task-events topic
                     ├──> TaskUpdatedEvent ──> task-events topic
                     ├──> TaskCompletedEvent ──> task-recurrence topic
                     └──> TaskDeletedEvent ──> task-events topic

Notification Service
  │
  ├──> Polls database for tasks with due_date approaching
  ├──> Publishes ReminderSentEvent ──> task-reminders topic
  └──> Updates task.reminder_sent = true

Recurring Task Service
  │
  ├──> Consumes TaskCompletedEvent from task-recurrence topic
  ├──> Parses recurrence_rule (RRULE)
  ├──> Calculates next occurrence
  ├──> Creates new task in database
  └──> Publishes TaskCreatedEvent ──> task-events topic
```

---

## Migration Strategy

**Alembic Migration** (from Feature 001 baseline):

```python
# alembic/versions/YYYYMMDD_add_event_driven_fields.py

def upgrade():
    # Add recurrence_rule and reminder_sent fields
    op.add_column('tasks_phaseiii',
        sa.Column('recurrence_rule', sa.String(), nullable=True)
    )
    op.add_column('tasks_phaseiii',
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false')
    )

    # Create indexes
    op.create_index('idx_tasks_reminder_sent', 'tasks_phaseiii', ['reminder_sent'])

    # Composite index for reminder query
    op.execute("""
        CREATE INDEX idx_tasks_reminder_query
        ON tasks_phaseiii(due_date, reminder_sent, completed)
        WHERE deleted_at IS NULL;
    """)

def downgrade():
    op.drop_index('idx_tasks_reminder_query', 'tasks_phaseiii')
    op.drop_index('idx_tasks_reminder_sent', 'tasks_phaseiii')
    op.drop_column('tasks_phaseiii', 'reminder_sent')
    op.drop_column('tasks_phaseiii', 'recurrence_rule')
```

**NOTE**: Feature 001 migration already added `priority`, `due_date`, `category_id`, `search_vector`, and GIN index. This migration only adds event-driven fields.

---

## Validation Rules

### Task Model
- `priority`: Must be one of `'low'`, `'medium'`, `'high'`, or `None`
- `due_date`: Must be future date (or None)
- `recurrence_rule`: Must match RRULE whitelist patterns
- `reminder_sent`: Can only be `true` if `due_date` is set

### Event Schemas
- `event_id`: Must be valid UUID v4
- `timestamp`: Must be UTC datetime
- `user_id`: Must be positive integer
- `task_id`: Must reference existing task
- `recurrence_rule`: Must be valid RRULE format (validated on task creation)

---

## Summary

This data model supports:
1. **Enhanced Tasks**: Priority, due dates, recurrence, full-text search
2. **Event Streaming**: 5 event types with Pydantic validation
3. **Consumer Services**: Notification and Recurring Task services
4. **Kafka Infrastructure**: 3 topics, 2 consumer groups
5. **Database Optimization**: Indexes for reminder queries and FTS

All entities are ready for implementation in Phase 2 (tasks.md generation).
