# Research: View Task Feature

**Feature**: 002-view-task
**Date**: 2025-12-06
**Status**: Complete

## Overview

This document consolidates research findings and technical decisions for implementing the View Task feature. Since the technical stack is well-established by the constitution and the feature builds on existing patterns from the Add Task feature (001-add-task), this research focuses on design patterns and best practices for read-only display operations.

---

## Key Decisions

### Decision 1: Display Architecture Pattern

**Decision**: Extend existing service layer pattern with read-only view methods.

**Rationale**:
- Consistency with Add Task feature architecture (TaskService pattern)
- Separation of concerns: TaskService handles data access, ui/prompts.py handles display formatting
- Testability: Service methods can be unit tested independently of UI formatting
- Maintainability: Clear boundaries between business logic and presentation

**Alternatives Considered**:
- **Direct access from UI**: Rejected because it violates separation of concerns and makes testing harder
- **New ViewService class**: Rejected because it adds unnecessary abstraction for simple read operations
- **Existing TaskService extension**: Selected for consistency and simplicity

**Implementation Notes**:
- Add `get_all_tasks()` method to TaskService for list view
- Add `get_task_by_id(task_id: int)` method to TaskService for detail view
- Both methods return Task objects or raise appropriate exceptions

---

### Decision 2: Error Handling Strategy

**Decision**: Use exception-based error handling with specific error codes and messages.

**Rationale**:
- Matches the pattern established in Add Task feature
- Provides clear error messages per spec requirements (ERROR 101, 102, 103)
- Allows UI layer to catch and display errors consistently
- Supports comprehensive error testing

**Error Classification**:
- **ERROR 101**: Task not found (ValueError with message "Task with ID {id} not found.")
- **ERROR 102**: Invalid input (ValueError with message "Invalid input. Please enter a numeric task ID.")
- **ERROR 103**: Invalid range (ValueError with message "Task ID must be a positive number.")

**Implementation Pattern**:
```python
def get_task_by_id(self, task_id: int) -> Task:
    """Retrieve a task by ID."""
    if task_id <= 0:
        raise ValueError("ERROR 103: Task ID must be a positive number.")

    for task in self.tasks:
        if task.id == task_id:
            return task

    raise ValueError(f"ERROR 101: Task with ID {task_id} not found.")
```

---

### Decision 3: Display Formatting Approach

**Decision**: Implement display functions in ui/prompts.py that format Task objects for console output.

**Rationale**:
- Consistent with existing UI patterns in prompts.py
- Keeps formatting logic separate from business logic
- Allows easy modification of display format without changing service layer
- Supports testing of formatting independently

**Display Functions to Add**:
1. `display_task_list(tasks: list[Task])` - Formats list view with completion indicators
2. `display_task_details(task: Task)` - Formats detailed single task view
3. `display_empty_list_message()` - Shows "No tasks found." message
4. `display_pagination_prompt()` - Shows "Press Enter to continue..." every 20 tasks

---

### Decision 4: Input Validation Strategy

**Decision**: Validate numeric input using try-except with int() conversion, then validate range.

**Rationale**:
- Python-native approach (Pythonic)
- Clear exception handling for non-numeric input
- Consistent with standard Python patterns
- Easy to test with parametrized tests

**Validation Flow**:
1. Prompt user for input
2. Try to convert to int → ValueError if non-numeric (ERROR 102)
3. Check if int > 0 → ValueError if not (ERROR 103)
4. Pass to service layer for existence check (ERROR 101)

---

### Decision 5: Pagination Implementation

**Decision**: Implement simple counter-based pagination with manual Enter prompt every 20 tasks.

**Rationale**:
- Meets spec requirement (FR-006a)
- Simple implementation without external dependencies
- No need for terminal control libraries (curses, rich, etc.)
- Maintains compatibility with automated testing

**Implementation**:
```python
def display_task_list(tasks: list[Task]):
    for i, task in enumerate(tasks, start=1):
        print(f"{task.id}. {'[X]' if task.completed else '[ ]'} {task.title}")
        if i % 20 == 0 and i < len(tasks):
            input("Press Enter to continue...")
    print(f"\nTotal: {len(tasks)} tasks")
```

---

### Decision 6: Empty Description Placeholder

**Decision**: Display "(No description)" when description field is empty or whitespace-only.

**Rationale**:
- Meets spec requirement (FR-016)
- Provides clear visual feedback that field is intentionally empty
- Prevents confusion from blank lines
- User-friendly alternative to empty string display

---

### Decision 7: Timestamp Display Format

**Decision**: Display timestamps in ISO 8601 format as stored (no conversion or formatting).

**Rationale**:
- Matches spec assumption: "Timestamps are displayed in their stored ISO 8601 format"
- No additional parsing or formatting logic required
- Consistent with data model
- Precise and unambiguous
- Out-of-scope items explicitly exclude human-readable formats like "2 hours ago"

---

## Technology Stack Summary

| Component | Technology | Notes |
|-----------|-----------|-------|
| Language | Python 3.13 | Per constitution requirement |
| Testing | pytest | Only external dependency allowed |
| Storage | In-memory list | Existing tasks list in TaskService |
| UI | Standard I/O | print() and input() only |
| Formatting | String methods | No external formatting libraries |
| Validation | Native Python | int(), try-except, conditionals |

---

## Best Practices Applied

### Console Display
- Use clear visual indicators: `[ ]` for incomplete, `[X]` for complete
- Add labeled fields in detail view: "ID: 5", "Title: Buy groceries"
- Preserve special characters (newlines, emojis, Unicode) as-is
- Let terminal handle text wrapping naturally

### Input Validation
- Validate early and provide specific error messages
- Allow retries on invalid input for detail view
- Return to main menu on task not found errors
- Use try-except for type conversion errors

### Code Organization
- Service layer: Data access and business logic
- UI layer: Display formatting and user interaction
- Models: Data structures (existing Task dataclass)
- Constants: Error messages and magic numbers

### Testing Strategy
- Unit tests: Service methods (get_all_tasks, get_task_by_id)
- Unit tests: Validation logic (numeric, positive, exists)
- Unit tests: Display formatting functions
- Integration tests: End-to-end user scenarios from spec

---

## Dependencies on Existing Code

### models/task.py
- **Dependency**: Task dataclass with fields: id, title, description, completed, created_at, updated_at
- **Usage**: Read-only access to all fields for display
- **Assumption**: Task structure remains unchanged from Add Task feature

### services/task_service.py
- **Dependency**: TaskService class with `self.tasks` list
- **Extension**: Add `get_all_tasks()` and `get_task_by_id()` methods
- **Assumption**: Existing task list is accessible and mutable (for future features)

### ui/prompts.py
- **Dependency**: Existing prompt patterns and conventions
- **Extension**: Add display_task_list() and display_task_details() functions
- **Assumption**: Console-based I/O using print() and input()

### main.py
- **Dependency**: Main menu loop and option handling
- **Extension**: Add options 2 and 3 for "View Tasks" and "View Task Details"
- **Assumption**: Menu system supports adding new numbered options

---

## Implementation Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large task lists cause terminal overflow | Medium | Pagination every 20 tasks (FR-006a) |
| Long titles/descriptions break formatting | Low | Let terminal handle wrapping naturally (spec assumption) |
| Unicode/emoji display issues | Low | Display as-is (spec requirement); terminal compatibility assumed |
| Task ID conflicts with future features | Low | Use existing ID field from Task dataclass; no new ID logic |
| Input validation inconsistencies | Medium | Reuse validation patterns from Add Task; comprehensive test coverage |

---

## Compliance Verification

All decisions align with constitutional principles:
- ✅ **Spec-Driven**: This research derives from spec.md requirements
- ✅ **CLI-Only**: Console display using standard I/O
- ✅ **In-Memory**: Read-only access to existing task list
- ✅ **Python 3.13**: Standard library only (no new dependencies)
- ✅ **Clean Code**: Clear separation of concerns, type hints required
- ✅ **Testing**: Unit and integration tests planned
- ✅ **Core Features**: View Tasks is feature #2 of 5

---

**Research Status**: ✅ Complete - Ready for Phase 1 (Design & Contracts)
