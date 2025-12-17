# Phase 1: Data Model Specification

**Feature**: AI-Powered Conversational Task Management
**Branch**: `002-ai-chat-service-integration`
**Date**: 2025-12-17

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for Phase III conversational task management.

---

## Entity Definitions

### 1. Task (Phase III)

**Table Name**: `tasks_phaseiii`

**Purpose**: Represents a todo item managed through conversational interface. Completely separate from Phase II tasks table.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TaskPhaseIII(SQLModel, table=True):
    __tablename__ = "tasks_phaseiii"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTOINCREMENT | Unique task identifier |
| `user_id` | str | INDEXED, NOT NULL | Owner user ID from Better Auth |
| `title` | str | NOT NULL, max 200 chars | Task title |
| `description` | str | NULLABLE | Optional task description |
| `completed` | bool | NOT NULL, DEFAULT False | Completion status |
| `created_at` | datetime | NOT NULL, DEFAULT now() | Creation timestamp |
| `updated_at` | datetime | NOT NULL, DEFAULT now() | Last modification timestamp |

**Validation Rules**:
- **Title**: Required, 1-200 characters after trimming, cannot be whitespace-only
- **Description**: Optional, no length limit (simplified for Phase III)
- **User ID**: Required, must be valid Better Auth user ID
- **Completed**: Boolean, defaults to False

**Indexes**:
- `idx_tasks_phaseiii_user_id` on `user_id` - Fast user task lookup
- `idx_tasks_phaseiii_user_completed` on `(user_id, completed)` - Filter pending/completed tasks

**State Transitions**:
```
[Created] --complete_task()--> [Completed]
[Completed] --update_task()--> [Completed with new details]
[Created] --delete_task()--> [Deleted from DB]
[Completed] --delete_task()--> [Deleted from DB]
```

---

### 2. Conversation

**Table Name**: `conversations`

**Purpose**: Represents an ongoing dialogue session between a user and the AI assistant. Enables conversation continuity and context building.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTOINCREMENT | Unique conversation identifier |
| `user_id` | str | INDEXED, NOT NULL | Owner user ID from Better Auth |
| `created_at` | datetime | NOT NULL, DEFAULT now() | Conversation start timestamp |
| `updated_at` | datetime | NOT NULL, DEFAULT now() | Last activity timestamp |

**Validation Rules**:
- **User ID**: Required, must be valid Better Auth user ID
- **Timestamps**: Automatically managed by database

**Indexes**:
- `idx_conversations_user_id` on `user_id` - Fast user conversation lookup

**Lifecycle**:
- Created when user sends first message without conversation_id
- Updated timestamp refreshed on each new message
- Persisted indefinitely until user deletes
- Messages cascade-deleted when conversation deleted

---

### 3. Message

**Table Name**: `messages`

**Purpose**: Represents a single message exchange within a conversation. Stores both user messages and AI assistant responses.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, sa_type=Text)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTOINCREMENT | Unique message identifier |
| `conversation_id` | int | FOREIGN KEY → conversations.id, INDEXED | Parent conversation |
| `user_id` | str | INDEXED, NOT NULL | Owner user ID |
| `role` | str | NOT NULL, ENUM('user', 'assistant') | Message sender role |
| `content` | text | NOT NULL | Message content |
| `created_at` | datetime | NOT NULL, DEFAULT now() | Message timestamp |

**Validation Rules**:
- **Content**: Required, cannot be empty or whitespace-only
- **Role**: Must be 'user' or 'assistant'
- **Conversation ID**: Must reference existing conversation owned by user
- **User ID**: Must match conversation owner

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` - Fast message retrieval by conversation
- `idx_messages_user_id` on `user_id` - User message lookup

**Query Patterns**:
- Load last 20 messages for conversation context: `ORDER BY created_at DESC LIMIT 20`
- Count messages in conversation: `COUNT(*) WHERE conversation_id = ?`
- Get conversation history: `SELECT * WHERE conversation_id = ? ORDER BY created_at ASC`

---

### 4. User (Reference Only)

**Note**: User entity managed by Better Auth; not implemented in Phase III backend. Referenced via `user_id` string in all entities.

**Better Auth User Fields** (for reference):
- `id` (string) - Primary identifier
- `email` (string) - User email
- `name` (string) - Display name
- `created_at` (datetime) - Account creation

**Usage in Phase III**:
- All entities store `user_id` as a string foreign key reference
- Backend validates `user_id` from JWT token
- No direct database relationship to Better Auth user table

---

## Entity Relationships

### ERD Diagram (Text Format)

```
┌──────────────────┐
│  User            │
│  (Better Auth)   │
└────────┬─────────┘
         │
         │ 1:N (owner)
         │
    ┌────┴────────────────────┬─────────────────────┐
    │                         │                     │
    ▼                         ▼                     ▼
┌───────────────┐     ┌─────────────────┐   ┌──────────────┐
│ TaskPhaseIII  │     │  Conversation   │   │   Message    │
├───────────────┤     ├─────────────────┤   ├──────────────┤
│ id            │     │ id              │◄──┤ conversation │
│ user_id       │     │ user_id         │   │   _id (FK)   │
│ title         │     │ created_at      │   │ user_id      │
│ description   │     │ updated_at      │   │ role         │
│ completed     │     └─────────────────┘   │ content      │
│ created_at    │              │            │ created_at   │
│ updated_at    │              │ 1:N        └──────────────┘
└───────────────┘              │
                               ▼
                        [Multiple Messages
                         per Conversation]
```

### Relationship Summary

1. **User → TaskPhaseIII**: One-to-Many
   - One user owns many tasks
   - Tasks scoped by `user_id`
   - No foreign key constraint (user in external Better Auth DB)

2. **User → Conversation**: One-to-Many
   - One user owns many conversations
   - Conversations scoped by `user_id`
   - No foreign key constraint (user in external Better Auth DB)

3. **Conversation → Message**: One-to-Many
   - One conversation contains many messages
   - Foreign key constraint with CASCADE delete
   - Messages ordered chronologically by `created_at`

4. **User → Message**: One-to-Many (indirect)
   - Messages inherit user ownership from conversation
   - `message.user_id` must equal `conversation.user_id`
   - Enables user-scoped message queries

---

## Validation Rules

### Task Validation

**Title Validation**:
```python
def validate_task_title(title: str) -> str:
    """Validate and sanitize task title."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required and cannot be whitespace-only")
    if len(title) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    return title
```

**Error Response**:
```json
{
  "detail": "Title is required and must be 1-200 characters",
  "code": "INVALID_TITLE",
  "field": "title"
}
```

### Message Validation

**Content Validation**:
```python
def validate_message_content(content: str) -> str:
    """Validate message content."""
    content = content.strip()
    if not content:
        raise ValueError("Message content is required")
    return content
```

**Error Response**:
```json
{
  "detail": "Message is required and cannot be empty",
  "code": "INVALID_MESSAGE",
  "field": "content"
}
```

### Conversation Validation

**Conversation ID Validation**:
```python
async def validate_conversation_ownership(
    conversation_id: int,
    user_id: str,
    db: AsyncSession
) -> Conversation:
    """Validate conversation exists and belongs to user."""
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404, detail="Conversation not found")
    if conversation.user_id != user_id:
        raise HTTPException(403, detail="Conversation access denied")
    return conversation
```

**Error Responses**:
```json
// Not found
{
  "detail": "Conversation not found",
  "code": "CONVERSATION_NOT_FOUND"
}

// Access denied
{
  "detail": "Conversation access denied",
  "code": "CONVERSATION_ACCESS_DENIED"
}
```

---

## State Transitions

### Task State Machine

```
┌─────────────────────────────────────────────────────┐
│                    Task Lifecycle                    │
└─────────────────────────────────────────────────────┘

[New Task Request]
       │
       ▼
   add_task(user_id, title, description?)
       │
       ▼
┌──────────────────┐
│  Task Created    │
│  completed=False │
└──────┬───────────┘
       │
       ├──► update_task(task_id, title?, description?)
       │         │
       │         └──► [Task Updated, still completed=False]
       │
       ├──► complete_task(task_id)
       │         │
       │         ▼
       │    ┌────────────────┐
       │    │ Task Completed │
       │    │ completed=True │
       │    └────┬───────────┘
       │         │
       │         └──► update_task(task_id, ...)
       │                  │
       │                  └──► [Task Updated, still completed=True]
       │
       └──► delete_task(task_id)
                 │
                 ▼
           [Task Deleted from DB]
```

**Transition Rules**:
- **Created → Updated**: Allowed anytime via `update_task()`
- **Created → Completed**: Via `complete_task()` - sets `completed=True`
- **Completed → Updated**: Allowed via `update_task()` - keeps `completed=True`
- **Any State → Deleted**: Via `delete_task()` - removes from database
- **Completed → Created**: Not supported (no un-complete operation)

### Conversation State Machine

```
[User Sends First Message Without conversation_id]
       │
       ▼
   Create New Conversation
       │
       ▼
┌──────────────────────┐
│  Active Conversation │
│  (id assigned)       │
└──────┬───────────────┘
       │
       ├──► User sends message
       │         │
       │         └──► Store user message → Invoke AI → Store assistant message
       │                  │
       │                  └──► Update conversation.updated_at
       │
       ├──► User continues with conversation_id
       │         │
       │         └──► Load history → Process → Store new messages
       │
       └──► User deletes conversation
                 │
                 ▼
           [Conversation & All Messages Deleted]
```

**Transition Rules**:
- **New → Active**: First message creates conversation, assigns ID
- **Active → Active**: Each message updates `updated_at` timestamp
- **Active → Deleted**: User-initiated deletion (future feature)
- **Messages**: Added incrementally, never updated (immutable log)

---

## Database Indexes (Performance Optimization)

### Primary Indexes

| Table | Index Name | Columns | Purpose |
|-------|------------|---------|---------|
| `tasks_phaseiii` | `idx_tasks_phaseiii_user_id` | `user_id` | Fast user task lookup |
| `tasks_phaseiii` | `idx_tasks_phaseiii_user_completed` | `(user_id, completed)` | Filter pending/completed |
| `conversations` | `idx_conversations_user_id` | `user_id` | Fast user conversation lookup |
| `messages` | `idx_messages_conversation_id` | `conversation_id` | Message history retrieval |
| `messages` | `idx_messages_user_id` | `user_id` | User message queries |

### Query Performance Expectations

| Query | Expected Performance | Index Used |
|-------|---------------------|------------|
| List user tasks | < 50ms | `idx_tasks_phaseiii_user_id` |
| Filter pending tasks | < 50ms | `idx_tasks_phaseiii_user_completed` |
| Load conversation messages | < 100ms | `idx_messages_conversation_id` |
| List user conversations | < 50ms | `idx_conversations_user_id` |

---

## Data Migration Strategy

### Initial Migration (Alembic)

**Migration File**: `phaseIII/backend/alembic/versions/001_initial_schema.py`

**Upgrade Operations**:
1. Create `tasks_phaseiii` table with indexes
2. Create `conversations` table with indexes
3. Create `messages` table with foreign key to `conversations` and indexes

**Downgrade Operations**:
1. Drop `messages` table
2. Drop `conversations` table
3. Drop `tasks_phaseiii` table

### Data Isolation Guarantees

- **No Phase II Imports**: Phase III does not read or write Phase II `tasks` table
- **Separate Alembic History**: Independent migration management
- **Table Naming**: `tasks_phaseiii` prevents accidental Phase II queries
- **Testing**: Integration tests verify data isolation between phases

---

## Data Access Patterns

### Common Query Patterns

**1. Load Conversation with Messages (Context Building)**:
```python
async def get_conversation_with_messages(
    conversation_id: int,
    user_id: str,
    db: AsyncSession,
    limit: int = 20
) -> tuple[Conversation, list[Message]]:
    """Load conversation and last N messages for AI context."""
    # Validate ownership
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(404, "Conversation not found")

    # Load last N messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()  # Chronological order for AI context

    return conversation, messages
```

**2. List User Tasks with Filter**:
```python
async def list_user_tasks(
    user_id: str,
    db: AsyncSession,
    status: str = "all"  # all | pending | completed
) -> list[TaskPhaseIII]:
    """List tasks with optional status filter."""
    query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

    if status == "pending":
        query = query.where(TaskPhaseIII.completed == False)
    elif status == "completed":
        query = query.where(TaskPhaseIII.completed == True)

    query = query.order_by(TaskPhaseIII.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()
```

**3. Create Task**:
```python
async def create_task(
    user_id: str,
    title: str,
    description: str | None,
    db: AsyncSession
) -> TaskPhaseIII:
    """Create new task with validation."""
    title = validate_task_title(title)

    task = TaskPhaseIII(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

---

## Data Model Completion Checklist

- [x] All entities defined with SQLModel schemas
- [x] Field types, constraints, and defaults specified
- [x] Validation rules documented with error responses
- [x] Entity relationships and cardinality defined
- [x] State transitions documented with rules
- [x] Database indexes specified for performance
- [x] Migration strategy outlined
- [x] Common query patterns provided
- [x] Data isolation from Phase II guaranteed
- [x] ERD diagram created

**Status**: Data model complete. Ready for API contract generation (Phase 1 continued).
