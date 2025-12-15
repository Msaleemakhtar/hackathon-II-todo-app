# Research & Technical Decisions: Update Task

**Feature**: 003-update-task
**Date**: 2025-12-06
**Purpose**: Document research findings and technical decisions for implementing the Update Task feature

---

## Research Task 1: Existing TaskService Implementation

### Findings

**File**: `src/services/task_service.py`

**Key Patterns Identified**:
1. **In-memory storage**: `_task_storage: list[Task] = []` - module-level list
2. **ID generation**: `generate_next_id()` - returns max(IDs) + 1, or 1 if empty
3. **Task lookup**: `get_task_by_id(task_id)` - linear search through `_task_storage`, raises ValueError if not found
4. **Task retrieval**: `get_all_tasks()` - returns `_task_storage.copy()` (defensive copy)
5. **Task creation**: `create_task(title, description)` - creates Task, appends to storage, returns new task

**Update Strategy Decision**:
- **Decision**: Use `get_task_by_id()` to locate task, modify in-place, return updated task
- **Rationale**:
  - Reuses existing validation (task_id positive check, existence check)
  - In-place modification preserves task object identity in list
  - No need to remove/re-add or rebuild list
- **Implementation**:
  ```python
  def update_task(task_id: int, new_title: str | None, new_description: str | None) -> Task:
      task = get_task_by_id(task_id)  # Reuse existing lookup + validation
      if new_title is not None:
          task.title = new_title
      if new_description is not None:
          task.description = new_description
      task.updated_at = Task.generate_timestamp()
      return task
  ```

**Alternatives Considered**:
- Create new Task and replace in list → Rejected: unnecessary complexity, breaks object identity
- Remove old task and append new one → Rejected: changes list order, complicates ID management

---

## Research Task 2: Validation Patterns from Add-Task

### Findings

**File**: `src/ui/prompts.py`

**Validation Functions** (lines 20-49):
1. `validate_title(title)` → `(is_valid: bool, error_message: str | None)`
   - Strips whitespace
   - Checks length: 0 → ERROR_TITLE_REQUIRED, >200 → ERROR_TITLE_TOO_LONG
2. `validate_description(description)` → `(is_valid: bool, error_message: str | None)`
   - Strips whitespace
   - Checks length: >1000 → ERROR_DESCRIPTION_TOO_LONG

**Input Collection with Retry Loop** (lines 52-77):
1. `get_task_title()` - loop until valid, print error on failure
2. `get_task_description()` - loop until valid, print error on failure

**Reuse Strategy Decision**:
- **Decision**: Reuse `validate_title()` and `validate_description()` functions directly
- **Rationale**:
  - Identical validation rules for update as for create (per spec)
  - DRY principle - single source of truth for validation
  - Error codes 001-003 already defined and tested
- **New UI Functions Needed**:
  - `get_new_task_title()` - similar to `get_task_title()` but different prompt
  - `get_new_task_description()` - similar to `get_task_description()` but different prompt

**Error Codes to Reuse** (from `src/constants.py`):
- ERROR_TITLE_REQUIRED (001)
- ERROR_TITLE_TOO_LONG (002)
- ERROR_DESCRIPTION_TOO_LONG (003)

---

## Research Task 3: ID Validation Patterns from View-Task

### Findings

**File**: `src/ui/prompts.py` (lines 139-161)

**ID Validation Pattern**:
1. `prompt_for_task_id()` function:
   - Prompts with PROMPT_TASK_ID constant
   - Tries `int()` conversion → ValueError if non-numeric (ERROR 102)
   - Checks `task_id <= 0` → ValueError (ERROR 103)
   - Returns valid positive integer

**File**: `src/services/task_service.py` (lines 53-76)

**Task Existence Validation**:
1. `get_task_by_id(task_id)` function:
   - Validates task_id > 0 (ERROR 103)
   - Searches `_task_storage` for matching ID
   - Raises ValueError if not found (ERROR 101 with formatted message)

**Reuse Strategy Decision**:
- **Decision**: Reuse `prompt_for_task_id()` for collecting task ID, reuse `get_task_by_id()` for validation
- **Rationale**:
  - Identical ID validation rules (positive integer, must exist)
  - Error codes 101-103 already implemented
  - Consistent error messages across features

**Error Codes to Reuse**:
- ERROR_TASK_NOT_FOUND (101) - formatted with task_id
- ERROR_INVALID_INPUT (102) - non-numeric input
- ERROR_INVALID_TASK_ID (103) - zero or negative

---

## Research Task 4: Python In-Place List Modification Best Practices

### Research Findings

**Python List Modification Strategies**:

1. **Direct attribute modification** (CHOSEN):
   ```python
   task = get_task_by_id(task_id)
   task.title = new_title  # Modifies dataclass instance in-place
   ```
   - ✅ Simplest, most readable
   - ✅ Preserves object identity
   - ✅ No index management needed
   - ✅ Works with dataclass frozen=False (default)

2. **Replace by index**:
   ```python
   index = next(i for i, t in enumerate(_task_storage) if t.id == task_id)
   _task_storage[index] = new_task
   ```
   - ❌ More complex
   - ❌ Requires creating new Task instance
   - ❌ Breaks object identity

3. **Remove and re-append**:
   ```python
   _task_storage.remove(old_task)
   _task_storage.append(new_task)
   ```
   - ❌ Changes list order
   - ❌ More operations
   - ❌ Risk of data loss if append fails

**Decision**: Use direct attribute modification (Strategy 1)

**Rationale**:
- Python dataclass instances are mutable by default
- Modifying attributes directly is idiomatic Python
- Preserves list order and object references
- Minimal code, maximum clarity

**Verification**:
```python
# Task dataclass is mutable (frozen=False by default in dataclasses)
@dataclass
class Task:  # No frozen=True → mutable
    id: int
    title: str
    # ...
```

---

## Research Task 5: CLI Menu-Driven Selection Patterns

### Findings

**File**: `src/main.py` (assumed from constitution requirements)

**Main Menu Pattern** (from constitution):
- Numbered options (1-6): 5 features + Exit
- User enters number
- Validation: numeric check, range check
- Loop until valid choice

**Field Selection Menu Decision**:
- **Decision**: Follow same numbered menu pattern
- **Implementation**:
  ```python
  def display_field_selection_menu() -> None:
      print("\nSelect fields to update:")
      print("1. Update Title Only")
      print("2. Update Description Only")
      print("3. Update Both Title and Description")

  def prompt_for_field_choice() -> int:
      while True:
          try:
              choice = int(input("Select update option (1-3): "))
              if 1 <= choice <= 3:
                  return choice
              print(ERROR_INVALID_OPTION)  # New error code 104
          except ValueError:
              print(ERROR_INVALID_OPTION)
  ```

**New Constant Needed** (add to `src/constants.py`):
```python
ERROR_INVALID_OPTION = "ERROR 104: Invalid option. Please select 1, 2, or 3."
```

**Alternatives Considered**:
- Letter-based menu (A/B/C) → Rejected: inconsistent with numeric main menu
- Prompt for each field individually → Rejected: violates spec requirement for menu selection

---

## Summary of Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Task Location** | Use `get_task_by_id()` | Reuses validation, consistent error handling |
| **Modification Strategy** | Direct attribute modification | Simplest, preserves identity, idiomatic Python |
| **Title Validation** | Reuse `validate_title()` | DRY, consistent error codes (001-002) |
| **Description Validation** | Reuse `validate_description()` | DRY, consistent error code (003) |
| **ID Validation** | Reuse `prompt_for_task_id()` + `get_task_by_id()` | Consistent error codes (101-103) |
| **Field Selection UI** | Numbered menu (1-3) | Matches main menu pattern, clear UX |
| **New Error Code** | ERROR 104 for invalid field selection | Continues sequential numbering from 103 |
| **Timestamp Update** | Call `Task.generate_timestamp()` | Reuses existing utility, consistent format |

---

## Dependencies & Integration Points

**No New Dependencies**: All functionality uses Python standard library

**Code Reuse**:
- `src/services/task_service.py`: `get_task_by_id()`, `Task.generate_timestamp()`
- `src/ui/prompts.py`: `validate_title()`, `validate_description()`, `prompt_for_task_id()`
- `src/models/task.py`: Task dataclass (no changes needed)
- `src/constants.py`: Existing error codes 001-003, 101-103

**New Code Needed**:
- `src/services/task_service.py`: `update_task(task_id, new_title, new_description)` method
- `src/ui/prompts.py`:
  - `display_field_selection_menu()`
  - `prompt_for_field_choice()`
  - `get_new_task_title(current_title)`
  - `get_new_task_description(current_description)`
  - `update_task_prompt()` (orchestrator)
- `src/constants.py`: ERROR 104, new prompts for update UI
- `src/main.py`: Menu option 3 handler calling `update_task_prompt()`

---

## Risks & Mitigations

**Risk**: None identified

**Confidence**: High - straightforward extension of proven patterns from features 001 and 002

---

**Research Complete**: All NEEDS CLARIFICATION items resolved. Ready for Phase 1 (Design & Contracts).
