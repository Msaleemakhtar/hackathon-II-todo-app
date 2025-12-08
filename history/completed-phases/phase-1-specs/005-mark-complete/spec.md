# Feature Specification: Mark Complete

**Feature Branch**: `005-mark-complete`
**Created**: 2025-12-06
**Status**: Draft
**Input**: User description: "Mark-complete feature"

## Clarifications

### Session 2025-12-06

- Q: When an invalid confirmation response is entered (like "yes", "maybe", "1"), should the system re-prompt indefinitely until valid input is received, or implement a maximum retry limit before canceling the operation? → A: Re-prompt indefinitely until valid Y/y/N/n is entered (consistent with ID validation pattern)
- Q: The spec mentions pytest for testing but doesn't specify how test data (tasks) should be set up for each test case. Should tests use a shared task repository fixture with predefined tasks, or should each test create its own isolated task data within the test function? → A: Each test creates its own task data independently (no shared test data across tests)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Toggle Task to Complete (Priority: P1)

A user wants to mark an incomplete task as complete to track their progress and indicate that a task has been finished.

**Why this priority**: This is the core value proposition - users need to mark tasks as done to track accomplishments and distinguish between pending work and completed work. Without this capability, the todo app provides no way to track task completion.

**Independent Test**: Can be fully tested by navigating to Mark Complete menu option, entering the ID of an incomplete task, and verifying the task's completed status changes to True and the updated_at timestamp is updated.

**Acceptance Scenarios**:

1. **Given** a task with ID 2 exists with completed status False, **When** the user selects "Mark Complete", enters ID "2", and confirms with "Y", **Then** the system displays "Task marked as complete.", sets the task's completed field to True, updates the updated_at timestamp to current UTC time, and returns to the main menu.

2. **Given** the task list contains tasks with IDs [1, 2, 3] where task 2 has completed=False, **When** the user marks task ID 2 as complete, **Then** task 2 has completed=True, tasks 1 and 3 remain unchanged, and the updated_at timestamp for task 2 reflects the time of the operation.

3. **Given** a task with ID 5 exists with completed=False, **When** the user selects "Mark Complete", enters ID "5", and confirms with "y" (lowercase), **Then** the system treats "y" as equivalent to "Y", marks the task as complete, and displays "Task marked as complete."

---

### User Story 2 - Toggle Task to Incomplete (Priority: P1)

A user wants to mark a completed task back to incomplete when they realize the task needs more work or was marked complete by mistake.

**Why this priority**: Users make mistakes and tasks sometimes need to be reopened. This toggle functionality provides flexibility and prevents the need to delete and recreate tasks when status changes are needed.

**Independent Test**: Can be fully tested by navigating to Mark Complete (or Mark Incomplete if menu option changes), entering the ID of a completed task, and verifying the task's completed status changes to False and the updated_at timestamp is updated.

**Acceptance Scenarios**:

1. **Given** a task with ID 3 exists with completed status True, **When** the user selects "Mark Complete", enters ID "3", and confirms with "Y", **Then** the system displays "Task marked as incomplete.", sets the task's completed field to False, updates the updated_at timestamp to current UTC time, and returns to the main menu.

2. **Given** the task list contains tasks with IDs [1, 2, 3] where task 2 has completed=True, **When** the user toggles task ID 2, **Then** task 2 has completed=False, tasks 1 and 3 remain unchanged, and the updated_at timestamp for task 2 reflects the time of the operation.

---

### User Story 3 - Cancel Status Change Operation (Priority: P1)

A user wants the ability to cancel a status change operation after entering a task ID, preventing accidental modifications.

**Why this priority**: A confirmation step prevents user errors when they select the wrong task ID. This provides a safety net similar to the delete operation's confirmation pattern.

**Independent Test**: Can be fully tested by navigating to Mark Complete, entering a valid task ID, canceling with "N" at the confirmation prompt, and verifying the task's status remains unchanged.

**Acceptance Scenarios**:

1. **Given** a task with ID 4 exists with completed=False and title "Buy groceries", **When** the user selects "Mark Complete", enters ID "4", sees the confirmation prompt "Mark task 'Buy groceries' as complete? (Y/N): ", and enters "N", **Then** the system displays "Operation canceled.", task ID 4 remains with completed=False and unchanged updated_at timestamp, and returns to the main menu.

2. **Given** a task with ID 7 exists with completed=True, **When** the user enters "n" (lowercase) at the confirmation prompt, **Then** the system treats "n" as equivalent to "N", cancels the operation, displays "Operation canceled.", and returns to the main menu.

3. **Given** the confirmation prompt is displayed, **When** the user enters an invalid response (e.g., "yes", "no", "1"), **Then** the system displays "ERROR 205: Invalid input. Please enter Y or N." and re-prompts for confirmation.

---

### User Story 4 - Handle Invalid Status Change Attempts (Priority: P1)

A user enters a non-existent task ID or invalid input when attempting to mark a task as complete/incomplete, and the system provides clear error feedback without crashing.

**Why this priority**: Error handling is critical for system stability and user experience. Users will make mistakes, and the system must gracefully handle invalid inputs without data corruption or application crashes.

**Independent Test**: Can be fully tested by attempting to mark complete with non-existent task ID, invalid input types, and verifying appropriate error messages are shown without system crashes.

**Acceptance Scenarios**:

1. **Given** the task list contains tasks with IDs [1, 2, 4, 5], **When** the user tries to mark task ID 3 as complete (which doesn't exist), **Then** the system displays "ERROR 201: Task with ID 3 not found." and returns to the main menu without prompting for confirmation.

2. **Given** the user is at the task ID prompt for marking complete, **When** they enter "abc" (non-numeric input), **Then** the system displays "ERROR 202: Invalid input. Please enter a numeric task ID." and re-prompts for the ID.

3. **Given** the user is at the task ID prompt, **When** they enter "0" or "-3" (zero or negative number), **Then** the system displays "ERROR 203: Task ID must be a positive number." and re-prompts for the ID.

4. **Given** the task list is empty (no tasks), **When** the user tries to mark any task ID as complete, **Then** the system displays "ERROR 201: Task with ID {id} not found." and returns to the main menu.

---

### Edge Cases

- **Empty task list**: What happens when a user tries to mark a task complete when no tasks exist? → Handled via FR-007 (ERROR 201: Task not found)
- **Toggle behavior confirmation**: Does the confirmation prompt text change based on current status? → Yes, "Mark task '{title}' as complete? (Y/N):" for incomplete tasks, "Mark task '{title}' as incomplete? (Y/N):" for complete tasks (FR-008)
- **Case sensitivity**: Is confirmation input case-sensitive? → No, both "Y"/"y" and "N"/"n" are accepted (FR-013)
- **Whitespace in confirmation**: What if user enters " Y " (with spaces)? → System strips whitespace before validation (FR-012)
- **Multiple rapid toggles**: Can a task be toggled multiple times in succession? → Yes, each toggle updates the status and updated_at timestamp independently
- **Timestamp precision**: Is the updated_at timestamp updated every time status is toggled? → Yes, updated_at reflects the exact time of the toggle operation (FR-016)
- **created_at preservation**: Does toggling status affect created_at? → No, created_at remains unchanged; only updated_at is modified (FR-017)

## Requirements *(mandatory)*

### Functional Requirements

#### Task Selection and Validation

- **FR-001**: System MUST provide a "Mark Complete" menu option accessible from the main menu.
- **FR-002**: System MUST display prompt "Enter Task ID to mark complete/incomplete: " to collect the task ID for status change.
- **FR-003**: System MUST validate that the input is a valid positive integer.
- **FR-004**: System MUST reject zero or negative integers with error message "ERROR 203: Task ID must be a positive number." and re-prompt.
- **FR-005**: System MUST reject non-numeric input with error message "ERROR 202: Invalid input. Please enter a numeric task ID." and re-prompt.
- **FR-006**: System MUST verify the task ID exists in the task list.
- **FR-007**: System MUST display error message "ERROR 201: Task with ID {id} not found." when the ID doesn't exist and return to the main menu (no confirmation prompt shown).

#### Status Change Confirmation

- **FR-008**: System MUST display different confirmation prompts based on current task status:
  - For incomplete tasks (completed=False): "Mark task '{title}' as complete? (Y/N): "
  - For complete tasks (completed=True): "Mark task '{title}' as incomplete? (Y/N): "
- **FR-009**: System MUST wait for user confirmation input before proceeding with status change.
- **FR-010**: System MUST accept both uppercase and lowercase responses: "Y", "y", "N", "n".
- **FR-011**: System MUST reject any input other than Y/y/N/n with error message "ERROR 205: Invalid input. Please enter Y or N." and re-prompt for confirmation indefinitely until valid input is received (no retry limit).
- **FR-012**: System MUST strip leading and trailing whitespace from confirmation input before validation.
- **FR-013**: System MUST treat "Y" and "y" as confirmation to proceed with status change.
- **FR-014**: System MUST treat "N" and "n" as cancellation of status change.

#### Status Toggle Execution

- **FR-015**: System MUST toggle the completed status when user confirms with Y/y:
  - If completed=False, set to True
  - If completed=True, set to False
- **FR-016**: System MUST update the task's updated_at timestamp to current UTC time in ISO 8601 format when status is toggled.
- **FR-017**: System MUST NOT modify the task's created_at timestamp during status change.
- **FR-018**: System MUST preserve all other task attributes (id, title, description) unchanged during status change.
- **FR-019**: System MUST display success message based on new status:
  - After marking complete (completed=True): "Task marked as complete."
  - After marking incomplete (completed=False): "Task marked as incomplete."

#### Cancellation Handling

- **FR-020**: System MUST preserve the task unchanged when user cancels with N/n.
- **FR-021**: System MUST display message "Operation canceled." when user chooses not to proceed.
- **FR-022**: System MUST return to the main menu after operation cancellation.

#### General Behavior

- **FR-023**: System MUST return the user to the main menu after successful status change, cancellation, or error handling.
- **FR-024**: System MUST NOT crash under any input validation error scenario and MUST allow users to retry input.

### Key Entities

- **Task**: The existing Task entity whose completed status will be toggled:
  - `id` (integer): Unique identifier - used for selection
  - `title` (string): Task title - displayed in confirmation prompt
  - `description` (string): Task description - not displayed during status change
  - `completed` (boolean): **Completion status - toggled by this feature**
  - `created_at` (ISO 8601 timestamp string): Creation timestamp - never modified
  - `updated_at` (ISO 8601 timestamp string): **Last modification timestamp - updated on every toggle**

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully toggle a task's completion status in under 15 seconds from selecting the "Mark Complete" menu option.
- **SC-002**: 100% of confirmed status changes (valid ID + Y/y confirmation) result in correct completed field toggle (False→True or True→False).
- **SC-003**: 100% of confirmed status changes update the updated_at timestamp to reflect the operation time.
- **SC-004**: 100% of status changes preserve the created_at timestamp unchanged.
- **SC-005**: 100% of canceled operations (valid ID + N/n response) result in task preservation with no field changes.
- **SC-006**: 100% of invalid inputs (non-existent ID, invalid ID format, invalid confirmation response) display the exact specified error message and allow retry without application crash.
- **SC-007**: Users are returned to the main menu after every operation (success, cancellation, or error) 100% of the time.
- **SC-008**: Confirmation prompt displays correct action verb ("complete" vs "incomplete") based on current task status 100% of the time.
- **SC-009**: Success message displays correct status ("marked as complete" vs "marked as incomplete") based on new task status 100% of the time.
- **SC-010**: 100% of toggle operations preserve all other task attributes (id, title, description) unchanged.

## Assumptions

- **Toggle Behavior**: Single "Mark Complete" menu option handles both marking complete and marking incomplete (smart toggle based on current state), rather than separate menu options for each direction.
- **Confirmation Required**: All status changes require explicit Y/N confirmation to prevent accidental modifications (consistent with delete operation pattern).
- **Case Insensitivity**: Confirmation accepts both uppercase and lowercase (Y/y/N/n) for user convenience.
- **Whitespace Handling**: Leading and trailing whitespace is stripped from confirmation input (follows standard input handling pattern).
- **Dynamic Prompts**: Confirmation prompt text dynamically reflects the action that will be taken ("mark as complete" vs "mark as incomplete") to provide clear context.
- **Dynamic Success Messages**: Success message dynamically reflects the new status to confirm the operation result.
- **Error Code Sequence**: New error codes (201-205) follow the pattern from previous features: 101-105 (delete), 151-155 (update), 201-205 (mark complete).
- **Timestamp Update**: Only updated_at is modified; created_at is immutable for all update operations.
- **Title in Prompt**: Displaying task title in confirmation prompt reduces user errors by providing context about which task is being modified.
- **Menu Integration**: Main menu provides a numbered "Mark Complete" option (or similar label like "Toggle Complete").
- **Test Data Isolation**: Each test creates its own task data independently without shared fixtures, ensuring test independence and preventing cross-test contamination.

## Out of Scope

- Marking multiple tasks complete at once (bulk operations)
- Setting completion percentage (partial completion)
- Completion history or audit trail
- Automatic status changes based on rules
- Completion date tracking (separate from updated_at)
- Undo toggle capability
- Visual indicators in task list (that's part of View Tasks feature)
- Filtering tasks by completion status (that's part of View Tasks feature)
- Completion statistics or reporting
