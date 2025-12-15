# Quickstart Guide: View Task Feature

**Feature**: 002-view-task
**Version**: 1.0
**Last Updated**: 2025-12-06

## Overview

The View Task feature allows you to view your todo tasks in two ways:
1. **View Tasks** - See all tasks in a list format
2. **View Task Details** - See complete details for a specific task

This is a **read-only** feature - you can view tasks but not modify them.

---

## Quick Start

### Starting the Application

```bash
uv run python src/main.py
```

You'll see the main menu with numbered options:

```
=== Todo App ===
1. Add Task
2. View Tasks
3. View Task Details
4. Update Task
5. Delete Task
6. Mark Complete
7. Exit

Enter your choice:
```

---

## Feature 1: View All Tasks

**Purpose**: Display a list of all your tasks with their completion status.

### How to Use

1. **Select Option 2** from the main menu:
   ```
   Enter your choice: 2
   ```

2. **View the task list**:
   ```
   1. [ ] Buy groceries
   2. [X] Complete project report
   3. [ ] Call dentist

   Total: 3 tasks
   ```

3. **Return to menu**: You'll automatically return to the main menu after viewing.

### Understanding the Display

- **ID Number**: The number at the start (e.g., `1.`, `2.`)
- **Completion Status**:
  - `[ ]` = Task is **not complete**
  - `[X]` = Task is **complete**
- **Title**: The task description

### Special Cases

#### Empty Task List
If you have no tasks, you'll see:
```
No tasks found.
```

#### Large Lists (20+ Tasks)
If you have more than 20 tasks, the display will pause every 20 tasks:
```
1. [ ] Task 1
2. [ ] Task 2
...
20. [ ] Task 20
Press Enter to continue...
```

Just press **Enter** to see the next batch of tasks.

---

## Feature 2: View Task Details

**Purpose**: See complete information about a specific task, including its description and timestamps.

### How to Use

1. **Select Option 3** from the main menu:
   ```
   Enter your choice: 3
   ```

2. **Enter the task ID** you want to view:
   ```
   Enter Task ID: 2
   ```

3. **View the details**:
   ```
   ID: 2
   Title: Buy groceries
   Description: Milk, eggs, bread
   Completed: No
   Created At: 2025-12-06T10:00:00.000000Z
   Updated At: 2025-12-06T10:00:00.000000Z
   ```

4. **Return to menu**: You'll automatically return to the main menu after viewing.

### Understanding the Details

| Field | Description |
|-------|-------------|
| **ID** | Unique task number |
| **Title** | Task name (1-200 characters) |
| **Description** | Detailed notes (0-1000 characters) |
| **Completed** | "Yes" if complete, "No" if not |
| **Created At** | When the task was first created (UTC time) |
| **Updated At** | When the task was last modified (UTC time) |

### Special Cases

#### Empty Description
If a task has no description, you'll see:
```
Description: (No description)
```

#### Multi-line Descriptions
Descriptions with multiple lines display as-is:
```
Description: Shopping list:
- Milk
- Eggs
- Bread
```

---

## Error Handling

The View Task Details feature validates your input and provides helpful error messages:

### Error 102: Invalid Input

**Cause**: You entered something that's not a number.

**Example**:
```
Enter Task ID: abc
ERROR 102: Invalid input. Please enter a numeric task ID.
Enter Task ID:
```

**Solution**: Enter a number (e.g., `1`, `5`, `42`)

---

### Error 103: Invalid Task ID Range

**Cause**: You entered zero or a negative number.

**Example**:
```
Enter Task ID: 0
ERROR 103: Task ID must be a positive number.
Enter Task ID:
```

**Solution**: Enter a positive number (e.g., `1`, `2`, `3`)

---

### Error 101: Task Not Found

**Cause**: No task exists with that ID.

**Example**:
```
Enter Task ID: 99
ERROR 101: Task with ID 99 not found.

[Returns to main menu]
```

**Solution**:
- Use "View Tasks" (option 2) to see which task IDs exist
- Then use "View Task Details" (option 3) with a valid ID

---

## Common Workflows

### Workflow 1: Browse All Tasks Then View One

```
1. Select option 2 (View Tasks)
   → See list: 1, 2, 3, 4, 5

2. Return to main menu

3. Select option 3 (View Task Details)
   → Enter ID: 3
   → See full details for task #3
```

### Workflow 2: Check If Any Tasks Exist

```
1. Select option 2 (View Tasks)
   → If "No tasks found." appears, you have no tasks
   → Add tasks using option 1 (Add Task)
```

### Workflow 3: Find a Task's Creation Date

```
1. Select option 3 (View Task Details)
2. Enter the task ID
3. Look at "Created At:" field
   → Shows UTC timestamp (e.g., 2025-12-06T10:00:00.000000Z)
```

---

## Tips and Best Practices

### 1. Use List View First
Always start with "View Tasks" (option 2) to see what tasks exist before using "View Task Details" (option 3).

### 2. Understanding Timestamps
- Timestamps are in **UTC time zone**
- Format: `YYYY-MM-DDTHH:MM:SS.ffffffZ`
- Example: `2025-12-06T10:00:00.000000Z` = December 6, 2025 at 10:00 AM UTC

### 3. Working with Long Lists
For lists over 20 tasks:
- Press **Enter** at each "Press Enter to continue..." prompt
- Count shown at bottom: `Total: 45 tasks`

### 4. Retry on Errors
- **ERROR 102** and **ERROR 103** let you try again
- **ERROR 101** returns you to the main menu (task doesn't exist)

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Continue (during pagination) |
| **Ctrl+C** | Exit application immediately |

---

## Limitations (By Design)

This feature is **read-only** and does NOT support:

- ❌ Editing tasks while viewing
- ❌ Deleting tasks from the view screen
- ❌ Filtering or searching tasks
- ❌ Sorting tasks (always displays in creation order)
- ❌ Selecting multiple tasks
- ❌ Copying task details to clipboard
- ❌ Exporting tasks to files

**Note**: Use other menu options (Update, Delete, Mark Complete) to modify tasks.

---

## Examples

### Example 1: Viewing Your Daily Tasks

```
Enter your choice: 2

1. [ ] Morning workout
2. [ ] Check emails
3. [X] Team standup meeting
4. [ ] Review pull requests
5. [ ] Write documentation

Total: 5 tasks

[Returns to main menu]
```

### Example 2: Checking Task Details

```
Enter your choice: 3
Enter Task ID: 4

ID: 4
Title: Review pull requests
Description: Check PRs #123, #124, #125 for security issues
Completed: No
Created At: 2025-12-06T09:00:00.000000Z
Updated At: 2025-12-06T09:00:00.000000Z

[Returns to main menu]
```

### Example 3: Handling Invalid Input

```
Enter your choice: 3
Enter Task ID: test
ERROR 102: Invalid input. Please enter a numeric task ID.
Enter Task ID: -5
ERROR 103: Task ID must be a positive number.
Enter Task ID: 999
ERROR 101: Task with ID 999 not found.

[Returns to main menu]
```

---

## Troubleshooting

### Problem: "No tasks found" but I added tasks earlier

**Cause**: The application is in-memory only. Tasks are lost when you exit.

**Solution**: This is expected behavior. Tasks only exist while the application is running.

---

### Problem: I can't find a specific task

**Solution**:
1. Use "View Tasks" (option 2) to see all task IDs
2. Look for the task title in the list
3. Note the ID number
4. Use "View Task Details" (option 3) with that ID

---

### Problem: Long descriptions are cut off

**Cause**: Your terminal window may be too narrow.

**Solution**:
- Maximize your terminal window
- Descriptions are not truncated - they wrap to multiple lines
- Scroll up if needed to see the full description

---

### Problem: Special characters look wrong

**Cause**: Your terminal may not support UTF-8 encoding.

**Solution**:
- Ensure your terminal uses UTF-8 encoding
- Most modern terminals support emojis and Unicode characters
- Example: "Buy 🥛 and 🥚" should display correctly

---

## Related Features

- **Add Task** (Option 1) - Create new tasks to view
- **Update Task** (Option 4) - Modify task title or description
- **Mark Complete** (Option 5) - Toggle completion status (changes `[ ]` to `[X]`)
- **Delete Task** (Option 6) - Remove tasks from the list

---

## Technical Details

### Performance
- **List View**: Displays all tasks in under 5 seconds (typically instant)
- **Detail View**: Displays task details in under 10 seconds (typically instant)

### Data Freshness
- Task data is always current (no caching)
- Changes from other menu options (Update, Mark Complete) are immediately visible

### Compatibility
- Works on all platforms: Windows, macOS, Linux
- Requires Python 3.13 or newer
- No external dependencies (uses standard library)

---

## Getting Help

- **In-app**: Error messages provide specific guidance
- **Documentation**: See `specs/002-view-task/spec.md` for complete specification
- **Source Code**: See `src/services/task_service.py` and `src/ui/prompts.py`

---

**Ready to view your tasks?** Run `uv run python src/main.py` and select option 2 or 3!
