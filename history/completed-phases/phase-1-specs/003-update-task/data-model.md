# Data Model: Update Task Feature

**Feature**: 003-update-task
**Date**: 2025-12-06
**Purpose**: Document data entities, relationships, and state transitions for the Update Task feature

---

## Overview

The Update Task feature modifies existing Task entities by allowing selective updates to the `title` and/or `description` fields while preserving immutability of `id`, `completed`, and `created_at` fields. The `updated_at` timestamp is refreshed on every update operation regardless of which fields are modified.

---

## Entities

### Task (Existing Entity - Partial Update)

**Source**: `src/models/task.py`

**Data Structure**: Python `@dataclass`

**Fields**:

| Field | Type | Mutability | Validation | Update Behavior |
|-------|------|------------|------------|-----------------|
| `id` | `int` | **Immutable** | N/A (never modified) | ❌ Never updated |
| `title` | `str` | **Mutable** | 1-200 chars, non-empty (after strip) | ✅ Updated when option 1 or 3 selected |
| `description` | `str` | **Mutable** | 0-1000 chars (after strip), allows empty | ✅ Updated when option 2 or 3 selected |
| `completed` | `bool` | **Immutable** (for this feature) | N/A (not modified by update) | ❌ Never updated (separate Mark Complete feature) |
| `created_at` | `str` | **Immutable** | N/A (set once at creation) | ❌ Never updated |
| `updated_at` | `str` | **Auto-updated** | ISO 8601 timestamp | ✅ Always updated to current UTC time |

**Immutability Guarantees**:
- `id`: Unique identifier must never change to maintain referential integrity
- `completed`: Completion status managed by separate Mark Complete feature (feature #5)
- `created_at`: Historical record of task creation time must be preserved

**Mutability Rules**:
- `title`: Can be updated via option 1 (Title Only) or option 3 (Both)
- `description`: Can be updated via option 2 (Description Only) or option 3 (Both)
- `updated_at`: Automatically set to current timestamp on every update operation

---

## Validation Rules

### Title Validation (Reused from 001-add-task)

**Function**: `validate_title(title: str)` from `src/ui/prompts.py`

| Rule | Check | Error Code | Error Message |
|------|-------|------------|---------------|
| Non-empty | `len(title.strip()) > 0` | ERROR 001 | "ERROR 001: Title is required and must be 1-200 characters." |
| Max length | `len(title.strip()) <= 200` | ERROR 002 | "ERROR 002: Title is required and must be 1-200 characters." |

**Pre-processing**: Strip leading/trailing whitespace before validation

### Description Validation (Reused from 001-add-task)

**Function**: `validate_description(description: str)` from `src/ui/prompts.py`

| Rule | Check | Error Code | Error Message |
|------|-------|------------|---------------|
| Max length | `len(description.strip()) <= 1000` | ERROR 003 | "ERROR 003: Description cannot exceed 1000 characters." |
| Allow empty | `len(description.strip()) == 0` | ✅ Valid | Empty string is acceptable |

**Pre-processing**: Strip leading/trailing whitespace before validation

### Task ID Validation (Reused from 002-view-task)

**Function**: `get_task_by_id(task_id: int)` from `src/services/task_service.py`

| Rule | Check | Error Code | Error Message |
|------|-------|------------|---------------|
| Numeric | `int(user_input)` succeeds | ERROR 102 | "ERROR 102: Invalid input. Please enter a numeric task ID." |
| Positive | `task_id > 0` | ERROR 103 | "ERROR 103: Task ID must be a positive number." |
| Exists | Task found in `_task_storage` | ERROR 101 | "ERROR 101: Task with ID {task_id} not found." |

### Field Selection Validation (New for Update Task)

**Function**: `prompt_for_field_choice()` from `src/ui/prompts.py` (new)

| Rule | Check | Error Code | Error Message |
|------|-------|------------|---------------|
| Numeric | `int(user_input)` succeeds | ERROR 104 | "ERROR 104: Invalid option. Please select 1, 2, or 3." |
| Valid range | `1 <= choice <= 3` | ERROR 104 | "ERROR 104: Invalid option. Please select 1, 2, or 3." |

---

## State Transitions

### Update Operation State Machine

```text
┌─────────────────┐
│  Initial State  │
│  (Task exists)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate ID    │  ← ERROR 101/102/103 if invalid
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Current │
│  Title + Desc   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Field Selection │  ← ERROR 104 if invalid
│    Menu (1-3)   │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
┌───────┐ ┌────────┐ ┌──────────┐
│ Opt 1 │ │ Opt 2  │ │  Opt 3   │
│ Title │ │  Desc  │ │  Both    │
│ Only  │ │  Only  │ │          │
└───┬───┘ └───┬────┘ └────┬─────┘
    │         │            │
    ▼         ▼            ▼
┌───────┐ ┌────────┐ ┌──────────┐
│ Get   │ │  Get   │ │ Get Both │
│ New   │ │  New   │ │   New    │
│ Title │ │  Desc  │ │  Values  │
└───┬───┘ └───┬────┘ └────┬─────┘
    │         │            │
    │  ERROR 001/002 ←────┤
    │  ERROR 003 ←─────────┤
    │         │            │
    └────┬────┴────────────┘
         │
         ▼
┌─────────────────┐
│  Update Fields  │
│ + updated_at    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Success Msg   │
│  Return to Menu │
└─────────────────┘
```

### Field Modification Matrix

| Option Selected | Title Field | Description Field | updated_at Field |
|-----------------|-------------|-------------------|------------------|
| 1 (Title Only) | ✅ Updated | ⛔ Preserved | ✅ Updated |
| 2 (Description Only) | ⛔ Preserved | ✅ Updated | ✅ Updated |
| 3 (Both) | ✅ Updated | ✅ Updated | ✅ Updated |

---

## Data Flow

### Update Task Operation Flow

```text
User Input → UI Layer → Service Layer → Data Storage → Response
    │           │            │               │            │
    ├─ task_id ─┼─ validate ─┼─ get_task ───┤            │
    │           │            │               │            │
    ├─ choice ──┼─ validate ─┤               │            │
    │           │            │               │            │
    ├─ new_vals ┼─ validate ─┤               │            │
    │           │            │               │            │
    │           │            ├─ modify ──────┤            │
    │           │            ├─ timestamp ───┤            │
    │           │            │               │            │
    │           ├─ success ──┼───────────────┼────────────┤
    │           │  message   │               │            │
    └───────────┴────────────┴───────────────┴────────────┘
```

**Layers**:
1. **UI Layer** (`src/ui/prompts.py`):
   - Collect task ID
   - Display current values
   - Present field selection menu
   - Collect new value(s) based on choice
   - Validate all inputs
   - Display success/error messages

2. **Service Layer** (`src/services/task_service.py`):
   - Locate task by ID (reuse `get_task_by_id()`)
   - Modify task fields in-place
   - Generate and set new `updated_at` timestamp
   - Return updated task

3. **Data Storage**:
   - In-memory list: `_task_storage: list[Task]`
   - Modification: Direct attribute assignment on Task instance

---

## Entity Relationships

### Storage Model

```text
_task_storage (module-level list)
    │
    ├─ Task instance (id=1, title="...", ...)  ← May be updated
    ├─ Task instance (id=2, title="...", ...)  ← May be updated
    ├─ Task instance (id=3, title="...", ...)  ← May be updated
    └─ ...

Update Operation:
    1. Locate task by ID (linear search)
    2. Modify task.title and/or task.description in-place
    3. Set task.updated_at to current UTC time
    4. Return modified task (same object reference)
```

**Key Characteristics**:
- **No new entities**: Operates on existing Task instances
- **In-place modification**: Task object remains at same list position
- **Referential integrity**: Task ID never changes
- **Temporal tracking**: `updated_at` provides audit trail

---

## Timestamp Management

### ISO 8601 Format

**Function**: `Task.generate_timestamp()` from `src/models/task.py`

**Format**: `YYYY-MM-DDTHH:MM:SS.ffffffZ`

**Example**: `2025-12-06T10:30:45.123456Z`

**Precision**: Microseconds

**Timezone**: UTC (denoted by 'Z' suffix)

### Update Behavior

| Field | On Create | On Update (This Feature) |
|-------|-----------|--------------------------|
| `created_at` | `Task.generate_timestamp()` | ⛔ Never modified |
| `updated_at` | `Task.generate_timestamp()` (same as created_at) | ✅ `Task.generate_timestamp()` (current time) |

**Invariant**: After any update operation, `updated_at >= created_at` (strictly greater if update occurs after creation)

---

## Performance Characteristics

### Complexity Analysis

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Locate task by ID | O(n) | O(1) | Linear search through `_task_storage` |
| Validate title | O(1) | O(1) | String length check (constant time) |
| Validate description | O(1) | O(1) | String length check (constant time) |
| Update fields | O(1) | O(1) | Direct attribute assignment |
| Generate timestamp | O(1) | O(1) | `datetime.now()` call |
| **Total Update Operation** | **O(n)** | **O(1)** | Dominated by task lookup |

**Expected Performance**:
- In-memory operations: <1ms for typical task counts (<1000 tasks)
- User interaction time: ~5-30 seconds (per SC-001)
- Bottleneck: User input, not computation

---

## Data Integrity Constraints

### Enforced at Runtime

1. **Uniqueness**: Task ID uniqueness enforced by `generate_next_id()` (not violated by update)
2. **Non-null**: All Task fields are required (no Optional types)
3. **Length limits**: Title (1-200), Description (0-1000) enforced by validation
4. **Timestamp format**: ISO 8601 format enforced by `Task.generate_timestamp()`

### Not Enforced (Assumed Valid)

1. **Concurrent modification**: Not applicable (single-user CLI, ephemeral state)
2. **Transaction rollback**: Not applicable (no persistence)
3. **Foreign keys**: Not applicable (no entity relationships)

---

## Summary

**Entities Modified**: 1 (Task)
**New Entities**: 0
**Fields Updated**: 2-3 depending on user choice (title, description, updated_at)
**Immutable Fields**: 3 (id, completed, created_at)
**Validation Functions Reused**: 3 (title, description, task_id)
**New Validation**: 1 (field selection)
**State Transitions**: 1 main flow with 3 branches (field selection options)
**Performance**: O(n) lookup, O(1) update, overall dominated by user interaction time
