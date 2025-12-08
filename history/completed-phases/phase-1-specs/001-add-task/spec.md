# Feature Specification: Add Task

**Feature Branch**: `001-add-task`
**Created**: 2025-12-04
**Status**: Draft
**Input**: User description: "Enable a user to add a new task with a title and an optional description to the in-memory task list via a command-line interface."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task with Title and Description (Priority: P1)

A user wants to capture a new task with both a title and detailed description so they can remember what needs to be done and why.

**Why this priority**: This is the core value proposition of the feature - enabling users to create tasks with full context. Without this, the feature cannot deliver any value.

**Independent Test**: Can be fully tested by navigating to the Add Task menu option, entering a valid title and description, and verifying the task appears in the task list with correct data.

**Acceptance Scenarios**:

1. **Given** the user is at the main menu, **When** they select "Add Task", enter title "Complete project report" and description "Include Q4 metrics and team feedback", **Then** the system displays "Task added successfully." and returns to the main menu with the new task stored in memory.

2. **Given** the user is at the main menu, **When** they select "Add Task", enter title "Buy groceries" and description "Milk, eggs, bread, cheese", **Then** the task is created with ID 1 (if first task), completed status False, and both created_at and updated_at timestamps set to the current UTC time in ISO 8601 format.

---

### User Story 2 - Add Task with Title Only (Priority: P1)

A user wants to quickly capture a task with just a title when additional description is not needed.

**Why this priority**: Equally critical as Story 1 - many tasks are self-explanatory from the title alone. Users need the flexibility to skip the description to maintain a fast workflow.

**Independent Test**: Can be fully tested by navigating to Add Task, entering only a title and pressing Enter at the description prompt, verifying the task is created with an empty description.

**Acceptance Scenarios**:

1. **Given** the user is at the Add Task screen, **When** they enter title "Call dentist" and press Enter at the description prompt without entering text, **Then** the task is created with an empty string as the description.

2. **Given** the user has already added 3 tasks, **When** they add a new task with title "Review code" and no description, **Then** the new task receives ID 4 (one greater than the highest existing ID).

---

### Edge Cases

- **Whitespace handling**: What happens when a user enters a title or description with only spaces or tabs?
- **Maximum length boundaries**: How does the system behave when input is exactly at the 200-character limit for title or 1000-character limit for description?
- **Empty task list ID generation**: What ID is assigned to the very first task when the list is empty?
- **Error recovery**: What happens if a user enters invalid input multiple times - can they eventually succeed or return to the main menu?
- **Timestamp precision**: Are timestamps consistent when created_at and updated_at are set simultaneously during task creation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a prompt "Enter Task Title: " to collect the task title from the user.
- **FR-002**: System MUST strip leading and trailing whitespace from the title input before validation.
- **FR-003**: System MUST validate that the stripped title is between 1 and 200 characters in length (inclusive).
- **FR-004**: System MUST reject empty or whitespace-only titles with error message "ERROR 001: Title is required and must be 1-200 characters." and re-prompt the user.
- **FR-005**: System MUST reject titles exceeding 200 characters with error message "ERROR 002: Title is required and must be 1-200 characters." and re-prompt the title.
- **FR-006**: System MUST display a prompt "Enter Optional Task Description (press Enter to skip): " to collect an optional description.
- **FR-007**: System MUST strip leading and trailing whitespace from the description input before validation.
- **FR-008**: System MUST allow empty descriptions (when user presses Enter without text).
- **FR-009**: System MUST reject descriptions exceeding 1000 characters with error message "ERROR 003: Description cannot exceed 1000 characters." and re-prompt the user for the description only.
- **FR-010**: System MUST generate a unique integer ID for each new task, starting at 1 for the first task and incrementing by 1 for each subsequent task.
- **FR-011**: System MUST set the completed field to False for all newly created tasks.
- **FR-012**: System MUST set both created_at and updated_at fields to the current UTC timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffffZ) at the moment of task creation.
- **FR-013**: System MUST store the new task in an in-memory Python data structure (no file I/O or database operations).
- **FR-014**: System MUST display the confirmation message "Task added successfully." after successfully creating a task.
- **FR-015**: System MUST return the user to the main menu after task creation or error handling.
- **FR-016**: System MUST NOT crash under any input validation error scenario and MUST allow users to retry input.

### Key Entities

- **Task**: Represents a single todo item with the following attributes:
  - `id` (integer): Unique identifier, auto-generated starting from 1
  - `title` (string): Task title, 1-200 characters, required
  - `description` (string): Task description, 0-1000 characters, optional
  - `completed` (boolean): Completion status, defaults to False
  - `created_at` (ISO 8601 timestamp string): UTC timestamp when task was created
  - `updated_at` (ISO 8601 timestamp string): UTC timestamp when task was last modified (initially same as created_at)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully add a task with both title and description in under 30 seconds from selecting the "Add Task" menu option.
- **SC-002**: 100% of valid task inputs (title 1-200 chars, description 0-1000 chars) result in successful task creation with correct data stored.
- **SC-003**: 100% of invalid inputs (empty title, title >200 chars, description >1000 chars) display the exact specified error message and allow retry without application crash.
- **SC-004**: All created tasks receive unique sequential IDs starting from 1 with no gaps or duplicates.
- **SC-005**: 100% of created tasks have valid ISO 8601 UTC timestamps for both created_at and updated_at fields.
- **SC-006**: Users can add tasks with empty descriptions 100% of the time by pressing Enter at the description prompt.
- **SC-007**: After successful task addition, users are returned to the main menu 100% of the time with the confirmation message displayed.

## Assumptions

- **User Interface**: Assumes a text-based menu system where users select numbered options to access features.
- **Error Codes**: Error codes (001, 002, 003) are sequential and unique across validation rules for this feature.
- **Timestamp Format**: ISO 8601 format with microseconds (YYYY-MM-DDTHH:MM:SS.ffffffZ) provides sufficient precision for task tracking.
- **ID Generation Strategy**: Sequential integer IDs are sufficient for the ephemeral in-memory system; uniqueness is guaranteed by checking the maximum existing ID.
- **Input Method**: Standard Python `input()` function is the sole input mechanism (no GUI, web forms, or file imports).
- **Whitespace Stripping**: Leading and trailing whitespace is stripped, but internal whitespace (spaces between words) is preserved.
- **Data Structure**: Task storage uses Python's standard library data structures (likely a list of dataclass instances or dictionaries).
- **Main Menu Return**: After any operation (success or error recovery), control always returns to the main menu for next user action.

## Out of Scope

- Editing or updating existing tasks
- Deleting tasks
- Viewing or listing tasks (separate feature)
- Marking tasks as complete
- Task priorities, tags, or categories
- Due dates or reminders
- Task search or filtering
- Data persistence to files or databases
- Multi-user support or task sharing
- Task import/export functionality
- Undo/redo operations
