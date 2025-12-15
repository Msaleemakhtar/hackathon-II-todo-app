# Research: Mark Complete Feature

**Feature**: Mark Complete
**Branch**: 005-mark-complete
**Date**: 2025-12-06

## Overview

This document consolidates research findings for implementing the Mark Complete feature, which provides a toggle-based task completion status mechanism. Research focused on understanding existing patterns in the codebase to ensure consistency across validation, error handling, confirmation flows, and timestamp management.

---

## Research Question 1: Input Validation Pattern Consistency

### Question
What is the exact validation sequence pattern used in existing features (Delete, Update) for task ID input and confirmation?

### Findings

**Pattern from `prompt_for_task_id()` (src/ui/prompts.py:148-170)**:

```python
def prompt_for_task_id() -> int:
    user_input = input(PROMPT_TASK_ID)

    # Step 1: Validate numeric input
    try:
        task_id = int(user_input)
    except ValueError:
        raise ValueError(ERROR_INVALID_INPUT)  # ERROR 102

    # Step 2: Validate positive number
    if task_id <= 0:
        raise ValueError(ERROR_INVALID_TASK_ID)  # ERROR 103

    return task_id
```

**Usage Pattern** (from `delete_task_prompt()` and `update_task_prompt()`):

1. Call `prompt_for_task_id()` (raises ValueError for invalid input)
2. Call `get_task_by_id(task_id)` (raises ValueError if task not found - ERROR 101)
3. Wrap both in `try/except ValueError` block
4. On error: Print error message and return to main menu (no confirmation prompt shown)

### Decision
**Adopt identical validation pattern for Mark Complete**:
- Reuse `prompt_for_task_id()` function (no duplication)
- Follow same error handling: numeric check → positive check → existence check
- Return to main menu immediately on validation errors (skip confirmation if task not found)

### Rationale
- Consistency: Users experience identical validation across all features
- Code reuse: No need to duplicate validation logic
- Error sequence: Fail fast on invalid ID, only show confirmation for valid tasks

---

## Research Question 2: Confirmation Prompt Architecture

### Question
How does the Delete feature implement confirmation prompts with Y/N validation?

### Findings

**Pattern from `prompt_for_delete_confirmation()` (src/ui/prompts.py:270-294)**:

```python
def prompt_for_delete_confirmation(task_title: str) -> bool:
    prompt = f"Delete task '{task_title}'? (Y/N): "

    while True:
        response = input(prompt).strip().upper()

        if response == "Y":
            return True
        if response == "N":
            return False

        # Invalid response - re-prompt indefinitely
        print(ERROR_INVALID_CONFIRMATION)  # ERROR 105
```

**Key Design Patterns**:
1. **Indefinite retry loop**: Invalid responses re-prompt (no retry limit)
2. **Whitespace handling**: `strip()` removes leading/trailing spaces
3. **Case insensitivity**: `upper()` normalizes to uppercase before comparison
4. **Task context**: Displays task title in prompt for user confirmation
5. **Boolean return**: True = proceed, False = cancel
6. **Error code**: ERROR 105 for invalid confirmation input

### Decision
**Create parallel confirmation function for Mark Complete**:

```python
def prompt_for_mark_complete_confirmation(task_title: str, current_status: bool) -> bool:
    # Dynamic prompt based on current status
    action = "complete" if not current_status else "incomplete"
    prompt = f"Mark task '{task_title}' as {action}? (Y/N): "

    while True:
        response = input(prompt).strip().upper()
        if response == "Y":
            return True
        if response == "N":
            return False
        print(ERROR_MARK_COMPLETE_CONFIRMATION)  # New ERROR 205
```

**Differences from Delete**:
- **Dynamic prompt text**: Changes "complete" vs "incomplete" based on `task.completed` value
- **New error code**: ERROR 205 (Delete uses ERROR 105; Update doesn't use confirmation)
- **Same validation logic**: Identical whitespace handling, case insensitivity, indefinite retry

### Rationale
- Follows established Delete feature pattern (users already familiar)
- Dynamic prompt provides clear context (user knows what action will occur)
- Indefinite retry prevents premature exit (consistent with spec requirement: "re-prompt indefinitely")

---

## Research Question 3: Error Code Allocation Strategy

### Question
What is the error code numbering convention? Confirm 201-205 range is appropriate.

### Findings

**Current Error Code Allocation** (from src/constants.py):

| Feature | Range | Codes Used | Purpose |
|---------|-------|------------|---------|
| Add Task | 001-003 | 001, 002, 003 | Title required, title too long, description too long |
| View/Delete/Update | 101-105 | 101, 102, 103, 104, 105 | Task not found, invalid input, invalid ID, invalid option, invalid confirmation |

**Pattern Analysis**:
- Add Task: 001-003 (3 codes)
- Shared operations: 101-105 (5 codes covering multiple features)
- Gap: 004-100, 106-200 (available ranges)

**Spec Proposal**: 201-205 for Mark Complete

### Decision
**Use 201-205 range for Mark Complete feature**:
- **ERROR 201**: Task with ID {id} not found (feature-specific variant of 101)
- **ERROR 202**: Invalid input. Please enter a numeric task ID (feature-specific variant of 102)
- **ERROR 203**: Task ID must be a positive number (feature-specific variant of 103)
- **ERROR 204**: (Reserved for future use)
- **ERROR 205**: Invalid input. Please enter Y or N (confirmation validation)

### Rationale
- **Isolation**: Feature-specific error codes prevent cross-feature message confusion
- **Consistency**: Follows established numbering pattern (100s increment per feature group)
- **Traceability**: Error code in message allows quick feature identification
- **Spec alignment**: Matches error codes defined in spec.md (FR-003 to FR-011)

**Note**: Although 101-103 errors exist for shared operations, the spec explicitly defines 201-203 for this feature. This allows:
1. Future decoupling if features diverge
2. Clear error tracking per feature in logs/testing
3. Adherence to specification as written

---

## Research Question 4: Toggle vs. Separate Actions Design Pattern

### Question
Should single "Mark Complete" option intelligently toggle, or provide separate menu options?

### Findings

**Spec Requirement** (from spec.md):
- FR-008: System MUST display different confirmation prompts based on current task status
  - Incomplete tasks: "Mark task '{title}' as complete? (Y/N): "
  - Complete tasks: "Mark task '{title}' as incomplete? (Y/N): "
- FR-015: System MUST toggle the completed status (False↔True)
- Assumption: "Single 'Mark Complete' menu option handles both marking complete and marking incomplete (smart toggle based on current state)"

**UX Analysis**:

| Approach | Pros | Cons |
|----------|------|------|
| **Single Toggle Option** | - Simpler menu (fewer options)<br>- Intuitive: "Mark Complete" = manage status<br>- Fewer menu selections for users<br>- Spec-aligned | - Menu text "Mark Complete" ambiguous for completed tasks |
| **Separate Options** | - Explicit menu labels<br>- No ambiguity | - More menu clutter<br>- Requires checking task status to know which option to select<br>- Not spec-aligned |

### Decision
**Implement single "Mark Complete" menu option with smart toggle behavior**:
- Menu displays: "6. Mark Complete"
- Confirmation prompt dynamically shows "complete" or "incomplete" based on current task status
- Backend toggles `completed` field: False→True or True→False

### Rationale
1. **Spec compliance**: Matches specification's explicit assumption about single menu option
2. **Simplicity**: Reduces cognitive load (users don't need to track status before selecting)
3. **Consistency**: Similar to Update feature (one option, multiple outcomes based on user choices)
4. **Clear feedback**: Dynamic confirmation prompt eliminates ambiguity at decision point

---

## Research Question 5: Timestamp Update Mechanism

### Question
How is `updated_at` currently managed in update_task()? Is Task.generate_timestamp() the standard approach?

### Findings

**Pattern from `update_task()` (src/services/task_service.py:79-109)**:

```python
def update_task(task_id: int, new_title: str | None = None,
                new_description: str | None = None) -> Task:
    task = get_task_by_id(task_id)

    if new_title is not None:
        task.title = new_title
    if new_description is not None:
        task.description = new_description

    # Always update timestamp
    task.updated_at = Task.generate_timestamp()

    return task
```

**Timestamp Generation** (from src/models/task.py:28-34):

```python
@staticmethod
def generate_timestamp() -> str:
    """Generate current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
```

**Key Patterns**:
1. **Centralized generation**: `Task.generate_timestamp()` is the single source of truth
2. **UTC timezone**: All timestamps use `timezone.utc` (no local time)
3. **ISO 8601 format**: `YYYY-MM-DDTHH:MM:SS.ffffffZ` (includes microseconds)
4. **Unconditional update**: `updated_at` is ALWAYS updated, regardless of whether field values changed
5. **Immutable created_at**: `created_at` is NEVER modified after task creation

### Decision
**Adopt identical timestamp pattern for Mark Complete**:

```python
def toggle_task_completion(task_id: int) -> Task:
    task = get_task_by_id(task_id)

    # Toggle completed status
    task.completed = not task.completed

    # Always update timestamp
    task.updated_at = Task.generate_timestamp()

    return task
```

### Rationale
- **Consistency**: Matches update_task() timestamp handling pattern
- **Spec compliance**: FR-016 requires updated_at update; FR-017 forbids created_at changes
- **Audit trail**: Every status change is timestamped, enabling future analytics
- **Simplicity**: Reuse existing static method (no new timestamp logic needed)

---

## Best Practices Research

### Python Standard Library - Input Validation

**Research**: How to handle user input validation in CLI applications?

**Findings**:
- Use `input().strip()` to remove whitespace before validation
- Use `try/except ValueError` for `int()` conversion (standard Python pattern)
- Implement validation loops with `while True` for indefinite retry (matches spec)
- Use `str.upper()` for case-insensitive comparison (simpler than `lower()` or regex)

**Application**: Already applied in existing codebase; reuse patterns.

### Boolean Toggle Pattern

**Research**: What is the idiomatic Python way to toggle boolean values?

**Findings**:
- **Option 1**: `task.completed = not task.completed` (idiomatic, clear intent)
- **Option 2**: `task.completed = False if task.completed else True` (verbose, less Pythonic)
- **Option 3**: `task.completed ^= True` (XOR operator, too clever/obscure)

**Decision**: Use `not task.completed` (Option 1) - most readable and Pythonic.

### Error Message Formatting

**Research**: How to format error messages with dynamic values (task ID)?

**Findings** (from src/constants.py):
- Use Python f-string placeholders: `"ERROR 101: Task with ID {task_id} not found."`
- Format at usage site: `ERROR_TASK_NOT_FOUND.format(task_id=task_id)`

**Application**:
```python
ERROR_MARK_COMPLETE_NOT_FOUND = "ERROR 201: Task with ID {task_id} not found."
# Usage:
raise ValueError(ERROR_MARK_COMPLETE_NOT_FOUND.format(task_id=task_id))
```

---

## Integration Points

### Files to Modify

1. **src/constants.py**
   - Add 5 new error codes (201-205)
   - Add 3 new prompts (task ID, confirmation, success messages)
   - Add 1 cancellation message

2. **src/services/task_service.py**
   - Add `toggle_task_completion(task_id: int) -> Task` function
   - Function signature: Takes task_id, returns modified Task instance
   - Implementation: Reuses `get_task_by_id()` for validation and retrieval

3. **src/ui/prompts.py**
   - Add `mark_complete_prompt()` function (orchestration)
   - Add `prompt_for_mark_complete_confirmation(task_title, current_status)` function
   - Pattern: Mirror `delete_task_prompt()` structure

4. **src/main.py**
   - Add `handle_mark_complete()` function
   - Modify menu option "6. Mark Complete" to call handler (currently placeholder)
   - Pattern: Same structure as `handle_add_task()`, `handle_view_tasks()`

### Testing Strategy

**Unit Tests** (tests/unit/test_task_service.py):
- `test_toggle_incomplete_to_complete()` - False → True
- `test_toggle_complete_to_incomplete()` - True → False
- `test_toggle_updates_timestamp()` - Verify updated_at changes
- `test_toggle_preserves_created_at()` - Verify created_at unchanged
- `test_toggle_preserves_other_fields()` - Verify id/title/description unchanged
- `test_toggle_invalid_task_id()` - Verify ERROR 201
- `test_toggle_zero_task_id()` - Verify ERROR 203

**Integration Tests** (tests/integration/test_mark_complete_flow.py):
- `test_mark_complete_full_flow_confirm()` - End-to-end with Y confirmation
- `test_mark_complete_full_flow_cancel()` - End-to-end with N cancellation
- `test_mark_complete_invalid_id_handling()` - Error handling flow
- `test_mark_complete_invalid_confirmation()` - Confirmation retry flow

---

## Technical Decisions Summary

| Decision | Rationale | Tradeoffs Considered |
|----------|-----------|----------------------|
| **Reuse `prompt_for_task_id()`** | Avoid code duplication, ensure consistency | None - pure win |
| **Smart toggle (single menu option)** | Spec-aligned, simpler UX, less menu clutter | Menu text ambiguity (mitigated by dynamic confirmation) |
| **Error codes 201-205** | Feature isolation, spec compliance, traceability | Could reuse 101-105 (rejected for clarity) |
| **Dynamic confirmation prompts** | Clear user feedback, prevents mistakes | Slightly more complex logic (worth the UX improvement) |
| **`not task.completed` toggle** | Pythonic, readable, idiomatic | None - standard pattern |
| **`Task.generate_timestamp()`** | Consistency with existing code, centralized logic | None - already established pattern |
| **Indefinite retry on invalid input** | Spec requirement, matches Delete pattern | Could frustrate users (but spec mandates) |

---

## Alternatives Considered

### Alternative 1: Separate Menu Options ("Mark Complete" + "Mark Incomplete")

**Description**: Provide two distinct menu options instead of smart toggle.

**Rejected Because**:
- Violates spec assumption: "Single 'Mark Complete' menu option handles both"
- Increases menu complexity (7 options instead of 6)
- Requires users to know task status before selecting option
- Delete feature already demonstrates toggle pattern success (delete = toggle existence)

### Alternative 2: Reuse Error Codes 101-105

**Description**: Use existing shared error codes instead of feature-specific 201-205.

**Rejected Because**:
- Spec explicitly defines 201-205 for this feature (FR-004, FR-005, FR-007, FR-011)
- Feature-specific codes improve error traceability in testing and debugging
- Maintains isolation between feature domains
- Small cost (5 constants) for significant clarity benefit

### Alternative 3: Skip Confirmation Prompt

**Description**: Toggle status immediately without Y/N confirmation.

**Rejected Because**:
- Violates spec requirement FR-009: "System MUST wait for user confirmation"
- Inconsistent with Delete feature (which requires confirmation)
- Increases risk of accidental status changes
- User Story 3 explicitly requires cancellation capability

---

## Dependencies

### External Dependencies
- **None** - Python standard library only (per constitution)

### Internal Dependencies
- `src/models/task.py` - Existing Task dataclass (no changes needed)
- `src/services/task_service.py` - Existing `get_task_by_id()` function (reused)
- `src/ui/prompts.py` - Existing `prompt_for_task_id()` function (reused)
- `src/constants.py` - Existing validation constants (reused)

### Test Dependencies
- `pytest` - Already configured in pyproject.toml
- `unittest.mock` - For input mocking in integration tests (Python standard library)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Ambiguous menu text** | Medium | Low | Dynamic confirmation prompt clarifies action |
| **Error code confusion** | Low | Low | Feature-specific codes (201-205) prevent confusion |
| **Timestamp race conditions** | None | None | Single-threaded CLI application |
| **Data loss on toggle** | None | None | In-memory storage; toggle is atomic operation |

---

## Conclusion

All research questions have been resolved with clear decisions based on:
1. **Existing codebase patterns** - Ensures consistency
2. **Specification requirements** - Maintains compliance
3. **Python best practices** - Uses idiomatic approaches
4. **User experience** - Prioritizes clarity and error prevention

**Status**: ✅ Research complete - Ready for Phase 1 (Design & Contracts)

**Next Steps**:
1. Generate `data-model.md` (entity and state transition design)
2. Generate `contracts/` (if applicable - likely N/A for internal CLI feature)
3. Generate `quickstart.md` (implementation guide for AI code generation)
4. Update agent context (run `.specify/scripts/bash/update-agent-context.sh`)
