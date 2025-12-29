# Quickstart Guide: Advanced Task Management Foundation

**Feature**: 001-foundation-api
**Date**: 2025-12-30
**Target Audience**: Developers implementing this feature via AI code generation

## Overview

This guide provides step-by-step instructions for implementing Phase V advanced task management capabilities, including database migrations, model enhancements, service layers, MCP tools, and comprehensive testing.

---

## Prerequisites

Before starting implementation, ensure:

1. **Phase V Backend Exists**: `phaseV/backend/` directory with existing Phase III/IV code
2. **Database Access**: Neon Serverless PostgreSQL connection configured in `.env`
3. **Dependencies Installed**: `uv sync` has installed all Python dependencies
4. **Branch Created**: Working on `001-foundation-api` feature branch
5. **Spec Reviewed**: Read `spec.md`, `plan.md`, `data-model.md`, `contracts/mcp-tools.md`

---

## Implementation Workflow

### Phase 0: Preparation

#### Step 1: Add New Dependency
```bash
cd phaseV/backend
# Add python-dateutil for RRULE parsing
uv add "python-dateutil>=2.8.2"
```

#### Step 2: Verify Environment
```bash
# Check database connection
uv run python -c "from app.database import engine; print('Database connection OK')"

# Check existing migrations
uv run alembic history
```

---

### Phase 1: Database Migration

#### Step 3: Generate Migration Script
```bash
cd phaseV/backend
# Generate migration for schema evolution
uv run alembic revision --autogenerate -m "add_advanced_task_fields_and_tables"
```

Expected migration file: `alembic/versions/YYYYMMDD_HHMMSS_add_advanced_task_fields_and_tables.py`

#### Step 4: Review & Edit Migration

The auto-generated migration needs manual enhancements. Edit the migration file to include:

**Upgrade Function**:
```python
def upgrade() -> None:
    # 1. Create ENUM type
    op.execute("CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent')")

    # 2. Create new tables
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_category_user_name'),
        sa.CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name='check_color_format')
    )
    op.create_index('idx_categories_user_id', 'categories', ['user_id'])

    op.create_table('tags_phasev',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_tag_user_name'),
        sa.CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name='check_color_format')
    )
    op.create_index('idx_tags_user_id', 'tags_phasev', ['user_id'])

    op.create_table('task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks_phaseiii.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags_phasev.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )
    op.create_index('idx_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('idx_task_tags_tag_id', 'task_tags', ['tag_id'])

    # 3. Add new columns to tasks_phaseiii
    op.add_column('tasks_phaseiii', sa.Column('priority', sa.String(10), nullable=False, server_default='medium'))
    op.add_column('tasks_phaseiii', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks_phaseiii', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('tasks_phaseiii', sa.Column('recurrence_rule', sa.Text(), nullable=True))
    op.add_column('tasks_phaseiii', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks_phaseiii', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))
    op.add_column('tasks_phaseiii', sa.Column('search_rank', sa.Float(), nullable=True))

    # 4. Convert priority to ENUM
    op.execute("ALTER TABLE tasks_phaseiii ALTER COLUMN priority TYPE priority_level USING priority::priority_level")
    op.alter_column('tasks_phaseiii', 'priority', server_default=None)

    # 5. Add foreign key constraints
    op.create_foreign_key('fk_category', 'tasks_phaseiii', 'categories', ['category_id'], ['id'], ondelete='SET NULL')

    # 6. Create indexes
    op.create_index('idx_tasks_category_id', 'tasks_phaseiii', ['category_id'])
    op.create_index('idx_tasks_due_date', 'tasks_phaseiii', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_tasks_priority', 'tasks_phaseiii', ['priority'])
    op.create_index('idx_tasks_search_vector', 'tasks_phaseiii', ['search_vector'], postgresql_using='gin')

    # 7. Initialize search_vector for existing tasks
    op.execute("""
        UPDATE tasks_phaseiii
        SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
    """)

    # 8. Create trigger function for search_vector auto-update
    op.execute("""
        CREATE OR REPLACE FUNCTION update_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER tasks_search_vector_update
        BEFORE INSERT OR UPDATE OF title, description ON tasks_phaseiii
        FOR EACH ROW EXECUTE FUNCTION update_search_vector();
    """)

    # 9. Create trigger for updated_at auto-update
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER tasks_updated_at_trigger
        BEFORE UPDATE ON tasks_phaseiii
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks_phaseiii")
    op.execute("DROP TRIGGER IF EXISTS tasks_updated_at_trigger ON tasks_phaseiii")
    op.execute("DROP FUNCTION IF EXISTS update_search_vector()")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop indexes
    op.drop_index('idx_tasks_search_vector', 'tasks_phaseiii')
    op.drop_index('idx_tasks_priority', 'tasks_phaseiii')
    op.drop_index('idx_tasks_due_date', 'tasks_phaseiii')
    op.drop_index('idx_tasks_category_id', 'tasks_phaseiii')

    # Drop foreign key
    op.drop_constraint('fk_category', 'tasks_phaseiii', type_='foreignkey')

    # Drop new columns
    op.drop_column('tasks_phaseiii', 'search_rank')
    op.drop_column('tasks_phaseiii', 'search_vector')
    op.drop_column('tasks_phaseiii', 'reminder_sent')
    op.drop_column('tasks_phaseiii', 'recurrence_rule')
    op.drop_column('tasks_phaseiii', 'category_id')
    op.drop_column('tasks_phaseiii', 'due_date')
    op.drop_column('tasks_phaseiii', 'priority')

    # Drop tables
    op.drop_table('task_tags')
    op.drop_table('tags_phasev')
    op.drop_table('categories')

    # Drop ENUM type
    op.execute("DROP TYPE priority_level")
```

#### Step 5: Run Migration
```bash
# Apply migration
uv run alembic upgrade head

# Verify schema
uv run alembic current
```

---

### Phase 2: Model Layer

#### Step 6: Create New Models

**File**: `phaseV/backend/app/models/category.py`
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

**File**: `phaseV/backend/app/models/tag.py`
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

**File**: `phaseV/backend/app/models/task_tag.py`
```python
from sqlmodel import SQLModel, Field

class TaskTags(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks_phaseiii.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags_phasev.id", primary_key=True)
```

#### Step 7: Enhance Task Model

**File**: `phaseV/backend/app/models/task.py` (update existing)
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
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

### Phase 3: Schema Layer

#### Step 8: Create Pydantic Schemas

**File**: `phaseV/backend/app/schemas/category.py`
```python
import re
from datetime import datetime
from pydantic import BaseModel, field_validator

HEX_COLOR_REGEX = re.compile(r'^#[0-9A-Fa-f]{6}$')

class CategoryCreate(BaseModel):
    name: str
    color: str | None = None

    @field_validator('color')
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError('Color must be hex format (e.g., #FF5733)')
        return v.upper()

class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None

    @field_validator('color')
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError('Color must be hex format (e.g., #FF5733)')
        return v.upper()

class CategoryResponse(BaseModel):
    id: int
    user_id: str
    name: str
    color: str | None
    created_at: datetime

class CategoryWithCount(CategoryResponse):
    task_count: int
```

**File**: `phaseV/backend/app/schemas/tag.py` (similar structure to category)

**File**: `phaseV/backend/app/schemas/task.py` (enhance existing with new fields)

---

### Phase 4: Service Layer

#### Step 9: Create Service Functions

**File**: `phaseV/backend/app/services/category_service.py`
```python
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.category import Category
from app.models.task import TaskPhaseIII
from app.schemas.category import CategoryCreate, CategoryUpdate

async def create_category(
    category_data: CategoryCreate,
    user_id: str,
    session: AsyncSession
) -> Category:
    # Check 50-category limit
    result = await session.execute(
        select(func.count()).select_from(Category).where(Category.user_id == user_id)
    )
    count = result.scalar_one()
    if count >= 50:
        raise ValueError("Maximum 50 categories reached")

    # Create category
    category = Category(
        user_id=user_id,
        name=category_data.name,
        color=category_data.color
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

# Additional functions: list_categories, update_category, delete_category
```

**File**: `phaseV/backend/app/services/tag_service.py` (similar structure)

**File**: `phaseV/backend/app/services/search_service.py`
```python
from sqlmodel import select, func, text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import TaskPhaseIII

async def search_tasks(
    query: str,
    user_id: str,
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0
) -> list[TaskPhaseIII]:
    # Full-text search with ranking
    stmt = (
        select(TaskPhaseIII)
        .where(
            TaskPhaseIII.user_id == user_id,
            func.to_tsvector('english', TaskPhaseIII.title + ' ' + TaskPhaseIII.description)
            .match(func.to_tsquery('english', query))
        )
        .order_by(
            func.ts_rank(
                func.to_tsvector('english', TaskPhaseIII.title + ' ' + TaskPhaseIII.description),
                func.to_tsquery('english', query)
            ).desc()
        )
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(stmt)
    return result.scalars().all()
```

**File**: `phaseV/backend/app/utils/rrule_parser.py`
```python
from dateutil.rrule import rrulestr
from datetime import datetime

def validate_rrule(rule_string: str) -> bool:
    """Validate iCalendar RRULE format."""
    try:
        rrulestr(f"DTSTART:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\nRRULE:{rule_string}")
        return True
    except (ValueError, AttributeError):
        return False
```

---

### Phase 5: MCP Tools

#### Step 10: Enhance MCP Tools

**File**: `phaseV/backend/app/mcp/tools.py` (major enhancement)

Implement all 17 MCP tools following the contract in `contracts/mcp-tools.md`. Key patterns:

```python
from mcp import Tool
from app.services.category_service import create_category, list_categories
from app.services.tag_service import create_tag, add_tag_to_task
from app.services.search_service import search_tasks

# Enhanced add_task tool
@mcp_server.tool()
async def add_task(
    title: str,
    description: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    category_id: int | None = None,
    tag_ids: list[int] | None = None,
    recurrence_rule: str | None = None
) -> dict:
    """Create task with advanced features."""
    # Validate inputs
    # Create task in database
    # Assign tags
    # Return structured response
    pass

# New create_category tool
@mcp_server.tool()
async def create_category(name: str, color: str | None = None) -> dict:
    """Create a new category."""
    pass

# New search_tasks tool
@mcp_server.tool()
async def search_tasks(query: str, limit: int = 20) -> dict:
    """Full-text search across tasks."""
    pass
```

---

### Phase 6: Testing

#### Step 11: Write Unit Tests

**File**: `phaseV/backend/tests/test_category_service.py`
```python
import pytest
from app.services.category_service import create_category, list_categories
from app.schemas.category import CategoryCreate

@pytest.mark.asyncio
async def test_create_category(async_session):
    category_data = CategoryCreate(name="Work", color="#FF5733")
    category = await create_category(category_data, "user_123", async_session)
    assert category.name == "Work"
    assert category.color == "#FF5733"

@pytest.mark.asyncio
async def test_category_limit_enforcement(async_session):
    # Create 50 categories
    for i in range(50):
        await create_category(CategoryCreate(name=f"Cat{i}"), "user_123", async_session)

    # 51st category should fail
    with pytest.raises(ValueError, match="Maximum 50 categories"):
        await create_category(CategoryCreate(name="Cat51"), "user_123", async_session)
```

**File**: `phaseV/backend/tests/test_mcp_tools.py` (enhance with new tools)

**File**: `phaseV/backend/tests/test_search_service.py`

#### Step 12: Run Tests
```bash
cd phaseV/backend
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Target: ≥80% coverage
```

---

## Validation Checklist

Before marking implementation complete, verify:

- [ ] **Migration Applied**: `alembic current` shows latest revision
- [ ] **Models Created**: All 4 models (TaskPhaseIII enhanced, Category, TagPhaseV, TaskTags) exist
- [ ] **Services Implemented**: category_service, tag_service, search_service, task_service enhanced
- [ ] **MCP Tools**: All 17 tools implemented and registered
- [ ] **Tests Pass**: `pytest` exits with 0 (all tests passing)
- [ ] **Coverage**: ≥80% backend coverage
- [ ] **Linting**: `ruff check .` passes with no errors
- [ ] **Full-Text Search**: Search queries return ranked results
- [ ] **Data Isolation**: Multi-user tests pass (User A cannot access User B's data)

---

## Example Workflows

### Workflow 1: Create Task with Category and Tags
```python
# 1. Create category
category = await mcp_client.call_tool("create_category", {"name": "Work", "color": "#FF5733"})

# 2. Create tags
tag1 = await mcp_client.call_tool("create_tag", {"name": "urgent", "color": "#FF0000"})
tag2 = await mcp_client.call_tool("create_tag", {"name": "meeting"})

# 3. Create task with all features
task = await mcp_client.call_tool("add_task", {
    "title": "Prepare Q1 presentation",
    "description": "Create slides for board meeting",
    "priority": "high",
    "due_date": "2025-01-15T17:00:00-05:00",
    "category_id": category["id"],
    "tag_ids": [tag1["id"], tag2["id"]],
    "recurrence_rule": None
})
```

### Workflow 2: Search and Filter Tasks
```python
# Search for tasks containing "presentation"
results = await mcp_client.call_tool("search_tasks", {
    "query": "presentation",
    "category_id": 5,  # Filter by Work category
    "limit": 10
})

# List high priority tasks
tasks = await mcp_client.call_tool("list_tasks", {
    "priority": "high",
    "sort_by": "due_date",
    "sort_order": "asc"
})
```

---

## Troubleshooting

### Migration Fails
```bash
# Check current revision
uv run alembic current

# If stuck, rollback and retry
uv run alembic downgrade -1
uv run alembic upgrade head
```

### Full-Text Search Not Working
```bash
# Verify GIN index exists
psql $DATABASE_URL -c "\d+ tasks_phaseiii"

# Manually rebuild search_vector
psql $DATABASE_URL -c "UPDATE tasks_phaseiii SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))"
```

### Tests Failing
```bash
# Run specific test file
uv run pytest tests/test_category_service.py -v

# Run with detailed output
uv run pytest -vv --tb=short
```

---

## Next Steps

After completing 001-foundation-api:

1. **Create PHR**: Run `/sp.phr --title "Foundation API implementation" --stage implementation`
2. **Create Pull Request**: Merge `001-foundation-api` → `main`
3. **Feature 002**: Event-Driven Architecture with Kafka (add Kafka producers to MCP tools)
4. **Feature 003**: Dapr Integration (abstract infrastructure behind Dapr APIs)
5. **Feature 004**: Cloud Deployment (Oracle Cloud OKE, CI/CD, monitoring)

---

**End of Quickstart Guide**
