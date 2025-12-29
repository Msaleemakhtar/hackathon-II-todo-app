# Phase V Implementation Plan - Feature Breakdown

**Phase**: V (Event-Driven Cloud Deployment)
**Approach**: Grouped Features (3 specifications for Part A)
**Constitution**: v3.0.0
**Namespace**: todo-phasev

---

## Part A Features: Advanced Task Management (3 Grouped Features)

### Feature 001: Foundation + API Layer (A1 + A2)
**Feature ID**: `sphaseV/001-foundation-api`
**Priority**: P0 (CRITICAL)
**Estimated Effort**: 5-7 days
**Dependencies**: None

**What's Included**:
- Database schema evolution (6 new fields, 3 new tables)
- All 17 MCP tools (5 enhanced + 12 new)
- SQLModel definitions
- Alembic migration
- Unit + integration tests

**Deliverable**: Users can create/manage tasks with priorities, categories, tags, due dates, recurring rules via ChatKit

**Helm Chart Changes**: ✅ None required (backward compatible)

---

### Feature 002: Event-Driven Architecture (A3 + A4 + A5)
**Feature ID**: `sphaseV/002-event-driven`
**Priority**: P0 (CRITICAL)
**Estimated Effort**: 7-10 days
**Dependencies**: Feature 001 (needs enhanced task models)

**What's Included**:
- Redpanda Cloud Kafka integration (3 topics)
- Kafka event producers (in MCP tools)
- Notification Service (Kafka consumer)
- Recurring Task Service (Kafka consumer)
- Full-text search service (PostgreSQL FTS)
- Event schemas and error handling

**Deliverable**: Tasks auto-regenerate on completion, reminders sent, full-text search works, all events flowing through Kafka

**Helm Chart Changes**: ✅ **REQUIRED**
- NEW: `templates/kafka-secret.yaml`
- NEW: `templates/notification-deployment.yaml`
- NEW: `templates/notification-service.yaml`
- NEW: `templates/recurring-deployment.yaml`
- NEW: `templates/recurring-service.yaml`
- UPDATE: `templates/configmap.yaml` (add Kafka config)
- UPDATE: `templates/backend-deployment.yaml` (add Kafka env vars)
- UPDATE: `values.yaml` (add kafka.brokers, kafka.username, kafka.password)

---

### Feature 003: ChatKit UI Enhancements (A6)
**Feature ID**: `sphaseV/003-chatkit-ui`
**Priority**: P1 (High)
**Estimated Effort**: 3-5 days
**Dependencies**: Feature 001, Feature 002

**What's Included**:
- Updated ChatKit system prompts
- Enhanced suggested prompts
- Visual indicators for priorities (color coding)
- Due date display with countdown
- Tag badges in responses
- Category chips
- Natural language date parsing examples

**Deliverable**: Beautiful, intuitive UI showing all Phase V features

**Helm Chart Changes**: ✅ **REQUIRED**
- UPDATE: `templates/frontend-deployment.yaml` (add ChatKit config env vars)
- UPDATE: `values.yaml` (add chatkit.systemPrompt, chatkit.suggestedPrompts)

---

## Part B Features: Dapr Integration (4 Features)

### Feature 004: Dapr Foundation (B1 + B2)
**Feature ID**: `sphaseV/004-dapr-foundation`
**Priority**: P1 (High)
**Estimated Effort**: 4-6 days
**Dependencies**: Feature 002 (migrating from direct Kafka)

**What's Included**:
- Dapr CLI installation
- Dapr initialization on Kubernetes (`dapr init -k`)
- 4 Dapr component YAMLs (Pub/Sub, State Store, Secrets, Jobs)
- Dapr component documentation

**Deliverable**: Dapr running on Kubernetes with all components configured

**Helm Chart Changes**: ✅ **REQUIRED**
- NEW: `dapr-components/pubsub-kafka.yaml`
- NEW: `dapr-components/statestore-postgres.yaml`
- NEW: `dapr-components/secrets-kubernetes.yaml`
- NEW: `dapr-components/jobs-scheduler.yaml`

---

### Feature 005: Dapr Migration (B3 + B4)
**Feature ID**: `sphaseV/005-dapr-migration`
**Priority**: P1 (High)
**Estimated Effort**: 5-7 days
**Dependencies**: Feature 004

**What's Included**:
- Migrate Kafka producers from aiokafka to Dapr Pub/Sub HTTP API
- Migrate Kafka consumers to Dapr subscriptions
- Dapr Jobs API for reminders (replace cron polling)
- Remove direct Kafka client dependencies
- Update all deployments with Dapr annotations

**Deliverable**: Same functionality as Feature 002, but infrastructure-agnostic via Dapr

**Helm Chart Changes**: ✅ **REQUIRED**
- UPDATE: `templates/backend-deployment.yaml` (add Dapr annotations, remove Kafka env vars)
- UPDATE: `templates/notification-deployment.yaml` (add Dapr annotations)
- UPDATE: `templates/recurring-deployment.yaml` (add Dapr annotations)
- UPDATE: `templates/mcp-deployment.yaml` (add Dapr annotations)
- UPDATE: `values.yaml` (add dapr.enabled, dapr.appId, dapr.logLevel)
- DELETE: `templates/kafka-secret.yaml` (Dapr component handles it)

---

## Part C Features: Production Cloud Deployment (5 Features)

### Feature 006: Oracle Cloud Foundation (C1 + C2)
**Feature ID**: `sphaseV/006-oke-foundation`
**Priority**: P1 (High)
**Estimated Effort**: 5-7 days
**Dependencies**: Feature 005 (Dapr-enabled)

**What's Included**:
- Oracle Cloud OKE cluster setup (2 nodes, 4 OCPU each)
- VCN and subnet configuration
- OCIR (Oracle Container Registry) setup
- Production Helm values (values-production.yaml)
- cert-manager installation
- Let's Encrypt ClusterIssuer
- Domain DNS configuration

**Deliverable**: OKE cluster running, HTTPS working with Let's Encrypt certificates

**Helm Chart Changes**: ✅ **REQUIRED**
- NEW: `values-production.yaml` (production-specific configuration)
- UPDATE: `templates/ingress.yaml` (add TLS configuration, cert-manager annotations)

---

### Feature 007: CI/CD Pipeline (C3)
**Feature ID**: `sphaseV/007-cicd`
**Priority**: P1 (High)
**Estimated Effort**: 4-6 days
**Dependencies**: Feature 006

**What's Included**:
- GitHub Actions workflow: `ci-phase-v.yml` (lint, test, build)
- GitHub Actions workflow: `deploy-production.yml` (deploy to OKE)
- Docker image builds and push to OCIR
- Helm deployment automation
- Smoke tests post-deployment
- Slack/Discord notifications

**Deliverable**: Automated build and deployment on every release tag

**Helm Chart Changes**: ✅ None (uses existing charts)

---

### Feature 008: Monitoring Stack (C4)
**Feature ID**: `sphaseV/008-monitoring`
**Priority**: P2 (Medium)
**Estimated Effort**: 4-6 days
**Dependencies**: Feature 006

**What's Included**:
- Prometheus installation (kube-prometheus-stack)
- Grafana dashboards (HTTP, tasks, pods, HPA)
- ServiceMonitor for backend metrics
- Backend metrics instrumentation (prometheus-client)
- AlertManager configuration
- Loki for log aggregation (optional)

**Deliverable**: Full observability with metrics, dashboards, and alerts

**Helm Chart Changes**: ✅ **REQUIRED**
- NEW: `templates/prometheus-servicemonitor.yaml`
- UPDATE: `templates/backend-deployment.yaml` (expose /metrics endpoint)
- UPDATE: `values.yaml` (add monitoring.prometheus.enabled, monitoring.grafana.enabled)

---

### Feature 009: Production Hardening (C5)
**Feature ID**: `sphaseV/009-security`
**Priority**: P1 (High)
**Estimated Effort**: 3-5 days
**Dependencies**: Feature 006

**What's Included**:
- NetworkPolicies (deny-all default, allow specific)
- RBAC policies (service accounts, roles, rolebindings)
- Pod Security Standards (non-root, read-only filesystem, drop capabilities)
- Resource Quotas and LimitRanges
- Pod anti-affinity for HA
- Velero backup strategy
- Security scanning (Trivy)

**Deliverable**: Production-hardened, secure deployment

**Helm Chart Changes**: ✅ **REQUIRED**
- NEW: `templates/networkpolicy.yaml` (for each service)
- NEW: `templates/rbac.yaml` (ServiceAccounts, Roles, RoleBindings)
- NEW: `templates/resourcequota.yaml`
- UPDATE: All deployments (add securityContext, serviceAccountName)

---

## Feature Summary Table

| ID | Feature Name | Part | Effort | Helm Changes | Blocks |
|----|--------------|------|--------|--------------|--------|
| 001 | Foundation + API | A | 5-7d | None | 002, 003 |
| 002 | Event-Driven | A | 7-10d | Required | 003, 004 |
| 003 | ChatKit UI | A | 3-5d | Required | - |
| 004 | Dapr Foundation | B | 4-6d | Required | 005 |
| 005 | Dapr Migration | B | 5-7d | Required | 006 |
| 006 | OKE Foundation | C | 5-7d | Required | 007, 008, 009 |
| 007 | CI/CD Pipeline | C | 4-6d | None | - |
| 008 | Monitoring Stack | C | 4-6d | Required | - |
| 009 | Security Hardening | C | 3-5d | Required | - |

**Total Estimated Effort**: 40-60 days (8-12 weeks)

**Critical Path**: 001 → 002 → 004 → 005 → 006 → 009

---

## Current Specification: Feature 001

Below is the complete specification prompt for **Feature 001: Foundation + API Layer**

---

# Specification Prompt: Feature 001 - Foundation + API Layer

**Feature Name**: Foundation + API Layer (Database Schema Evolution + Enhanced MCP Tools)
**Feature ID**: sphaseV/001-foundation-api
**Phase**: V (Event-Driven Cloud Deployment)
**Part**: A (Advanced Features) - Features A1 + A2
**Priority**: P0 (CRITICAL - Blocks all other Phase V features)

---

## Feature Overview

Evolve the Phase III `tasks_phaseiii` database schema to support advanced task management capabilities including priorities, categories, tags, due dates, recurring tasks, reminders, and full-text search. This is the foundational feature that enables all other Phase V functionality.

**Current State (Phase IV)**:
- Basic task model: id, user_id, title, description, completed, created_at, updated_at
- Single table: `tasks_phaseiii`
- No advanced metadata (priorities, categories, tags, due dates)
- No search capabilities beyond exact matches

**Target State (Phase V)**:
- Enhanced task model with 6 new fields: priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector
- 3 new tables: categories, tags_phasev, task_tags (junction)
- Full-text search with PostgreSQL tsvector + GIN indexes
- 8 new composite indexes for performance
- Support for advanced filtering, sorting, and search

---

## Business Context

### Problem Statement
Users need advanced task organization capabilities beyond simple to-do lists:
- **Priority Management**: Distinguish between urgent vs. low-priority tasks
- **Temporal Planning**: Set due dates and receive reminders
- **Organization**: Group tasks by categories and apply multiple tags
- **Discoverability**: Full-text search across task titles and descriptions
- **Automation**: Recurring tasks that auto-regenerate on completion

### Success Metrics
- Database migration completes in <10 seconds on existing data
- Query performance: <200ms p95 for filtered/sorted queries
- Full-text search returns results in <200ms p95
- Zero data loss during migration
- Backward compatibility: Existing Phase III data remains accessible

### Out of Scope (Explicitly Not Included)
- Subtasks or task dependencies
- Task sharing between users
- File attachments
- External calendar integrations
- Real-time collaborative editing

---

## Constitutional Compliance

This feature must comply with Constitution v3.0.0:

**Principle III - Persistent & Relational State**:
- Use SQLModel for all data access
- Alembic migrations for schema changes (reversible)
- Async database operations (asyncpg driver)
- Connection pooling in production

**Principle XVI - Event-Driven Architecture**:
- While schema evolution itself is synchronous, the updated models will support event-driven features
- New fields (due_date, recurrence_rule) enable Kafka event publishing in subsequent features

**Phase V Data Models** (from Constitution):
- Enhanced tasks_phaseiii table
- New categories table
- New tags_phasev table (separate from Phase II tags)
- New task_tags junction table

---

## Functional Requirements

### FR-P5-001: Enhanced Task Model
**As a** user
**I want** tasks to have priority levels, due dates, categories, tags, and recurrence rules
**So that** I can organize and plan my work effectively

**Acceptance Criteria**:
- Tasks have priority field: enum of "low", "medium", "high", "urgent" (default: "medium")
- Tasks have optional due_date field: timestamp (nullable)
- Tasks have optional category_id field: foreign key to categories table
- Tasks have optional recurrence_rule field: iCal RRULE format string (nullable)
- Tasks have reminder_sent boolean flag: tracks if reminder notification sent (default: false)
- All new fields are nullable except priority (allows gradual adoption)
- Existing tasks receive default values during migration

**Edge Cases**:
- Invalid priority values → validation error (400)
- Invalid RRULE format → validation error with helpful message
- Due dates in the past → allowed (for historical tasks)
- Category deleted → task.category_id set to NULL (soft delete)
- Recurrence rule without due_date → validation warning (recurrence requires base date)

---

### FR-P5-002: Category Management
**As a** user
**I want** to create custom categories to organize my tasks
**So that** I can group related tasks together (e.g., "Work", "Personal", "Urgent")

**Acceptance Criteria**:
- Users can create categories with: name (required, max 50 chars), color (optional, hex format)
- Category names must be unique per user
- Categories are user-scoped (cannot see other users' categories)
- Maximum 50 categories per user
- Category has timestamps: created_at

**Validation Rules**:
- Name: 1-50 characters, trimmed, no leading/trailing whitespace
- Color: Must match regex `^#[0-9A-Fa-f]{6}$` or be null
- Duplicate name (same user) → validation error (409 Conflict)

**Edge Cases**:
- Deleting category with tasks → tasks.category_id set to NULL (cascade)
- Renaming category → no impact on existing task associations
- Color not provided → stored as NULL (frontend renders default color)

---

### FR-P5-003: Tag Management
**As a** user
**I want** to apply multiple tags to tasks for flexible filtering
**So that** I can cross-categorize tasks (e.g., tag "urgent" + "meeting" + "client-project")

**Acceptance Criteria**:
- Users can create tags with: name (required, max 30 chars), color (optional, hex format)
- Tag names must be unique per user
- Tasks support many-to-many relationship with tags (junction table: task_tags)
- Maximum 100 tags per user
- Maximum 10 tags per task
- Tags are user-scoped (cannot see other users' tags)

**Validation Rules**:
- Name: 1-30 characters, trimmed
- Color: Must match regex `^#[0-9A-Fa-f]{6}$` or be null
- Duplicate name (same user) → validation error (409 Conflict)
- Assigning tag to task: both must belong to same user (403 Forbidden otherwise)

**Edge Cases**:
- Deleting tag → removes all task_tags associations (cascade delete)
- Assigning duplicate tag to task → idempotent (no error, no duplicate rows)
- Assigning 11th tag to task → validation error (400)

---

### FR-P5-004: Full-Text Search Support
**As a** user
**I want** to search tasks by keywords in title and description
**So that** I can quickly find relevant tasks without scrolling

**Acceptance Criteria**:
- Tasks have `search_vector` column: PostgreSQL tsvector type
- Search vector automatically updated via database trigger on INSERT/UPDATE
- Title words weighted higher (weight 'A') than description words (weight 'B')
- GIN index created on search_vector for fast lookups
- Search queries use `plainto_tsquery` for natural language parsing
- Results ranked by `ts_rank` relevance score

**Technical Implementation**:
```sql
-- Trigger function
CREATE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER task_search_update
    BEFORE INSERT OR UPDATE ON tasks_phaseiii
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- GIN index
CREATE INDEX idx_tasks_search_vector ON tasks_phaseiii USING GIN(search_vector);
```

**Edge Cases**:
- Empty search query → return all tasks (no filter applied)
- No matches → return empty array (not an error)
- Special characters in query → sanitized by plainto_tsquery
- Non-English words → may have reduced relevance (English stemmer used)

---

### FR-P5-005: Recurring Tasks Support
**As a** user
**I want** to create tasks that repeat on a schedule (daily, weekly, monthly)
**So that** I don't have to manually recreate routine tasks

**Acceptance Criteria**:
- Tasks have `recurrence_rule` field storing iCal RRULE format
- Supported RRULE patterns:
  - `FREQ=DAILY` → repeats every day
  - `FREQ=WEEKLY;BYDAY=MO,WE,FR` → repeats on specific weekdays
  - `FREQ=MONTHLY;BYMONTHDAY=1` → repeats on specific day of month
  - `FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1` → repeats annually
- Recurrence rule validated on creation/update
- Tasks with recurrence_rule are marked in UI
- Actual recurrence logic implemented in Part A5 (Recurring Task Service)

**Validation Rules**:
- RRULE must be valid iCal format
- Invalid RRULE → validation error with example
- Recurrence rule without due_date → warning (but allowed)

**Edge Cases**:
- Removing recurrence_rule from task → allowed (stops future recurrence)
- Updating recurrence_rule → applies to next occurrence, not past
- Complex RRULE patterns → validated but may not be fully supported until Part A5

---

## Non-Functional Requirements

### QR-P5-001: Database Migration Performance
- Migration must complete in <10 seconds on 10,000 existing tasks
- No downtime during migration (online schema change if possible)
- Rollback script must be tested and documented

### QR-P5-002: Query Performance
- List tasks with filters: <200ms p95 latency
- Full-text search: <200ms p95 latency for 10,000 tasks
- Category/tag lookup: <50ms p95 (indexed)
- All queries use proper indexes (verified with EXPLAIN ANALYZE)

### QR-P5-003: Data Integrity
- All foreign keys enforced at database level
- Cascade deletes configured correctly (categories → NULL, tags → delete junction rows)
- Unique constraints enforced (category names, tag names per user)
- Check constraints for priority enum values

### QR-P5-004: Backward Compatibility
- Existing Phase III tasks continue to work
- API endpoints remain functional with new optional fields
- Phase IV Kubernetes deployments can roll back to previous schema

---

## Data Model Specification

### Enhanced tasks_phaseiii Table

| Field           | Type      | Constraints                          | Description                         | New? |
|-----------------|-----------|--------------------------------------|-------------------------------------|------|
| id              | int       | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier              | No   |
| user_id         | str       | INDEX, NOT NULL                      | Owner user ID from Better Auth      | No   |
| title           | str       | NOT NULL, max 200 chars              | Task title                          | No   |
| description     | str       | NULLABLE                             | Task description                    | No   |
| completed       | bool      | NOT NULL, DEFAULT False              | Completion status                   | No   |
| priority        | str       | NOT NULL, DEFAULT 'medium'           | **NEW**: Enum: low, medium, high, urgent | ✅   |
| due_date        | timestamp | NULLABLE                             | **NEW**: Task due date and time     | ✅   |
| category_id     | int       | NULLABLE, FK → categories.id         | **NEW**: Task category              | ✅   |
| recurrence_rule | str       | NULLABLE                             | **NEW**: iCal RRULE string          | ✅   |
| reminder_sent   | bool      | NOT NULL, DEFAULT False              | **NEW**: Reminder notification flag | ✅   |
| search_vector   | tsvector  | GENERATED, GIN indexed               | **NEW**: Full-text search vector    | ✅   |
| created_at      | timestamp | NOT NULL, DEFAULT now()              | Creation timestamp                  | No   |
| updated_at      | timestamp | NOT NULL, DEFAULT now(), ON UPDATE   | Last modification timestamp         | No   |

**Indexes**:
- Existing: `idx_tasks_phaseiii_user_id` (user_id)
- **NEW**: `idx_tasks_phaseiii_priority` (user_id, priority)
- **NEW**: `idx_tasks_phaseiii_due_date` (user_id, due_date)
- **NEW**: `idx_tasks_phaseiii_category` (category_id)
- **NEW**: `idx_tasks_search_vector` USING GIN (search_vector)

**Constraints**:
- **NEW**: CHECK (priority IN ('low', 'medium', 'high', 'urgent'))

---

### categories Table (NEW)

| Field      | Type      | Constraints                          | Description                         |
|------------|-----------|--------------------------------------|-------------------------------------|
| id         | int       | PRIMARY KEY, AUTOINCREMENT           | Unique category identifier          |
| user_id    | str       | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| name       | str       | NOT NULL, max 50 chars               | Category display name               |
| color      | str       | NULLABLE, CHECK matches hex format   | Category color for UI (#RRGGBB)     |
| created_at | timestamp | NOT NULL, DEFAULT now()              | Creation timestamp                  |

**Indexes**:
- `idx_categories_user` (user_id)
- `idx_categories_user_name` UNIQUE (user_id, name) - Enforce unique names per user

**Constraints**:
- UNIQUE(user_id, name)
- CHECK (length(trim(name)) >= 1 AND length(name) <= 50)
- CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')

---

### tags_phasev Table (NEW)

| Field      | Type      | Constraints                          | Description                         |
|------------|-----------|--------------------------------------|-------------------------------------|
| id         | int       | PRIMARY KEY, AUTOINCREMENT           | Unique tag identifier               |
| user_id    | str       | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| name       | str       | NOT NULL, max 30 chars               | Tag display name                    |
| color      | str       | NULLABLE, CHECK matches hex format   | Tag color for UI (#RRGGBB)          |
| created_at | timestamp | NOT NULL, DEFAULT now()              | Creation timestamp                  |

**Indexes**:
- `idx_tags_phasev_user` (user_id)
- `idx_tags_phasev_user_name` UNIQUE (user_id, name)

**Constraints**:
- UNIQUE(user_id, name)
- CHECK (length(trim(name)) >= 1 AND length(name) <= 30)
- CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')

---

### task_tags Junction Table (NEW)

| Field   | Type | Constraints                          | Description                         |
|---------|------|--------------------------------------|-------------------------------------|
| task_id | int  | FK → tasks_phaseiii.id, PK           | Task reference                      |
| tag_id  | int  | FK → tags_phasev.id, PK              | Tag reference                       |

**Indexes**:
- Composite PRIMARY KEY (task_id, tag_id)
- `idx_task_tags_task` (task_id)
- `idx_task_tags_tag` (tag_id)

**Constraints**:
- ON DELETE CASCADE for both foreign keys (deleting task or tag removes junction row)

---

## Database Migration Plan

### Migration File Structure
```
/phaseV/backend/alembic/versions/YYYYMMDD_HHMMSS_add_advanced_task_fields.py
```

### Migration Steps (Upgrade)

1. **Create new tables**:
   - Create `categories` table with indexes
   - Create `tags_phasev` table with indexes
   - Create `task_tags` junction table with indexes

2. **Alter tasks_phaseiii table**:
   - Add `priority` column (NOT NULL DEFAULT 'medium')
   - Add `due_date` column (NULLABLE)
   - Add `category_id` column (NULLABLE, FK to categories.id)
   - Add `recurrence_rule` column (NULLABLE)
   - Add `reminder_sent` column (NOT NULL DEFAULT false)
   - Add `search_vector` column (tsvector)

3. **Create indexes**:
   - `idx_tasks_phaseiii_priority` (user_id, priority)
   - `idx_tasks_phaseiii_due_date` (user_id, due_date)
   - `idx_tasks_phaseiii_category` (category_id)
   - `idx_tasks_search_vector` USING GIN (search_vector)

4. **Create trigger for search_vector**:
   - Create trigger function `update_search_vector()`
   - Create trigger `task_search_update` on tasks_phaseiii

5. **Backfill search_vector**:
   - Update all existing rows to populate search_vector
   - Use batched updates for performance (1000 rows at a time)

6. **Add check constraint**:
   - Add CHECK constraint for priority values

### Migration Steps (Downgrade)

1. Drop trigger `task_search_update`
2. Drop function `update_search_vector()`
3. Drop indexes (4 new indexes)
4. Drop columns from tasks_phaseiii (priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector)
5. Drop table `task_tags`
6. Drop table `tags_phasev`
7. Drop table `categories`

**Rollback Time**: <5 seconds (dropping is fast)
**Data Loss on Rollback**: Categories, tags, task metadata (priority, due_date, etc.)

---

## SQLModel Definitions

### Task Model (Enhanced)

```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, CheckConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR

class Task(SQLModel, table=True):
    __tablename__ = "tasks_phaseiii"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)

    # NEW: Advanced fields
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = None
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    recurrence_rule: Optional[str] = None
    reminder_sent: bool = Field(default=False)
    search_vector: Optional[str] = Field(sa_column=Column(TSVECTOR))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")

    __table_args__ = (
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="check_priority"),
    )
```

### Category Model (NEW)

```python
class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str = Field(max_length=50)
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List[Task] = Relationship(back_populates="category")

    __table_args__ = (
        CheckConstraint("length(trim(name)) >= 1 AND length(name) <= 50", name="check_name_length"),
        CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name="check_color_format"),
    )
```

### Tag Model (NEW)

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags_phasev"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str = Field(max_length=30)
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List[Task] = Relationship(back_populates="tags", link_model="TaskTag")

    __table_args__ = (
        CheckConstraint("length(trim(name)) >= 1 AND length(name) <= 30", name="check_name_length"),
        CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name="check_color_format"),
    )
```

### TaskTag Junction Model (NEW)

```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks_phaseiii.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags_phasev.id", primary_key=True)
```

---

## Testing Requirements

### Unit Tests (pytest)

**Model Tests** (`tests/test_models_phase_v.py`):
- Task model validation (priority enum, RRULE format)
- Category model validation (name length, color format, unique constraint)
- Tag model validation (name length, color format, unique constraint)
- TaskTag junction model (composite key, cascade deletes)

**Migration Tests** (`tests/test_migrations.py`):
- Migration upgrade succeeds
- Migration downgrade succeeds
- Data preserved after upgrade
- Search vector populated correctly
- Indexes created correctly

### Integration Tests

**Database Tests** (`tests/integration/test_database_phase_v.py`):
- Create task with priority, due_date, category, tags
- Query tasks filtered by priority
- Query tasks filtered by due_date range
- Query tasks filtered by category
- Query tasks filtered by tags
- Full-text search returns relevant results
- Search ranking works correctly
- Cascade delete: category deletion sets task.category_id to NULL
- Cascade delete: tag deletion removes task_tags rows

### Performance Tests

**Load Tests** (`tests/performance/test_phase_v_queries.py`):
- Seed database with 10,000 tasks
- Measure query latency:
  - List tasks filtered by priority: <200ms p95
  - List tasks filtered by due_date: <200ms p95
  - Full-text search: <200ms p95
  - Category lookup: <50ms p95
- Verify all queries use indexes (EXPLAIN ANALYZE)

### Test Data Fixtures

```python
# tests/fixtures/phase_v_data.py
@pytest.fixture
async def sample_category(async_session):
    category = Category(
        user_id="user123",
        name="Work",
        color="#FF5733"
    )
    async_session.add(category)
    await async_session.commit()
    return category

@pytest.fixture
async def sample_tags(async_session):
    tags = [
        Tag(user_id="user123", name="urgent", color="#FF0000"),
        Tag(user_id="user123", name="meeting", color="#00FF00"),
    ]
    async_session.add_all(tags)
    await async_session.commit()
    return tags

@pytest.fixture
async def advanced_task(async_session, sample_category, sample_tags):
    task = Task(
        user_id="user123",
        title="Complete project proposal",
        description="Draft and review Q1 project proposal",
        priority="high",
        due_date=datetime.now() + timedelta(days=7),
        category_id=sample_category.id,
        recurrence_rule="FREQ=WEEKLY;BYDAY=FR"
    )
    async_session.add(task)
    await async_session.commit()

    # Add tags
    for tag in sample_tags:
        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        async_session.add(task_tag)
    await async_session.commit()

    return task
```

---

## API Impact Analysis

**No API Changes Required** - This feature only modifies the database schema and SQLModel definitions. API endpoints will be enhanced in subsequent features (Part A2: Enhanced MCP Tools).

**Backward Compatibility**:
- Existing API endpoints continue to work
- New fields are nullable/have defaults
- Phase IV Kubernetes deployments can query tasks without errors

---

## Documentation Requirements

### Technical Documentation

1. **Migration Guide** (`phaseV/backend/alembic/versions/MIGRATION_GUIDE.md`):
   - Step-by-step migration instructions
   - Rollback procedure
   - Performance considerations
   - Expected downtime (if any)

2. **Database Schema Diagram** (`phaseV/docs/database-schema-phase-v.md`):
   - Entity-relationship diagram
   - Table definitions
   - Index strategy
   - Foreign key relationships

3. **Search Implementation** (`phaseV/docs/full-text-search.md`):
   - PostgreSQL FTS overview
   - Trigger function explanation
   - Query examples
   - Performance tuning tips

### Developer Documentation

1. **Model Usage Examples** (`phaseV/backend/README.md`):
   - Creating tasks with advanced fields
   - Querying with filters
   - Full-text search queries
   - Managing categories and tags

2. **Testing Guide** (`phaseV/backend/tests/README.md`):
   - Running unit tests
   - Running integration tests
   - Performance benchmarks
   - Test data generation

---

## Acceptance Criteria Summary

**Definition of Done**:
- [ ] All 4 SQLModel models defined (Task enhanced, Category, Tag, TaskTag)
- [ ] Alembic migration created and tested (upgrade + downgrade)
- [ ] All 8 database indexes created
- [ ] PostgreSQL FTS trigger function working
- [ ] Migration tested with 10,000 existing tasks (<10s)
- [ ] All unit tests pass (models, validation)
- [ ] All integration tests pass (queries, cascades, search)
- [ ] Performance tests pass (<200ms p95 for all queries)
- [ ] Migration guide documented
- [ ] Database schema diagram created
- [ ] Code reviewed and approved
- [ ] Deployed to local Minikube (Phase V namespace: todo-phasev)
- [ ] Zero data loss verified
- [ ] Rollback tested successfully

---

## Risk Mitigation

### High-Risk Areas

1. **Migration Performance on Large Datasets**
   - **Risk**: Migration takes too long on production database
   - **Mitigation**:
     - Test migration with 100,000 synthetic tasks
     - Use batched updates for search_vector backfill
     - Consider online schema change tools (pt-online-schema-change)
     - Schedule migration during low-traffic window

2. **Search Vector Storage Overhead**
   - **Risk**: tsvector column significantly increases table size
   - **Mitigation**:
     - Monitor table size before/after migration
     - Use TOAST compression for large tsvector values
     - Consider separate search index table if needed

3. **Foreign Key Constraint Violations**
   - **Risk**: Invalid category_id values cause errors
   - **Mitigation**:
     - Add NOT VALID constraint initially
     - Validate data before enabling constraint
     - Soft delete categories (set deleted_at instead of DELETE)

4. **Backward Compatibility Issues**
   - **Risk**: Phase IV deployments fail after migration
   - **Mitigation**:
     - All new columns nullable or have defaults
     - Test Phase IV API against Phase V schema
     - Document rollback procedure clearly

### Rollback Plan

**If migration fails**:
1. Stop backend services
2. Run `alembic downgrade -1`
3. Verify data integrity
4. Restart backend services
5. Investigate failure root cause

**Data Loss on Rollback**:
- All categories deleted
- All tags deleted
- Task priority/due_date/category/tags lost
- Search vector lost

**Backup Strategy**:
- Take Neon PostgreSQL snapshot before migration
- Export all tables to CSV
- Test restore procedure

---

## Dependencies

**Blocked By**:
- None (this is the foundational feature)

**Blocks**:
- Part A2: Enhanced MCP Tools (needs new fields in models)
- Part A3: Kafka Event Streaming (needs updated models for event payloads)
- Part A4: Search & Filter (needs search_vector and indexes)
- Part A5: Recurring Tasks (needs recurrence_rule field)

**External Dependencies**:
- PostgreSQL 15+ (for GIN indexes and tsvector)
- SQLModel 0.0.14+
- Alembic 1.12+
- python-dateutil 2.8+ (for RRULE validation)

---

## Implementation Checklist

### Phase 1: Model Definitions
- [ ] Create `app/models/category.py`
- [ ] Create `app/models/tag.py`
- [ ] Create `app/models/task_tag.py`
- [ ] Update `app/models/task.py` with new fields
- [ ] Add validation logic for priority, RRULE, colors
- [ ] Update `app/models/__init__.py` exports

### Phase 2: Alembic Migration
- [ ] Generate migration: `alembic revision --autogenerate -m "add advanced task fields"`
- [ ] Review auto-generated migration
- [ ] Add search_vector trigger function
- [ ] Add search_vector backfill logic
- [ ] Add check constraints
- [ ] Test upgrade on empty database
- [ ] Test upgrade on database with 10,000 tasks
- [ ] Test downgrade (rollback)

### Phase 3: Testing
- [ ] Write model unit tests
- [ ] Write migration tests
- [ ] Write integration tests (queries, cascades)
- [ ] Write performance tests
- [ ] Create test data fixtures
- [ ] Run all tests and verify passing

### Phase 4: Documentation
- [ ] Write migration guide
- [ ] Create database schema diagram
- [ ] Document search implementation
- [ ] Add model usage examples
- [ ] Update README

### Phase 5: Deployment
- [ ] Deploy to local Minikube (todo-phasev namespace)
- [ ] Run migration on development database
- [ ] Verify data integrity
- [ ] Test backward compatibility
- [ ] Create backup/restore documentation

---

## Next Steps After Completion

Once this feature is complete:
1. **Part A2**: Implement Enhanced MCP Tools (add_task, list_tasks, update_task with new parameters)
2. **Part A2**: Implement New MCP Tools (search_tasks, category management, tag management)
3. **Part A3**: Integrate Kafka event streaming (publish task events)
4. **Part A4**: Implement search service (full-text search endpoint)
5. **Part A5**: Implement recurring task service (Kafka consumer)

---

## Specification Approval

**Created By**: Claude Sonnet 4.5 (AI Assistant)
**Review Required**: Project Owner
**Approval Status**: PENDING
**Estimated Effort**: 2-3 days
**Priority**: P0 (Critical Path)

Once approved, this specification will be implemented following the Spec-Driven Development workflow defined in Constitution v3.0.0.
