# Data Model: Advanced Task Management Foundation

**Feature**: 001-foundation-api
**Date**: 2025-12-30
**Phase**: 1 - Data Model Design

## Overview

This document defines the complete data model for Phase V advanced task management, including schema evolution for the existing `tasks_phaseiii` table and three new tables (`categories`, `tags_phasev`, `task_tags`). The design supports task prioritization, categorization, tagging, due date management, recurring tasks, and full-text search.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       tasks_phaseiii                        │
├─────────────────────────────────────────────────────────────┤
│ PK  id                    INTEGER                           │
│ FK  category_id           INTEGER (nullable)     ──┐         │
│     user_id               VARCHAR                   │         │
│     title                 VARCHAR(200)              │         │
│     description           TEXT (nullable)           │         │
│     completed             BOOLEAN                   │         │
│ NEW priority              ENUM(low,med,high,urgent) │         │
│ NEW due_date              TIMESTAMP (nullable)      │         │
│ NEW recurrence_rule       TEXT (nullable)           │         │
│ NEW reminder_sent         BOOLEAN                   │         │
│ NEW search_vector         TSVECTOR                  │         │
│ NEW search_rank           REAL (nullable)           │         │
│     created_at            TIMESTAMP                 │         │
│     updated_at            TIMESTAMP                 │         │
└──────────────────────────────────────┬───────────────────────┘
                                       │
                   ┌───────────────────┼─────────────────────┐
                   │                   │                     │
                   ▼                   ▼                     ▼
         ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
         │  categories  │    │  task_tags   │    │   tags_phasev    │
         ├──────────────┤    ├──────────────┤    ├──────────────────┤
         │ PK id        │◄───┤ FK task_id   │───►│ PK id            │
         │    user_id   │    │ FK tag_id    │    │    user_id       │
         │    name      │    └──────────────┘    │    name          │
         │    color     │                        │    color         │
         │    created_at│                        │    created_at    │
         └──────────────┘                        └──────────────────┘

Relationships:
- Task → Category: Many-to-One (nullable)
- Task ↔ Tag: Many-to-Many (via task_tags junction)
```

---

## Entity Definitions

### 1. TaskPhaseIII (Enhanced)

**Table**: `tasks_phaseiii`
**Description**: Core task entity with advanced features for priority, due dates, categorization, recurrence, and search

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| `user_id` | VARCHAR | NOT NULL, INDEXED | Owner user ID from JWT (data isolation) |
| `title` | VARCHAR(200) | NOT NULL | Task title (searchable) |
| `description` | TEXT | NULLABLE | Task description (searchable) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `priority` | ENUM | NOT NULL, DEFAULT 'medium' | Priority level: low, medium, high, urgent |
| `due_date` | TIMESTAMP | NULLABLE | Due date in UTC (clients send ISO 8601 with TZ) |
| `category_id` | INTEGER | NULLABLE, FOREIGN KEY → categories.id | Optional category assignment |
| `recurrence_rule` | TEXT | NULLABLE | iCalendar RRULE format (e.g., FREQ=WEEKLY;BYDAY=MO) |
| `reminder_sent` | BOOLEAN | NOT NULL, DEFAULT FALSE | Tracks if reminder notification sent |
| `search_vector` | TSVECTOR | NOT NULL, INDEXED (GIN) | Full-text search index (auto-updated via trigger) |
| `search_rank` | REAL | NULLABLE | Pre-computed search relevance rank (optimization) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks_phaseiii(user_id);
CREATE INDEX idx_tasks_category_id ON tasks_phaseiii(category_id);
CREATE INDEX idx_tasks_due_date ON tasks_phaseiii(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks_phaseiii(priority);
CREATE INDEX idx_tasks_search_vector ON tasks_phaseiii USING GIN(search_vector);
```

**Triggers**:
```sql
-- Auto-update search_vector on title/description changes
CREATE TRIGGER tasks_search_vector_update
BEFORE INSERT OR UPDATE ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);

-- Auto-update updated_at timestamp
CREATE TRIGGER tasks_updated_at_trigger
BEFORE UPDATE ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Validations**:
- `priority` must be one of: low, medium, high, urgent
- `recurrence_rule` must be valid iCalendar RRULE format (validated at application level)
- `due_date` stored in UTC; clients send/receive ISO 8601 with timezone
- `category_id` must reference existing category owned by same user
- `color` (categories/tags) must be hex format: `^#[0-9A-Fa-f]{6}$` or NULL

**State Transitions**:
```
created (completed=false) → completed (completed=true)
completed (completed=true) → uncompleted (completed=false)
```

---

### 2. Category

**Table**: `categories`
**Description**: User-defined organizational buckets for tasks (e.g., "Work", "Personal", "Health")

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique category identifier |
| `user_id` | VARCHAR | NOT NULL, INDEXED | Owner user ID from JWT |
| `name` | VARCHAR(50) | NOT NULL | Category name (case-sensitive) |
| `color` | VARCHAR(7) | NULLABLE | Hex color code (e.g., #FF5733) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Constraints**:
```sql
ALTER TABLE categories ADD CONSTRAINT uq_category_user_name
UNIQUE (user_id, name);

ALTER TABLE categories ADD CONSTRAINT check_color_format
CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$');
```

**Indexes**:
```sql
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE UNIQUE INDEX idx_categories_user_name ON categories(user_id, name);
```

**Business Rules**:
- Maximum 50 categories per user (enforced at application level)
- Category names must be unique per user (case-sensitive)
- Deleting a category sets `category_id` to NULL on associated tasks (ON DELETE SET NULL)
- Color codes are optional; if provided, must be valid hex format

---

### 3. TagPhaseV

**Table**: `tags_phasev`
**Description**: Flexible labels for cross-categorical organization (e.g., #urgent, #meeting, #client-facing)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique tag identifier |
| `user_id` | VARCHAR | NOT NULL, INDEXED | Owner user ID from JWT |
| `name` | VARCHAR(30) | NOT NULL | Tag name (case-sensitive) |
| `color` | VARCHAR(7) | NULLABLE | Hex color code (e.g., #FF5733) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Constraints**:
```sql
ALTER TABLE tags_phasev ADD CONSTRAINT uq_tag_user_name
UNIQUE (user_id, name);

ALTER TABLE tags_phasev ADD CONSTRAINT check_color_format
CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$');
```

**Indexes**:
```sql
CREATE INDEX idx_tags_user_id ON tags_phasev(user_id);
CREATE UNIQUE INDEX idx_tags_user_name ON tags_phasev(user_id, name);
```

**Business Rules**:
- Maximum 100 tags per user (enforced at application level)
- Tag names must be unique per user (case-sensitive)
- Deleting a tag removes all associations from task_tags table (ON DELETE CASCADE)
- Color codes are optional; if provided, must be valid hex format

---

### 4. TaskTags (Junction Table)

**Table**: `task_tags`
**Description**: Many-to-many relationship between tasks and tags

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_id` | INTEGER | NOT NULL, FOREIGN KEY → tasks_phaseiii.id | Task being tagged |
| `tag_id` | INTEGER | NOT NULL, FOREIGN KEY → tags_phasev.id | Tag being applied |

**Constraints**:
```sql
ALTER TABLE task_tags ADD PRIMARY KEY (task_id, tag_id);

ALTER TABLE task_tags ADD CONSTRAINT fk_task
FOREIGN KEY (task_id) REFERENCES tasks_phaseiii(id) ON DELETE CASCADE;

ALTER TABLE task_tags ADD CONSTRAINT fk_tag
FOREIGN KEY (tag_id) REFERENCES tags_phasev(id) ON DELETE CASCADE;
```

**Indexes**:
```sql
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

**Business Rules**:
- Maximum 10 tags per task (enforced at application level + optional database trigger)
- Duplicate tag assignments are idempotent (PRIMARY KEY prevents duplicates)
- Deleting a task removes all tag associations (ON DELETE CASCADE)
- Deleting a tag removes all task associations (ON DELETE CASCADE)

---

## Field Validations Summary

| Field | Validation Rule | Error Message |
|-------|-----------------|---------------|
| `task.title` | 1-200 characters, required | "Title must be 1-200 characters" |
| `task.priority` | Enum: low, medium, high, urgent | "Priority must be one of: low, medium, high, urgent" |
| `task.due_date` | ISO 8601 datetime or null | "Due date must be ISO 8601 format (e.g., 2025-01-15T17:00:00-05:00)" |
| `task.recurrence_rule` | Valid iCalendar RRULE or null | "Invalid recurrence pattern. Examples: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,WE,FR" |
| `category.name` | 1-50 characters, unique per user | "Category name must be 1-50 characters and unique" |
| `category.color` | Hex format (#RRGGBB) or null | "Color must be hex format (e.g., #FF5733)" |
| `tag.name` | 1-30 characters, unique per user | "Tag name must be 1-30 characters and unique" |
| `tag.color` | Hex format (#RRGGBB) or null | "Color must be hex format (e.g., #FF5733)" |
| Tags per task | Maximum 10 | "Maximum 10 tags per task exceeded" |
| Categories per user | Maximum 50 | "Maximum 50 categories reached. Delete unused categories to create new ones." |
| Tags per user | Maximum 100 | "Maximum 100 tags reached. Delete unused tags to create new ones." |

---

## Migration Strategy

### Step 1: Add New Tables
```sql
-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_category_user_name UNIQUE (user_id, name),
    CONSTRAINT check_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Create tags_phasev table
CREATE TABLE tags_phasev (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name VARCHAR(30) NOT NULL,
    color VARCHAR(7),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tag_user_name UNIQUE (user_id, name),
    CONSTRAINT check_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Create task_tags junction table
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    CONSTRAINT fk_task FOREIGN KEY (task_id) REFERENCES tasks_phaseiii(id) ON DELETE CASCADE,
    CONSTRAINT fk_tag FOREIGN KEY (tag_id) REFERENCES tags_phasev(id) ON DELETE CASCADE
);
```

### Step 2: Enhance tasks_phaseiii Table
```sql
-- Add new columns
ALTER TABLE tasks_phaseiii
ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium',
ADD COLUMN due_date TIMESTAMP,
ADD COLUMN category_id INTEGER,
ADD COLUMN recurrence_rule TEXT,
ADD COLUMN reminder_sent BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN search_vector TSVECTOR,
ADD COLUMN search_rank REAL;

-- Convert priority to ENUM (PostgreSQL-specific)
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent');
ALTER TABLE tasks_phaseiii ALTER COLUMN priority TYPE priority_level USING priority::priority_level;

-- Add foreign key constraint
ALTER TABLE tasks_phaseiii ADD CONSTRAINT fk_category
FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL;

-- Create indexes
CREATE INDEX idx_tasks_category_id ON tasks_phaseiii(category_id);
CREATE INDEX idx_tasks_due_date ON tasks_phaseiii(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks_phaseiii(priority);
CREATE INDEX idx_tasks_search_vector ON tasks_phaseiii USING GIN(search_vector);

-- Initialize search_vector for existing tasks
UPDATE tasks_phaseiii
SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''));

-- Create trigger for auto-updating search_vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_vector_update
BEFORE INSERT OR UPDATE OF title, description ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

### Step 3: Create Supporting Functions
```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_updated_at_trigger
BEFORE UPDATE ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Rollback Strategy
```sql
-- Rollback script (reverses migration)
DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks_phaseiii;
DROP TRIGGER IF EXISTS tasks_updated_at_trigger ON tasks_phaseiii;
DROP FUNCTION IF EXISTS update_search_vector();
DROP FUNCTION IF EXISTS update_updated_at_column();

ALTER TABLE tasks_phaseiii DROP CONSTRAINT IF EXISTS fk_category;
ALTER TABLE tasks_phaseiii
DROP COLUMN IF EXISTS priority,
DROP COLUMN IF EXISTS due_date,
DROP COLUMN IF EXISTS category_id,
DROP COLUMN IF EXISTS recurrence_rule,
DROP COLUMN IF EXISTS reminder_sent,
DROP COLUMN IF EXISTS search_vector,
DROP COLUMN IF EXISTS search_rank;

DROP TABLE IF EXISTS task_tags CASCADE;
DROP TABLE IF EXISTS tags_phasev CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TYPE IF EXISTS priority_level;

-- WARNING: Rollback loses all data in new fields and tables!
```

---

## SQLModel Class Definitions

### TaskPhaseIII (Enhanced)
```python
from datetime import datetime
from enum import Enum as PyEnum
from sqlmodel import SQLModel, Field, Column, Enum as SQLEnum

class PriorityLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskPhaseIII(SQLModel, table=True):
    __tablename__ = "tasks_phaseiii"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        sa_column=Column(SQLEnum(PriorityLevel), nullable=False)
    )
    due_date: datetime | None = Field(default=None, nullable=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id")
    recurrence_rule: str | None = Field(default=None)
    reminder_sent: bool = Field(default=False, nullable=False)
    # search_vector and search_rank managed by database triggers
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Category
```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=50, nullable=False)
    color: str | None = Field(max_length=7, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### TagPhaseV
```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class TagPhaseV(SQLModel, table=True):
    __tablename__ = "tags_phasev"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=30, nullable=False)
    color: str | None = Field(max_length=7, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### TaskTags
```python
from sqlmodel import SQLModel, Field

class TaskTags(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks_phaseiii.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags_phasev.id", primary_key=True)
```

---

## Performance Considerations

1. **Full-Text Search**: GIN index on `search_vector` enables sub-200ms searches for 10k tasks
2. **Filtered Queries**: Indexes on `user_id`, `priority`, `due_date`, `category_id` for fast filtering
3. **Tag Lookups**: Indexes on junction table for efficient many-to-many queries
4. **Unique Constraints**: Composite indexes on (user_id, name) for categories/tags prevent duplicates and speed lookups
5. **Trigger Performance**: `search_vector` update trigger runs on insert/update only (acceptable overhead)

---

**End of Data Model Design**
