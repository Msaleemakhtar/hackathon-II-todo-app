# Feature Specification: Delete Task

**Feature Branch**: `004-delete-task`
**Created**: 2025-12-06
**Status**: Draft
**Input**: User description: "delete-task feature"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Single Task by ID (Priority: P1)

A user wants to permanently remove a task from their task list by entering its ID, typically when the task is no longer relevant or was created by mistake.

**Why this priority**: This is the core value proposition - users need the ability to remove tasks they no longer need. Without this capability, the task list becomes cluttered with obsolete or erroneous tasks, reducing usability and clarity.

**Independent Test**: Can be fully tested by navigating to Delete Task menu option, entering a valid task ID, confirming the deletion, and verifying the task is removed from the task list permanently.

**Acceptance Scenarios**:

1. **Given** a task with ID 3 exists in the task list with title "Buy groceries", **When** the user selects "Delete Task", enters ID "3", and confirms deletion with "Y", **Then** the system displays "Task deleted successfully.", removes task ID 3 from the list, and returns to the main menu.

2. **Given** the task list contains 5 tasks with IDs [1, 2, 3, 4, 5], **When** the user deletes task ID 3, **Then** the task list contains 4 tasks with IDs [1, 2, 4, 5] (ID 3 is permanently removed, other IDs remain unchanged).

3. **Given** a task with ID 7 exists, **When** the user selects "Delete Task", enters ID "7", and confirms with "y" (lowercase), **Then** the system treats "y" as equivalent to "Y", deletes the task, and displays "Task deleted successfully."

---

### User Story 2 - Cancel Deletion Operation (Priority: P1)

A user wants the ability to cancel a deletion operation after entering a task ID, preventing accidental deletion of important tasks.

**Why this priority**: Deletion is a destructive, irreversible operation. A confirmation step prevents user errors and provides a safety net against accidental deletions. This is a critical UX feature for any delete functionality.

**Independent Test**: Can be fully tested by navigating to Delete Task, entering a valid task ID, canceling with "N" at the confirmation prompt, and verifying the task remains in the list unchanged.

**Acceptance Scenarios**:

1. **Given** a task with ID 2 exists with title "Call dentist", **When** the user selects "Delete Task", enters ID "2", sees the confirmation prompt "Delete task 'Call dentist'? (Y/N): ", and enters "N", **Then** the system displays "Deletion canceled.", task ID 2 remains in the list with all data unchanged, and returns to the main menu.

2. **Given** a task with ID 5 exists, **When** the user enters "n" (lowercase) at the confirmation prompt, **Then** the system treats "n" as equivalent to "N", cancels the deletion, displays "Deletion canceled.", and returns to the main menu.

3. **Given** the confirmation prompt is displayed, **When** the user enters an invalid response (e.g., "maybe", "x", "1"), **Then** the system displays "ERROR 105: Invalid input. Please enter Y or N." and re-prompts for confirmation.

---

### User Story 3 - Handle Invalid Deletion Attempts (Priority: P1)

A user enters a non-existent task ID or invalid input when attempting to delete a task, and the system provides clear error feedback without crashing.

**Why this priority**: Error handling is critical for system stability and user experience. Users will make mistakes, and the system must gracefully handle invalid inputs without data corruption or application crashes.

**Independent Test**: Can be fully tested by attempting to delete with non-existent task ID, invalid input types, or invalid confirmation responses, and verifying appropriate error messages are shown without system crashes.

**Acceptance Scenarios**:

1. **Given** the task list contains tasks with IDs [1, 2, 4, 5], **When** the user tries to delete task ID 3 (which doesn't exist), **Then** the system displays "ERROR 101: Task with ID 3 not found." and returns to the main menu without prompting for confirmation.

2. **Given** the user is at the task ID prompt for deletion, **When** they enter "abc" (non-numeric input), **Then** the system displays "ERROR 102: Invalid input. Please enter a numeric task ID." and re-prompts for the ID.

3. **Given** the user is at the task ID prompt, **When** they enter "0" or "-5" (zero or negative number), **Then** the system displays "ERROR 103: Task ID must be a positive number." and re-prompts for the ID.

4. **Given** the task list is empty (no tasks), **When** the user tries to delete any task ID, **Then** the system displays "ERROR 101: Task with ID {id} not found." and returns to the main menu.

---

### Edge Cases

- **Empty task list**: What happens when a user tries to delete a task when no tasks exist? → Handled via FR-007 (ERROR 101: Task not found)
- **Last remaining task**: What happens when deleting the only task in the list? → Task is removed, list becomes empty, no special handling needed
- **ID gaps after deletion**: After deleting task ID 3 from [1, 2, 3, 4, 5], do remaining IDs stay as [1, 2, 4, 5] or renumber to [1, 2, 3, 4]? → IDs remain unchanged (no renumbering), resulting in [1, 2, 4, 5]
- **Deleted task references**: Can deleted task IDs be reused for new tasks? → Yes, ID assignment follows existing system behavior (likely incremental counter, but reuse is technically possible if counter resets or uses gaps)
- **Case sensitivity**: Is confirmation input case-sensitive? → No, both "Y"/"y" and "N"/"n" are accepted (FR-013)
- **Whitespace in confirmation**: What if user enters " Y " (with spaces)? → System strips whitespace before validation (FR-012)
- **Completed vs incomplete tasks**: Can both completed and incomplete tasks be deleted? → Yes, deletion works regardless of completion status (no distinction in behavior)

## Requirements *(mandatory)*

### Functional Requirements

#### Task Selection and Validation

- **FR-001**: System MUST provide a "Delete Task" menu option accessible from the main menu.
- **FR-002**: System MUST display prompt "Enter Task ID to delete: " to collect the task ID for deletion.
- **FR-003**: System MUST validate that the input is a valid positive integer.
- **FR-004**: System MUST reject zero or negative integers with error message "ERROR 103: Task ID must be a positive number." and re-prompt.
- **FR-005**: System MUST reject non-numeric input with error message "ERROR 102: Invalid input. Please enter a numeric task ID." and re-prompt.
- **FR-006**: System MUST verify the task ID exists in the task list.
- **FR-007**: System MUST display error message "ERROR 101: Task with ID {id} not found." when the ID doesn't exist and return to the main menu (no confirmation prompt shown).

#### Deletion Confirmation

- **FR-008**: System MUST display the task title in the confirmation prompt after successful ID validation to provide context: "Delete task '{title}'? (Y/N): "
- **FR-009**: System MUST wait for user confirmation input before proceeding with deletion.
- **FR-010**: System MUST accept both uppercase and lowercase responses: "Y", "y", "N", "n".
- **FR-011**: System MUST reject any input other than Y/y/N/n with error message "ERROR 105: Invalid input. Please enter Y or N." and re-prompt for confirmation.
- **FR-012**: System MUST strip leading and trailing whitespace from confirmation input before validation.
- **FR-013**: System MUST treat "Y" and "y" as confirmation to proceed with deletion.
- **FR-014**: System MUST treat "N" and "n" as cancellation of deletion.

#### Deletion Execution

- **FR-015**: System MUST permanently remove the task from the task list when user confirms with Y/y.
- **FR-016**: System MUST display confirmation message "Task deleted successfully." after successful deletion.
- **FR-017**: System MUST preserve all other tasks in the list unchanged when a task is deleted (no ID renumbering or data modification).
- **FR-018**: System MUST NOT modify the deleted task's ID assignment for future tasks (IDs are not reused immediately, but system may reuse gaps based on ID generation logic).

#### Cancellation Handling

- **FR-019**: System MUST preserve the task in the list unchanged when user cancels with N/n.
- **FR-020**: System MUST display message "Deletion canceled." when user chooses not to proceed.
- **FR-021**: System MUST return to the main menu after deletion cancellation.

#### General Behavior

- **FR-022**: System MUST return the user to the main menu after successful deletion, cancellation, or error handling.
- **FR-023**: System MUST NOT crash under any input validation error scenario and MUST allow users to retry input.
- **FR-024**: System MUST handle deletion regardless of task completion status (both completed and incomplete tasks can be deleted).

### Key Entities

- **Task**: The existing Task entity that may be deleted. Deletion removes the entire entity from storage:
  - `id` (integer): Unique identifier - used for selection
  - `title` (string): Task title - displayed in confirmation prompt
  - `description` (string): Task description - not displayed during deletion
  - `completed` (boolean): Completion status - does not affect deletion eligibility
  - `created_at` (ISO 8601 timestamp string): Creation timestamp
  - `updated_at` (ISO 8601 timestamp string): Last modification timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully delete a task in under 15 seconds from selecting the "Delete Task" menu option.
- **SC-002**: 100% of confirmed deletions (valid ID + Y/y confirmation) result in permanent task removal from the list.
- **SC-003**: 100% of canceled deletions (valid ID + N/n response) result in task preservation with no data changes.
- **SC-004**: 100% of invalid inputs (non-existent ID, invalid ID format, invalid confirmation response) display the exact specified error message and allow retry without application crash.
- **SC-005**: Users are returned to the main menu after every delete operation (success, cancellation, or error) 100% of the time.
- **SC-006**: Task title is displayed in the confirmation prompt 100% of the time for valid task IDs (provides context for deletion decision).
- **SC-007**: 100% of deletion operations preserve the IDs and data of all non-deleted tasks (no unintended side effects).
- **SC-008**: System handles empty task list deletion attempts gracefully 100% of the time with appropriate error message.

## Assumptions

- **Confirmation Required**: All deletions require explicit Y/N confirmation to prevent accidental data loss (industry-standard UX pattern for destructive operations).
- **Case Insensitivity**: Confirmation accepts both uppercase and lowercase (Y/y/N/n) for user convenience.
- **Whitespace Handling**: Leading and trailing whitespace is stripped from confirmation input (follows standard input handling pattern).
- **ID Persistence**: Remaining task IDs are not renumbered after deletion (preserves referential integrity and follows immutable ID principle).
- **No Soft Delete**: Deletion is permanent and immediate (no "trash" or "undo" functionality in Phase I per constitution scope limitations).
- **Error Code Reuse**: Reuse existing error codes from view-task (101, 102, 103) for ID validation; introduce new ERROR 105 for invalid confirmation input.
- **Title in Prompt**: Displaying task title in confirmation prompt reduces user errors by providing context about what will be deleted.
- **Menu Integration**: Main menu provides a numbered "Delete Task" option.
- **Completion Agnostic**: Both completed and incomplete tasks can be deleted (no special handling based on status).
- **Empty List Handling**: Attempting to delete from empty list returns error message, not a special "empty list" message (consistent with non-existent ID error).

## Out of Scope

- Soft delete / trash / recycle bin functionality
- Undo deletion capability
- Deletion history or audit log
- Bulk delete (deleting multiple tasks at once)
- Delete by criteria (e.g., "delete all completed tasks")
- Confirmation preview showing full task details
- Renumbering task IDs after deletion
- Archive functionality (moving tasks instead of deleting)
- Permission checks or deletion restrictions
- Deletion notifications or warnings based on task properties
