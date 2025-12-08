# Function Contract: prompt_for_delete_confirmation()

**Module**: `src/ui/prompts.py`
**Feature**: Delete Task (004-delete-task)
**Date**: 2025-12-06

## Signature

```python
def prompt_for_delete_confirmation(task_title: str) -> bool:
    """Prompt user to confirm task deletion with Y/N response.

    Args:
        task_title: Title of the task to be deleted (for context in prompt)

    Returns:
        True if user confirms deletion (Y/y), False if user cancels (N/n)

    Raises:
        None - validation loop ensures only valid response is returned
    """
```

## Purpose

Display a confirmation prompt with the task title and collect a valid Y/N response from the user to prevent accidental deletion.

## Preconditions

1. `task_title` is a non-empty string (from existing Task object)
2. Task with this title exists in storage (validated by caller)

## Postconditions

### Success Case
1. Returns `True` if user enters Y or y (case-insensitive, whitespace-stripped)
2. Returns `False` if user enters N or n (case-insensitive, whitespace-stripped)
3. No exceptions raised (validation loop ensures valid response)
4. No modifications to storage or state (pure UI function)

### Validation Loop
1. Invalid responses (e.g., "maybe", "yes", "1", "") display ERROR 105 and re-prompt
2. Loop continues until valid Y/y/N/n response received
3. No limit on retry attempts (user can retry indefinitely)

## Implementation Strategy

```python
def prompt_for_delete_confirmation(task_title: str) -> bool:
    # Construct prompt with task title for context
    prompt = f"Delete task '{task_title}'? (Y/N): "

    # Validation loop (retry until valid response)
    while True:
        # Get user input and normalize (strip whitespace, uppercase)
        response = input(prompt).strip().upper()

        # Check for confirmation
        if response == "Y":
            return True

        # Check for cancellation
        if response == "N":
            return False

        # Invalid response - show error and re-prompt
        print(ERROR_INVALID_CONFIRMATION)
```

## Behavior Examples

### Example 1: Confirm Deletion (Uppercase)

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Buy groceries")
```

**User Interaction**:
```
Delete task 'Buy groceries'? (Y/N): Y
```

**Result**:
```python
# Returns: True
```

### Example 2: Confirm Deletion (Lowercase)

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Call dentist")
```

**User Interaction**:
```
Delete task 'Call dentist'? (Y/N): y
```

**Result**:
```python
# Returns: True
```

### Example 3: Cancel Deletion (Uppercase)

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Team meeting")
```

**User Interaction**:
```
Delete task 'Team meeting'? (Y/N): N
```

**Result**:
```python
# Returns: False
```

### Example 4: Cancel Deletion (Lowercase)

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Update resume")
```

**User Interaction**:
```
Delete task 'Update resume'? (Y/N): n
```

**Result**:
```python
# Returns: False
```

### Example 5: Invalid Response with Retry

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Finish report")
```

**User Interaction**:
```
Delete task 'Finish report'? (Y/N): maybe
ERROR 105: Invalid input. Please enter Y or N.
Delete task 'Finish report'? (Y/N): yes
ERROR 105: Invalid input. Please enter Y or N.
Delete task 'Finish report'? (Y/N): Y
```

**Result**:
```python
# Returns: True
```

### Example 6: Whitespace Handling

**Call**:
```python
confirmed = prompt_for_delete_confirmation("Test task")
```

**User Interaction**:
```
Delete task 'Test task'? (Y/N):   Y
```

**Result**:
```python
# Returns: True (whitespace stripped before validation)
```

## Dependencies

### Internal Dependencies
- None (standalone UI function)

### External Dependencies
- `src/constants.py`: ERROR_INVALID_CONFIRMATION constant
- Python standard library: `input()` function

## Constants Required

**New constant in `constants.py`**:
```python
ERROR_INVALID_CONFIRMATION = "ERROR 105: Invalid input. Please enter Y or N."
```

## Invariants

1. **No Side Effects**: Function only reads input and returns boolean (no storage modification)
2. **Always Returns**: Function never raises exceptions (validation loop ensures valid response)
3. **Case Insensitivity**: Both uppercase and lowercase Y/N are accepted
4. **Exact Match Required**: Only "Y", "y", "N", "n" are valid (not "yes", "no", "1", "0", etc.)

## Edge Cases

| Input | After Strip/Upper | Behavior |
|-------|-------------------|----------|
| "Y" | "Y" | Return True |
| "y" | "Y" | Return True |
| "N" | "N" | Return False |
| "n" | "N" | Return False |
| "  Y  " | "Y" | Return True (whitespace stripped) |
| "yes" | "YES" | Show ERROR 105, re-prompt |
| "no" | "NO" | Show ERROR 105, re-prompt |
| "1" | "1" | Show ERROR 105, re-prompt |
| "0" | "0" | Show ERROR 105, re-prompt |
| "" (empty) | "" | Show ERROR 105, re-prompt |
| "maybe" | "MAYBE" | Show ERROR 105, re-prompt |

## Testing Requirements

### Unit Tests (Minimal Set)

Mock `input()` to simulate user responses:

1. **Input "Y"**: Verify returns `True`, no error displayed
2. **Input "y"**: Verify returns `True`, no error displayed
3. **Input "N"**: Verify returns `False`, no error displayed
4. **Input "n"**: Verify returns `False`, no error displayed
5. **Input " Y " (with spaces)**: Verify returns `True` (whitespace stripped)
6. **Input "maybe" then "Y"**: Verify ERROR 105 shown once, then returns `True`
7. **Input "yes" then "no" then "N"**: Verify ERROR 105 shown twice, then returns `False`

### Integration Tests

Test as part of complete delete workflow in `test_delete_task_flow.py`:

1. Valid ID + "Y" confirmation → task deleted
2. Valid ID + "N" response → task preserved
3. Valid ID + invalid response → error shown, re-prompt works

## User Experience Requirements

1. **Context Provided**: Task title must be displayed in prompt to help user decide
2. **Clear Instructions**: Prompt clearly states "(Y/N)" format
3. **Helpful Errors**: ERROR 105 specifically states "Please enter Y or N" (not generic error)
4. **Case Flexibility**: Accept both uppercase and lowercase to reduce user friction
5. **Retry Capability**: User can correct invalid input without restarting workflow

## Security Considerations

1. **No SQL Injection Risk**: N/A (no database)
2. **No Command Injection**: Input is compared as string, never executed
3. **No XSS Risk**: N/A (CLI application, no HTML output)
4. **Input Validation**: Only Y/y/N/n accepted (prevents unexpected behavior)

## Performance Characteristics

- **Time Complexity**: O(1) for each input attempt (string comparison)
- **Space Complexity**: O(1) (single string variable)
- **User Latency**: Waits indefinitely for valid input (no timeout)

## Accessibility Notes

- **Visual Impairment**: Screen readers can read prompt clearly
- **Typo Prevention**: Confirmation prevents accidental deletion from mistyped task ID
- **Error Recovery**: Clear error message guides user to correct input format

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-06 | Initial contract | Delete Task feature specification |
