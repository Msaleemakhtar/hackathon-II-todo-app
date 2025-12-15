# Feature Specification: Update Task

**Feature Branch**: `003-update-task`
**Created**: 2025-12-06
**Status**: Draft
**Input**: User description: "update task"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Task Title and Description (Priority: P1)

A user wants to modify both the title and description of an existing task to correct mistakes or update information as the task evolves.

**Why this priority**: This is the core value proposition - users need the ability to edit task content when requirements change, mistakes are found, or more details become available. Without this, tasks become immutable after creation.

**Independent Test**: Can be fully tested by navigating to Update Task menu option, entering a valid task ID, providing new title and description, and verifying the task is updated with new values and updated_at timestamp changes.

**Acceptance Scenarios**:

1. **Given** a task with ID 2 exists with title "Buy groceries" and description "Milk and eggs", **When** the user selects "Update Task", enters ID "2", enters new title "Buy groceries for the week", and new description "Milk, eggs, bread, cheese, vegetables", **Then** the system displays "Task updated successfully.", updates the task with new values, sets updated_at to current UTC time, and returns to main menu.

2. **Given** a task with ID 5 exists, **When** the user updates only the title (keeping description the same), **Then** the task's title changes, description remains unchanged, and updated_at timestamp is updated to reflect the modification time.

---

### User Story 2 - Update Task with Selective Field Updates (Priority: P1)

A user wants to update only the title or only the description of a task without being forced to modify both fields, allowing targeted edits.

**Why this priority**: Flexibility in editing is essential - users often need to change just one field (e.g., fix a typo in title) without re-entering or modifying the other field. This improves efficiency and user experience.

**Independent Test**: Can be fully tested by navigating to Update Task, entering a task ID, selecting to update only one field (title or description), providing the new value, and verifying only that field changes while the other remains unchanged.

**Acceptance Scenarios**:

1. **Given** a task with ID 3 exists with title "Call dentist" and description "Schedule checkup", **When** the user selects "Update Task", enters ID "3", chooses "Update Title Only" from the field selection menu, and enters new title "Call dentist for appointment", **Then** the system updates only the title, leaves description as "Schedule checkup", sets updated_at to current time, displays "Task updated successfully.", and returns to main menu.

2. **Given** a task with ID 7 exists with title "Review code" and description "Check PR #42", **When** the user selects "Update Task", enters ID "7", chooses "Update Description Only", and enters new description "Check PR #42 and PR #43", **Then** the system updates only the description, leaves title as "Review code", sets updated_at to current time, and returns to main menu.

3. **Given** a task with ID 1 exists, **When** the user selects "Update Task", enters ID "1", and chooses "Update Both Title and Description", **Then** the system prompts for both new title and new description, updates both fields, and returns to main menu.

---

### User Story 3 - Handle Invalid Update Attempts (Priority: P1)

A user enters a non-existent task ID or invalid data when attempting to update a task, and the system provides clear error feedback without crashing.

**Why this priority**: Error handling is critical for user experience and system stability. Users will inevitably make mistakes, and the system must guide them gracefully.

**Independent Test**: Can be fully tested by attempting to update with non-existent task ID, invalid input types, or data exceeding validation limits, and verifying appropriate error messages are shown.

**Acceptance Scenarios**:

1. **Given** the task list contains tasks with IDs 1, 2, 3, **When** the user tries to update task ID 99, **Then** the system displays "ERROR 101: Task with ID 99 not found." and returns to the main menu.

2. **Given** the user is at the task ID prompt for updating, **When** they enter "abc" (non-numeric input), **Then** the system displays "ERROR 102: Invalid input. Please enter a numeric task ID." and re-prompts for the ID.

3. **Given** the user is updating task ID 1, **When** they enter an empty title (whitespace only), **Then** the system displays "ERROR 001: Title is required and must be 1-200 characters." and re-prompts for the title.

4. **Given** the user is updating task ID 1, **When** they enter a title with 250 characters, **Then** the system displays "ERROR 002: Title is required and must be 1-200 characters." and re-prompts for the title.

5. **Given** the user is updating task ID 1, **When** they enter a description with 1200 characters, **Then** the system displays "ERROR 003: Description cannot exceed 1000 characters." and re-prompts for the description.

---

### Edge Cases

- **Empty task list**: What happens when a user tries to update a task when no tasks exist? → Handled via FR-007 (ERROR 101)
- **Whitespace handling**: What happens when a user enters only spaces for title or description? → Title validation rejects (FR-012), description allows empty (FR-016)
- **No actual changes**: What happens if user "updates" a task with identical values? → System proceeds normally, updated_at timestamp still changes to reflect update attempt
- **Maximum length boundaries**: How does the system behave when input is exactly at limits (200 chars for title, 1000 for description)? → Accepts input (validation is ≤ not <)
- **Zero or negative IDs**: What happens when user enters ID 0 or -5? → Handled via FR-004 (ERROR 103)
- **Special characters**: Are special characters, newlines, emojis preserved? → Yes, preserved as-is (follows 001-add-task and 002-view-task patterns)

## Requirements *(mandatory)*

### Functional Requirements

#### Task Selection and Validation

- **FR-001**: System MUST provide an "Update Task" menu option accessible from the main menu.
- **FR-002**: System MUST prompt "Enter Task ID: " to collect the task ID to update.
- **FR-003**: System MUST validate that the input is a valid positive integer.
- **FR-004**: System MUST reject zero or negative integers with error message "ERROR 103: Task ID must be a positive number." and re-prompt.
- **FR-005**: System MUST reject non-numeric input with error message "ERROR 102: Invalid input. Please enter a numeric task ID." and re-prompt.
- **FR-006**: System MUST verify the task ID exists in the task list.
- **FR-007**: System MUST display error message "ERROR 101: Task with ID {id} not found." when the ID doesn't exist and return to the main menu.

#### Display Current Values and Field Selection

- **FR-008**: System MUST display the current task title and description after successful ID validation (provides context to user).
- **FR-008a**: System MUST display a field selection menu with three options:
  1. Update Title Only
  2. Update Description Only
  3. Update Both Title and Description
- **FR-008b**: System MUST prompt "Select update option (1-3): " to collect the user's choice.
- **FR-008c**: System MUST validate that the input is a valid integer between 1 and 3 (inclusive).
- **FR-008d**: System MUST reject invalid selections with error message "ERROR 104: Invalid option. Please select 1, 2, or 3." and re-prompt.

#### Title Update (When Option 1 or 3 Selected)

- **FR-009**: System MUST display a prompt "Enter New Task Title: " to collect the new task title when user selects option 1 or 3.
- **FR-010**: System MUST strip leading and trailing whitespace from the title input before validation.
- **FR-011**: System MUST validate that the stripped title is between 1 and 200 characters in length (inclusive).
- **FR-012**: System MUST reject empty or whitespace-only titles with error message "ERROR 001: Title is required and must be 1-200 characters." and re-prompt the user.
- **FR-013**: System MUST reject titles exceeding 200 characters with error message "ERROR 002: Title is required and must be 1-200 characters." and re-prompt the title.

#### Description Update (When Option 2 or 3 Selected)

- **FR-014**: System MUST display a prompt "Enter New Task Description (press Enter to clear): " to collect the new description when user selects option 2 or 3.
- **FR-015**: System MUST strip leading and trailing whitespace from the description input before validation.
- **FR-016**: System MUST allow empty descriptions (when user presses Enter without text, description becomes empty string).
- **FR-017**: System MUST reject descriptions exceeding 1000 characters with error message "ERROR 003: Description cannot exceed 1000 characters." and re-prompt the user for the description only.

#### Update Execution

- **FR-018**: System MUST update the task's title field with the new validated title value when option 1 or 3 is selected.
- **FR-019**: System MUST update the task's description field with the new validated description value when option 2 or 3 is selected.
- **FR-020**: System MUST preserve the task's title field (no changes) when option 2 is selected.
- **FR-021**: System MUST preserve the task's description field (no changes) when option 1 is selected.
- **FR-022**: System MUST set the task's updated_at field to the current UTC timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffffZ) at the moment of update, regardless of which fields are updated.
- **FR-023**: System MUST NOT modify the task's id, completed, or created_at fields during update.
- **FR-024**: System MUST display the confirmation message "Task updated successfully." after successfully updating a task.
- **FR-025**: System MUST return the user to the main menu after task update or error handling.
- **FR-026**: System MUST NOT crash under any input validation error scenario and MUST allow users to retry input.

### Key Entities

- **Task**: The existing Task entity with the following attributes (modified fields: title, description, updated_at):
  - `id` (integer): Unique identifier - **NOT MODIFIED**
  - `title` (string): Task title, 1-200 characters - **MODIFIED**
  - `description` (string): Task description, 0-1000 characters - **MODIFIED**
  - `completed` (boolean): Completion status - **NOT MODIFIED**
  - `created_at` (ISO 8601 timestamp string): UTC timestamp when task was created - **NOT MODIFIED**
  - `updated_at` (ISO 8601 timestamp string): UTC timestamp when task was last modified - **MODIFIED**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully update a task's title and description in under 30 seconds from selecting the "Update Task" menu option.
- **SC-002**: 100% of valid task updates (valid ID, title 1-200 chars, description 0-1000 chars) result in successful task modification with correct data stored.
- **SC-003**: 100% of updated tasks have their updated_at timestamp changed to the current UTC time at moment of update.
- **SC-004**: 100% of updated tasks preserve their original id, completed status, and created_at timestamp (no unintended modifications).
- **SC-005**: 100% of invalid inputs (non-existent ID, invalid ID format, empty title, title >200 chars, description >1000 chars) display the exact specified error message and allow retry without application crash.
- **SC-006**: Users are returned to the main menu after every update operation (success or error) 100% of the time with the confirmation message displayed.
- **SC-007**: Current task values are displayed before prompting for new values 100% of the time (provides context for editing).

## Assumptions

- **Update Scope**: Users can selectively update title only, description only, or both fields via explicit menu selection (Option B from clarifications)
- **Field Selection Menu**: A numbered menu (1-3) provides clear choices for which field(s) to update
- **Display Current Values**: Showing current title and description before prompting for new values improves user experience and reduces errors
- **Error Recovery**: Invalid inputs allow re-prompting within the update flow (follows 001-add-task pattern)
- **Timestamp Precision**: ISO 8601 format with microseconds provides sufficient precision for tracking updates
- **Validation Rules**: Title and description validation rules match exactly those from 001-add-task (consistency)
- **Error Codes**: Reuse existing error codes (001, 002, 003) from add-task for title/description validation; use 101, 102, 103 from view-task for ID validation; introduce new ERROR 104 for invalid field selection
- **Menu Integration**: Main menu provides a numbered "Update Task" option
- **Whitespace Handling**: Leading and trailing whitespace is stripped, but internal whitespace preserved (follows 001-add-task pattern)
- **Read-Modify-Write**: Update operation reads current task, modifies specified fields, writes back to same task ID (no task replacement/deletion)
- **Completed Status**: Updating a task does NOT change its completion status (that's handled by separate "Mark Complete" feature per constitution)

## Clarifications

### Session 2025-12-06

- **Q: Update behavior** - Can users update title only, description only, or must both fields be updated together? → **A: Option B - Selective update via menu selection** - Users explicitly choose which field(s) to update through a numbered menu (1: Title Only, 2: Description Only, 3: Both)

## Out of Scope

- Updating task completion status (separate "Mark Complete" feature exists)
- Updating task ID (IDs are immutable)
- Updating created_at timestamp (creation time is immutable)
- Bulk update of multiple tasks
- Undo/redo functionality
- Update history or change tracking
- Confirmation prompt before saving changes
- Preview of changes before committing
- Canceling an update mid-operation (user must complete or exit application)
