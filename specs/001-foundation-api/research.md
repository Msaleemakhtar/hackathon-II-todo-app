# Research: Advanced Task Management Foundation

**Feature**: 001-foundation-api
**Date**: 2025-12-30
**Phase**: 0 - Research & Design Decisions

## Overview

This document captures research findings and design decisions for implementing Phase V advanced task management capabilities, including database schema evolution, enhanced MCP tools, and full-text search infrastructure.

---

## Research Areas

### 1. PostgreSQL Full-Text Search with tsvector

**Question**: How to implement full-text search on task titles and descriptions using PostgreSQL tsvector + GIN indexes?

**Decision**: Use `tsvector` computed column with GIN index for efficient full-text search

**Rationale**:
- PostgreSQL native full-text search is simpler than external search engines (Elasticsearch, Meilisearch)
- `tsvector` stores lexemes (normalized tokens) for fast searching
- GIN (Generalized Inverted Index) provides optimal performance for full-text queries
- Supports ranking with `ts_rank()` for relevance-based ordering
- No additional infrastructure dependencies

**Implementation Approach**:
```sql
-- Add tsvector column to tasks_phaseiii table
ALTER TABLE tasks_phaseiii ADD COLUMN search_vector tsvector;

-- Create GIN index for fast full-text search
CREATE INDEX idx_tasks_search_vector ON tasks_phaseiii USING GIN (search_vector);

-- Update search_vector automatically via trigger
CREATE TRIGGER tasks_search_vector_update BEFORE INSERT OR UPDATE
ON tasks_phaseiii FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);

-- Also store pre-computed rank for optimization (optional)
ALTER TABLE tasks_phaseiii ADD COLUMN search_rank real;
```

**Query Pattern**:
```python
# SQLModel query with full-text search
query = select(TaskPhaseIII).where(
    TaskPhaseIII.user_id == user_id,
    func.to_tsvector('english', TaskPhaseIII.title + ' ' + TaskPhaseIII.description).match(search_query)
).order_by(
    func.ts_rank(TaskPhaseIII.search_vector, func.to_tsquery('english', search_query)).desc()
)
```

**Alternatives Considered**:
- **Elasticsearch**: Rejected - Over-engineered for 10k tasks/user; adds operational complexity
- **Meilisearch**: Rejected - Requires separate service; overkill for PostgreSQL-backed app
- **LIKE queries**: Rejected - Poor performance; no ranking; doesn't scale to 10k tasks

**References**:
- PostgreSQL Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- GIN Indexes: https://www.postgresql.org/docs/current/gin.html
- SQLModel with PostgreSQL Full-Text: https://sqlmodel.tiangolo.com/

---

### 2. iCalendar RRULE Format for Recurring Tasks

**Question**: How to validate and parse recurrence rules using the iCalendar RRULE standard?

**Decision**: Use `python-dateutil` library for RRULE parsing and validation; store raw RRULE string in database

**Rationale**:
- RFC 5545 (iCalendar) is the industry standard for recurrence rules
- `python-dateutil.rrule` provides robust parsing and validation
- RRULE strings are human-readable and portable (e.g., `FREQ=WEEKLY;BYDAY=MO,WE,FR`)
- Backend validates format but doesn't generate task instances (deferred to 002-event-streaming feature)

**Implementation Approach**:
```python
from dateutil.rrule import rrulestr
from datetime import datetime

# Validation utility
def validate_rrule(rule_string: str) -> bool:
    """Validate iCalendar RRULE format."""
    try:
        # Parse RRULE with a reference date
        rrulestr(f"DTSTART:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\nRRULE:{rule_string}")
        return True
    except (ValueError, AttributeError):
        return False

# Example valid RRULEs:
# - FREQ=DAILY
# - FREQ=WEEKLY;BYDAY=MO,WE,FR
# - FREQ=MONTHLY;BYMONTHDAY=15
# - FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25
```

**Database Storage**:
- `recurrence_rule` field: `TEXT` (nullable) storing raw RRULE string
- Validation at API level before persisting
- Future consumer service (002-event-streaming) will parse RRULE to generate instances

**Alternatives Considered**:
- **Custom JSON format**: Rejected - Not portable; reinventing the wheel
- **Cron syntax**: Rejected - Limited to specific intervals; not flexible for complex recurrence
- **ical library**: Rejected - Heavier than dateutil; unnecessary features

**References**:
- RFC 5545 (iCalendar): https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10
- python-dateutil RRULE: https://dateutil.readthedocs.io/en/stable/rrule.html

---

### 3. Priority Enum Design

**Question**: Should priority be stored as ENUM, VARCHAR, or INTEGER with lookup table?

**Decision**: Use SQLModel/PostgreSQL ENUM type with values: `low`, `medium`, `high`, `urgent`

**Rationale**:
- Type safety at database level (invalid values rejected by PostgreSQL)
- Clear semantics (text values are self-documenting)
- Efficient storage (internally stored as integers)
- Easy to extend via migration if additional levels needed
- Aligns with Phase II standards (constitution specifies Phase V adds "urgent" level)

**Implementation Approach**:
```python
from enum import Enum as PyEnum
from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column

class PriorityLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskPhaseIII(SQLModel, table=True):
    # ...
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        sa_column=Column(SQLEnum(PriorityLevel), nullable=False)
    )
```

**Alternatives Considered**:
- **VARCHAR**: Rejected - No type safety; allows typos ("hgih")
- **INTEGER with lookup table**: Rejected - Adds unnecessary join complexity; opaque values
- **Boolean flags (is_urgent, is_high)**: Rejected - Not scalable; mutual exclusivity not enforced

**References**:
- SQLModel Enums: https://sqlmodel.tiangolo.com/tutorial/fields/#enum-fields
- PostgreSQL ENUM: https://www.postgresql.org/docs/current/datatype-enum.html

---

### 4. Tag Limit Enforcement

**Question**: How to enforce "maximum 10 tags per task" at database level vs application level?

**Decision**: Enforce at application level (service layer) with database constraint as fallback

**Rationale**:
- Application-level validation provides better error messages
- Database constraint (CHECK on count) prevents data corruption if validation bypassed
- PostgreSQL doesn't natively support "count of related rows" in CHECK constraints
- Defense-in-depth approach: application validates, database prevents corruption

**Implementation Approach**:
```python
# Application-level validation in service layer
async def add_tag_to_task(task_id: int, tag_id: int, user_id: str, session: AsyncSession):
    # Count existing tags
    result = await session.execute(
        select(func.count()).select_from(TaskTags).where(TaskTags.task_id == task_id)
    )
    tag_count = result.scalar_one()

    if tag_count >= 10:
        raise ValueError("Maximum 10 tags per task exceeded")

    # Proceed with tag assignment...
```

**Database Fallback** (via trigger - optional):
```sql
-- Trigger function to enforce 10-tag limit
CREATE OR REPLACE FUNCTION enforce_tag_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM task_tags WHERE task_id = NEW.task_id) > 10 THEN
        RAISE EXCEPTION 'Maximum 10 tags per task exceeded';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_tag_limit
AFTER INSERT ON task_tags
FOR EACH ROW EXECUTE FUNCTION enforce_tag_limit();
```

**Alternatives Considered**:
- **Database-only enforcement**: Rejected - Poor error messages; harder to test
- **No enforcement**: Rejected - Violates spec requirement FR-005
- **Array column (tag_ids)**: Rejected - Violates normalization; can't reuse tags across tasks

**References**:
- PostgreSQL Triggers: https://www.postgresql.org/docs/current/trigger-definition.html
- Many-to-Many Best Practices: https://en.wikipedia.org/wiki/Many-to-many_(data_model)

---

### 5. Timezone Handling for Due Dates

**Question**: How to handle timezones for due dates - store as UTC, naive datetime, or timestamptz?

**Decision**: Store as UTC `TIMESTAMP` (without timezone); clients send/receive ISO 8601 with timezone; backend converts to UTC

**Rationale**:
- Aligns with constitution requirement: "Store as UTC; clients send/receive ISO 8601 with timezone; server converts to UTC for storage"
- UTC storage simplifies comparison, sorting, and filtering
- ISO 8601 format (`2025-01-15T17:00:00-05:00`) preserves client timezone information in transit
- Python `datetime.fromisoformat()` handles timezone-aware parsing
- Database stores canonical UTC representation

**Implementation Approach**:
```python
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):
    title: str
    due_date: datetime | None = None

    @field_validator('due_date')
    @classmethod
    def convert_to_utc(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        # If timezone-aware, convert to UTC; if naive, assume UTC
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

# Database model
class TaskPhaseIII(SQLModel, table=True):
    due_date: datetime | None = Field(default=None, nullable=True)
    # SQLModel maps to PostgreSQL TIMESTAMP (without timezone)
```

**Client Behavior**:
- Client sends: `{"due_date": "2025-01-15T17:00:00-05:00"}` (ISO 8601 with timezone)
- Backend converts to UTC: `2025-01-15T22:00:00` (stored in DB)
- Client retrieves: `"2025-01-15T22:00:00Z"` (ISO 8601 UTC)
- Client displays: Converted to user's local timezone

**Alternatives Considered**:
- **TIMESTAMPTZ (with timezone)**: Rejected - Constitution specifies TIMESTAMP; PostgreSQL stores UTC internally anyway
- **Naive datetime (no timezone)**: Rejected - Ambiguous; can't distinguish user timezones
- **Date-only (no time)**: Rejected - Requirements specify "date and time precision"

**References**:
- ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
- Python datetime: https://docs.python.org/3/library/datetime.html
- PostgreSQL Timestamp Types: https://www.postgresql.org/docs/current/datatype-datetime.html

---

### 6. Unique Constraints for Category/Tag Names

**Question**: Should category/tag names be unique globally or per-user?

**Decision**: Unique per-user (composite unique constraint on `user_id + name`)

**Rationale**:
- Requirements specify: "System MUST enforce unique category names per user" (FR-011)
- Different users can have categories/tags with the same name
- Case-sensitive uniqueness (per spec: FR-011, FR-012)
- Prevents duplicate organizational structures within a single user's workspace

**Implementation Approach**:
```python
class Category(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_category_user_name'),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=50, nullable=False)
    color: str | None = Field(max_length=7, nullable=True)  # Hex format: #FF5733
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class TagPhaseV(SQLModel, table=True):
    __tablename__ = "tags_phasev"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_tag_user_name'),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=30, nullable=False)
    color: str | None = Field(max_length=7, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Alternatives Considered**:
- **Global uniqueness**: Rejected - Users should be able to name categories independently
- **Case-insensitive**: Rejected - Spec explicitly states "case-sensitive" (FR-011, FR-012)
- **No uniqueness constraint**: Rejected - Violates requirements FR-011, FR-012

**References**:
- SQLModel Unique Constraints: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#unique-constraints
- PostgreSQL Unique Constraints: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS

---

### 7. Color Code Validation

**Question**: How to validate hex color codes (#FF5733) at database vs application level?

**Decision**: Regex validation at Pydantic schema level; store as VARCHAR(7) in database

**Rationale**:
- Pydantic provides clean validation with clear error messages
- Database constraint as fallback (CHECK with regex)
- Constitution requires "6-character hex format (e.g., #FF5733) or allow empty/null" (FR-015)
- Application-level validation is easier to test and maintain

**Implementation Approach**:
```python
import re
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
        return v.upper()  # Normalize to uppercase
```

**Database Constraint** (optional fallback):
```sql
ALTER TABLE categories ADD CONSTRAINT check_color_format
CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$');
```

**Alternatives Considered**:
- **RGB struct (r, g, b integers)**: Rejected - More complex; hex is standard for web
- **Named colors ("red", "blue")**: Rejected - Spec requires hex format
- **No validation**: Rejected - Violates requirement FR-015

**References**:
- Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
- Hex Color Format: https://en.wikipedia.org/wiki/Web_colors#Hex_triplet

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Full-Text Search** | PostgreSQL tsvector + GIN index | Native, simple, performant; no external dependencies |
| **Recurrence Rules** | iCalendar RRULE with python-dateutil | Industry standard; portable; robust validation |
| **Priority Storage** | PostgreSQL ENUM (low, medium, high, urgent) | Type-safe; efficient; self-documenting |
| **Tag Limit Enforcement** | Application-level + database trigger fallback | Clear errors; defense-in-depth |
| **Timezone Handling** | Store UTC; accept ISO 8601 with TZ | Aligns with constitution; canonical representation |
| **Name Uniqueness** | Per-user composite constraint (user_id + name) | User isolation; prevents duplicates within workspace |
| **Color Validation** | Pydantic regex + database CHECK constraint | Clean errors; fallback safety |

---

## Dependencies & Libraries

### Required (already in pyproject.toml):
- `sqlmodel>=0.0.14` - ORM with Pydantic integration
- `alembic>=1.13.0` - Database migrations
- `asyncpg>=0.29.0` - Async PostgreSQL driver
- `fastapi>=0.109.0` - Web framework
- `pydantic-settings>=2.1.0` - Configuration management

### New Dependencies (to be added):
- `python-dateutil>=2.8.2` - RRULE parsing and validation

### Development Dependencies (already present):
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `ruff>=0.1.0` - Linting and formatting

---

## Next Steps (Phase 1)

1. Generate `data-model.md` with complete entity definitions and relationships
2. Generate API contracts in `contracts/` directory (OpenAPI schemas for MCP tools)
3. Generate `quickstart.md` with setup instructions and example workflows
4. Update agent context with new technologies (python-dateutil)
5. Re-evaluate Constitution Check after design artifacts are complete

---

**End of Research Phase**
