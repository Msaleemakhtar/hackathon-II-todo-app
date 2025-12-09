# Data Model: Foundational Backend Setup

**Date**: 2025-12-09
**Feature**: 001-foundational-backend-setup
**Phase**: 1 (Design & Contracts)

This document defines the complete SQLModel entity definitions, relationships, constraints, and database schema for the foundational backend.

---

## Entity Definitions

### 1. User Entity

**Purpose**: Represents a registered application user with authentication credentials

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    """User entity with authentication credentials"""
    __tablename__ = "users"

    id: str = Field(primary_key=True, description="User ID (UUID string from Better Auth)")
    email: str = Field(unique=True, index=True, nullable=False, description="User's email address")
    password_hash: str = Field(nullable=False, description="Bcrypt-hashed password")
    name: Optional[str] = Field(default=None, description="User's display name")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, description="Account creation timestamp")

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    tags: List["Tag"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
```

**Constraints**:
- `id`: PRIMARY KEY (string to support UUID format)
- `email`: UNIQUE, NOT NULL, indexed for lookup performance
- `password_hash`: NOT NULL (never store plaintext passwords)
- `name`: NULLABLE (optional display name)
- `created_at`: NOT NULL, defaults to current UTC timestamp

**Notes**:
- Password hash uses bcrypt with 12 rounds (see research.md #3)
- User ID is string type to accommodate Better Auth UUID integration
- Cascade delete ensures tasks and tags are deleted when user is deleted

---

### 2. Task Entity

**Purpose**: Represents a todo item owned by a user

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class PriorityEnum(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    """Task entity representing a todo item"""
    __tablename__ = "tasks"

    id: int = Field(primary_key=True, description="Unique task identifier")
    title: str = Field(min_length=1, max_length=200, nullable=False, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Detailed description")
    completed: bool = Field(default=False, nullable=False, description="Completion status")
    priority: str = Field(default="medium", nullable=False, description="Priority level: low, medium, high")
    due_date: Optional[datetime] = Field(default=None, description="Task due date and time")
    recurrence_rule: Optional[str] = Field(default=None, description="iCal RRULE string for recurring tasks")
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True, description="Task owner")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, description="Last modification timestamp")

    # Relationships
    user: User = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTagLink")

    # Indexes defined in migration (see migration strategy below)
```

**Constraints**:
- `id`: PRIMARY KEY, auto-increment
- `title`: NOT NULL, 1-200 characters
- `description`: NULLABLE, max 1000 characters
- `completed`: NOT NULL, default False
- `priority`: NOT NULL, default 'medium', must be one of: 'low', 'medium', 'high'
- `due_date`: NULLABLE (tasks may not have due dates)
- `recurrence_rule`: NULLABLE (not all tasks are recurring)
- `user_id`: FOREIGN KEY to users.id, NOT NULL, indexed
- `created_at`: NOT NULL, defaults to current UTC timestamp
- `updated_at`: NOT NULL, updated on modification

**Validation Rules** (enforced in Pydantic schemas):
- Title: Required, 1-200 chars after trimming
- Description: Optional, max 1000 chars
- Priority: Must be 'low', 'medium', or 'high'
- Due date: Must be valid ISO 8601 datetime (backend validates format, no past-date check on creation per spec)
- Recurrence rule: Must be valid iCal RRULE format if provided

---

### 3. Tag Entity

**Purpose**: Represents a category label for tasks, owned by a user

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Tag(SQLModel, table=True):
    """Tag entity for categorizing tasks"""
    __tablename__ = "tags"

    id: int = Field(primary_key=True, description="Unique tag identifier")
    name: str = Field(min_length=1, max_length=50, nullable=False, description="Tag display name")
    color: Optional[str] = Field(default=None, regex="^#[0-9A-Fa-f]{6}$", description="Hex color code for UI display")
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True, description="Tag owner")

    # Relationships
    user: User = Relationship(back_populates="tags")
    tasks: List[Task] = Relationship(back_populates="tags", link_model="TaskTagLink")
```

**Constraints**:
- `id`: PRIMARY KEY, auto-increment
- `name`: NOT NULL, 1-50 characters
- `color`: NULLABLE, hex format (#RRGGBB) if provided
- `user_id`: FOREIGN KEY to users.id, NOT NULL, indexed
- **UNIQUE(name, user_id)**: No duplicate tag names per user (composite unique constraint)

**Validation Rules**:
- Name: Required, 1-50 chars after trimming, unique per user
- Color: Optional, must match hex color pattern if provided

---

### 4. TaskTagLink Entity (Junction Table)

**Purpose**: Many-to-many relationship between tasks and tags

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field

class TaskTagLink(SQLModel, table=True):
    """Junction table for many-to-many Task-Tag relationship"""
    __tablename__ = "task_tag_link"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True, description="Task reference")
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, description="Tag reference")
```

**Constraints**:
- `task_id`: FOREIGN KEY to tasks.id, part of composite PRIMARY KEY
- `tag_id`: FOREIGN KEY to tags.id, part of composite PRIMARY KEY
- **Composite PRIMARY KEY(task_id, tag_id)**: Prevents duplicate task-tag associations

**Cascade Behavior**:
- When a task is deleted, all TaskTagLink entries for that task are deleted
- When a tag is deleted, all TaskTagLink entries for that tag are deleted
- Tags and tasks are NOT deleted when the link is removed

---

## Relationships

### User ↔ Task (One-to-Many)
- **Cardinality**: One User has many Tasks
- **Foreign Key**: Task.user_id → User.id
- **Cascade**: DELETE CASCADE (deleting user deletes all their tasks)
- **Back-population**: User.tasks, Task.user

### User ↔ Tag (One-to-Many)
- **Cardinality**: One User has many Tags
- **Foreign Key**: Tag.user_id → User.id
- **Cascade**: DELETE CASCADE (deleting user deletes all their tags)
- **Back-population**: User.tags, Tag.user

### Task ↔ Tag (Many-to-Many)
- **Cardinality**: Many Tasks can have many Tags
- **Junction Table**: TaskTagLink
- **Foreign Keys**:
  - TaskTagLink.task_id → Task.id
  - TaskTagLink.tag_id → Tag.id
- **Cascade**: DELETE CASCADE on both sides (deleting either task or tag removes the link)
- **Back-population**: Task.tags, Tag.tasks

---

## Database Indexes

Per constitution requirements, the following indexes **MUST** be created to optimize query performance:

### Task Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
```

**Purpose**:
- `idx_tasks_user_id`: Fast lookup of all tasks for a user
- `idx_tasks_user_completed`: Filtered queries (e.g., "show only pending tasks")
- `idx_tasks_user_priority`: Priority-based sorting and filtering
- `idx_tasks_user_due_date`: Due date sorting and upcoming tasks queries

### Tag Indexes
```sql
CREATE INDEX idx_tags_user_id ON tags(user_id);
```

**Purpose**: Fast lookup of all tags for a user

### TaskTagLink Indexes
```sql
CREATE INDEX idx_task_tag_link_task ON task_tag_link(task_id);
CREATE INDEX idx_task_tag_link_tag ON task_tag_link(tag_id);
```

**Purpose**:
- `idx_task_tag_link_task`: Fast lookup of tags for a task
- `idx_task_tag_link_tag`: Fast lookup of tasks for a tag

**Implementation Note**: These indexes are created in the Alembic migration file (see migration strategy below).

---

## Alembic Migration Strategy

### Initial Migration

**Migration File**: `alembic/versions/YYYYMMDD_HHMMSS_initial_schema.py`

```python
"""Initial schema: users, tasks, tags, task_tag_link

Revision ID: 001
Revises: None
Create Date: 2025-12-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'user_id', name='uq_tag_name_user')
    )
    op.create_index('idx_tags_user_id', 'tags', ['user_id'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('recurrence_rule', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])

    # Create task_tag_link junction table
    op.create_table(
        'task_tag_link',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )
    op.create_index('idx_task_tag_link_task', 'task_tag_link', ['task_id'])
    op.create_index('idx_task_tag_link_tag', 'task_tag_link', ['tag_id'])

def downgrade() -> None:
    op.drop_table('task_tag_link')
    op.drop_table('tasks')
    op.drop_table('tags')
    op.drop_table('users')
```

### Migration Commands

```bash
# Generate migration (auto-detect changes from models)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## Pydantic Schemas (Request/Response)

### User Schemas

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Shared user properties"""
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    """User creation request"""
    password: str = Field(min_length=8, description="Minimum 8 characters")

class UserResponse(UserBase):
    """User response (excludes password)"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### Task Schemas

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskBase(BaseModel):
    """Shared task properties"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False
    priority: PriorityEnum = PriorityEnum.MEDIUM
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None

class TaskCreate(TaskBase):
    """Task creation request"""
    pass

class TaskUpdate(BaseModel):
    """Task update request (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None

class TaskResponse(TaskBase):
    """Task response"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    tags: list[int] = []  # List of tag IDs

    class Config:
        from_attributes = True
```

### Tag Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class TagBase(BaseModel):
    """Shared tag properties"""
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

    @validator('color')
    def validate_color_format(cls, v):
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v

class TagCreate(TagBase):
    """Tag creation request"""
    pass

class TagUpdate(BaseModel):
    """Tag update request (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class TagResponse(TagBase):
    """Tag response"""
    id: int
    user_id: str

    class Config:
        from_attributes = True
```

---

## Data Isolation & Security

**Critical Requirement**: ALL database queries MUST scope to the authenticated user's ID to prevent unauthorized data access.

### Implementation Pattern

```python
# core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import verify_token
from models.user import User
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate user from JWT token"""
    try:
        payload = verify_token(token, expected_type="access")
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# Usage in endpoints
@router.get("/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # ALWAYS filter by current_user.id
    result = await db.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    tasks = result.scalars().all()
    return tasks
```

---

## Testing Strategy

### Model Tests

```python
# tests/test_models.py
import pytest
from models import User, Task, Tag, TaskTagLink

@pytest.mark.asyncio
async def test_user_creation(db_session):
    """Test user model creation and constraints"""
    user = User(
        id="test-uuid",
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id == "test-uuid"
    assert user.email == "test@example.com"
    assert user.created_at is not None

@pytest.mark.asyncio
async def test_task_relationships(db_session):
    """Test task-user relationship and cascade delete"""
    user = User(id="user-1", email="user@example.com", password_hash="hash")
    task = Task(title="Test Task", user_id=user.id)

    db_session.add(user)
    db_session.add(task)
    await db_session.commit()

    # Verify relationship
    await db_session.refresh(user)
    assert len(user.tasks) == 1
    assert user.tasks[0].title == "Test Task"

    # Test cascade delete
    await db_session.delete(user)
    await db_session.commit()
    # Task should be deleted (cascade)
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    assert result.scalar_one_or_none() is None
```

---

## Summary

This data model provides:

✅ **Constitution Compliance**: All entities, constraints, and indexes per constitution spec
✅ **Type Safety**: SQLModel provides Pydantic validation and SQLAlchemy ORM
✅ **Relationships**: Proper foreign keys and cascade behavior
✅ **Indexes**: Optimized for common query patterns
✅ **Data Isolation**: User-scoped queries prevent unauthorized access
✅ **Migration Strategy**: Alembic for reversible schema evolution
✅ **Testing**: Clear patterns for model and relationship tests

**Next Step**: Generate API contracts in `contracts/auth-api.yaml`
