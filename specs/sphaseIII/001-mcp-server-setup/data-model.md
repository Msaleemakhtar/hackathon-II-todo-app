# Data Model: MCP Server Implementation (Phase III)

**Feature**: MCP Server Implementation for Phase III
**Date**: 2025-12-17
**Status**: Design Complete

---

## Overview

This document defines the data models for Phase III's MCP server implementation. All models use SQLModel (SQLAlchemy + Pydantic) with async operations via asyncpg driver. The models are completely independent from Phase II, using separate tables (`tasks_phaseiii`, `conversations`, `messages`) to maintain phase separation per Constitution Principle II.

---

## Entity Relationships

```
User (from Better Auth)
  │
  ├──► Task (tasks_phaseiii) [1:N]
  │     - User owns multiple tasks
  │     - Tasks scoped to user_id
  │
  ├──► Conversation [1:N]
  │     - User owns multiple conversations
  │     - Conversations scoped to user_id
  │
  └──► Message [1:N via Conversation]
        - Messages belong to conversations
        - Messages scoped to user_id for redundant isolation
        - Foreign key: conversation_id → conversations.id
```

---

## 1. Task Entity (Phase III)

### Table Name: `tasks_phaseiii`

**Purpose**: Represents a todo item managed through MCP tools. Completely separate from Phase II tasks table.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| `user_id` | String | INDEX, NOT NULL | Owner user ID from Better Auth JWT |
| `title` | String(200) | NOT NULL | Task title (1-200 characters) |
| `description` | Text | NULLABLE | Task description (≤1000 chars, optional) |
| `completed` | Boolean | NOT NULL, DEFAULT False | Completion status |
| `created_at` | DateTime | NOT NULL, DEFAULT UTC now | Creation timestamp |
| `updated_at` | DateTime | NOT NULL, DEFAULT UTC now, ON UPDATE | Last modification timestamp |

### Indexes

- **PRIMARY**: `id`
- **INDEX**: `user_id` (for fast user task lookup)
- **INDEX**: `created_at` (for ordering)

### Validation Rules

- **title**: Required, 1-200 characters after trimming whitespace
- **description**: Optional, maximum 1000 characters
- **user_id**: Required, string format (Better Auth UUID)
- **completed**: Boolean, defaults to False

### SQLModel Definition

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class TaskPhaseIII(SQLModel, table=True):
    """Phase III task entity - separate from Phase II tasks."""

    __tablename__ = "tasks_phaseiii"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth JWT")
    title: str = Field(max_length=200, nullable=False, description="Task title (1-200 chars)")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description (≤1000 chars)")
    completed: bool = Field(default=False, nullable=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "ba_user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:00:00Z"
            }
        }
```

### State Transitions

```
[New Task]
    ↓
[Pending] (completed = False)
    ↓ (via complete_task tool)
[Completed] (completed = True)
    ↓ (via complete_task tool - idempotent)
[Completed] (remains True)

[Any State]
    ↓ (via delete_task tool)
[Deleted] (removed from database)
```

---

## 2. Conversation Entity

### Table Name: `conversations`

**Purpose**: Represents a chat session between user and AI assistant. Contains conversation metadata and links to messages.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| `user_id` | String | INDEX, NOT NULL | Owner user ID from Better Auth JWT |
| `created_at` | DateTime | NOT NULL, DEFAULT UTC now | Conversation start timestamp |
| `updated_at` | DateTime | NOT NULL, DEFAULT UTC now, ON UPDATE | Last activity timestamp |

### Indexes

- **PRIMARY**: `id`
- **INDEX**: `user_id` (for fast user conversation lookup)

### Validation Rules

- **user_id**: Required, string format (Better Auth UUID)
- **created_at**: Automatically set on creation
- **updated_at**: Automatically updated on modification

### SQLModel Definition

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Conversation(SQLModel, table=True):
    """Conversation between user and AI assistant."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth JWT")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "ba_user_abc123",
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:15:00Z"
            }
        }
```

### State Transitions

```
[New Conversation]
    ↓
[Active] (has messages)
    ↓
[Inactive] (no recent messages, but persists indefinitely)
```

---

## 3. Message Entity

### Table Name: `messages`

**Purpose**: Represents a single message in a conversation (either from user or AI assistant). Ordered by created_at for conversation history.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| `conversation_id` | Integer | FOREIGN KEY → conversations.id, INDEX, NOT NULL | Parent conversation |
| `user_id` | String | INDEX, NOT NULL | Owner user ID (redundant isolation layer) |
| `role` | String | NOT NULL | Message role: "user" or "assistant" |
| `content` | Text | NOT NULL | Message content (no length limit) |
| `created_at` | DateTime | NOT NULL, DEFAULT UTC now | Message timestamp |

### Indexes

- **PRIMARY**: `id`
- **INDEX**: `conversation_id` (for fast message lookup by conversation)
- **INDEX**: `user_id` (for redundant user isolation)

### Validation Rules

- **conversation_id**: Required, must reference existing conversation
- **user_id**: Required, must match conversation.user_id
- **role**: Required, must be "user" or "assistant"
- **content**: Required, non-empty string

### SQLModel Definition

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional, Literal

class Message(SQLModel, table=True):
    """Message in a conversation (user or assistant)."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False, description="User ID (redundant isolation)")
    role: Literal["user", "assistant"] = Field(nullable=False, description="Message sender role")
    content: str = Field(nullable=False, description="Message content")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "ba_user_abc123",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2025-12-17T10:00:00Z"
            }
        }
```

### State Transitions

```
[New Message]
    ↓
[Stored] (persists indefinitely)
```

**Note**: Messages are immutable once created. No update operations.

---

## Alembic Migration

### Initial Schema Migration

**File**: `phaseIII/backend/alembic/versions/20251217_initial_phase_iii_schema.py`

```python
"""Initial Phase III schema

Revision ID: 001
Revises:
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tasks_phaseiii table
    op.create_table(
        'tasks_phaseiii',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create messages table with FK to conversations
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_tasks_phaseiii_user_id', 'tasks_phaseiii', ['user_id'])
    op.create_index('idx_tasks_phaseiii_created_at', 'tasks_phaseiii', ['created_at'])
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

def downgrade():
    # Drop in reverse order (FK constraints)
    op.drop_index('idx_messages_user_id', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_index('idx_tasks_phaseiii_created_at', table_name='tasks_phaseiii')
    op.drop_index('idx_tasks_phaseiii_user_id', table_name='tasks_phaseiii')

    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('tasks_phaseiii')
```

---

## Database Constraints

### Foreign Keys

- `messages.conversation_id` → `conversations.id` (CASCADE on delete)

### Check Constraints

- `tasks_phaseiii.title`: Length between 1 and 200 characters
- `tasks_phaseiii.description`: Maximum 1000 characters (enforced by application)
- `messages.role`: Must be "user" or "assistant" (enforced by Literal type)

### Unique Constraints

None - All tables allow duplicates (multiple tasks with same title, etc.)

---

## Query Patterns

### User Task Lookup

```python
# List all tasks for a user
tasks = await session.exec(
    select(TaskPhaseIII)
    .where(TaskPhaseIII.user_id == user_id)
    .order_by(TaskPhaseIII.created_at.desc())
)
```

### Filtered Task Lookup

```python
# List pending tasks only
pending_tasks = await session.exec(
    select(TaskPhaseIII)
    .where(TaskPhaseIII.user_id == user_id)
    .where(TaskPhaseIII.completed == False)
    .order_by(TaskPhaseIII.created_at.desc())
)
```

### Conversation with Messages

```python
# Get conversation with all messages
conversation = await session.get(Conversation, conversation_id)
messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
)
```

### User Isolation Verification

```python
# ALWAYS filter by JWT user_id
task = await session.exec(
    select(TaskPhaseIII)
    .where(TaskPhaseIII.id == task_id)
    .where(TaskPhaseIII.user_id == jwt_user_id)  # CRITICAL: user isolation
)

if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## Data Isolation Patterns

### Three-Layer Security

1. **JWT Validation**: Extract user_id from validated JWT token (authoritative source)
2. **Path Validation**: Verify path parameter matches JWT user_id (403 if mismatch)
3. **Query Scoping**: All queries filtered by JWT user_id (never path parameter)

### Example: MCP Tool Data Access

```python
async def list_tasks_tool(user_id: str, status: str = "all") -> dict:
    """
    user_id comes from authenticated JWT context, not from tool parameters.
    """
    query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

    if status == "pending":
        query = query.where(TaskPhaseIII.completed == False)
    elif status == "completed":
        query = query.where(TaskPhaseIII.completed == True)
    # else: status == "all", no additional filter

    tasks = await session.exec(query.order_by(TaskPhaseIII.created_at.desc()))

    return {"tasks": [task.dict() for task in tasks]}
```

---

## Performance Considerations

### Indexes

- `user_id` indexes enable fast lookup for user-scoped queries (p95 < 50ms)
- `conversation_id` index enables fast message retrieval
- `created_at` index supports ordering without full table scan

### Connection Pooling

- Pool size: 5-10 connections
- Reuses connections across requests
- Prevents connection exhaustion

### Async Operations

- All queries use `async`/`await` for non-blocking I/O
- Expected response time: 10-50ms for database operations

---

## Testing Requirements

### Unit Tests

- Model validation (field constraints, type checking)
- Relationship integrity (FK constraints)
- Default values (created_at, updated_at, completed)

### Integration Tests

- Multi-user data isolation (User A cannot see User B's data)
- Query scoping correctness (all queries filtered by user_id)
- Migration reversibility (upgrade → downgrade → upgrade)

---

## Constitutional Compliance

✅ **Principle II (Phase Separation)**: Separate tables (`tasks_phaseiii`, not `tasks`)
✅ **Principle III (Database Persistence)**: SQLModel with async operations, Alembic migrations
✅ **Principle IV (JWT Security)**: All models scoped to user_id from JWT
✅ **Principle XI (MCP Server)**: Stateless design with database-backed state

---

**Data Model Status**: Complete and ready for implementation
**Next Step**: Implement SQLModel models in `phaseIII/backend/app/models/`
