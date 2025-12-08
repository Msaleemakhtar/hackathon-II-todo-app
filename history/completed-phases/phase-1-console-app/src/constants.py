"""Application constants for validation and messaging."""

# Validation limits
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000

# Error codes and messages - Add Task feature
ERROR_TITLE_REQUIRED = "ERROR 001: Title is required and must be 1-200 characters."
ERROR_TITLE_TOO_LONG = "ERROR 002: Title is required and must be 1-200 characters."
ERROR_DESCRIPTION_TOO_LONG = "ERROR 003: Description cannot exceed 1000 characters."

# Error codes and messages - View Task feature
ERROR_TASK_NOT_FOUND = "ERROR 101: Task with ID {task_id} not found."
ERROR_INVALID_INPUT = "ERROR 102: Invalid input. Please enter a numeric task ID."
ERROR_INVALID_TASK_ID = "ERROR 103: Task ID must be a positive number."

# Error codes and messages - Update Task feature
ERROR_INVALID_OPTION = "ERROR 104: Invalid option. Please select 1, 2, or 3."

# Error codes and messages - Delete Task feature
ERROR_INVALID_CONFIRMATION = "ERROR 105: Invalid input. Please enter Y or N."

# Success messages
MSG_TASK_ADDED = "Task added successfully."
MSG_TASK_UPDATED = "Task updated successfully."
MSG_TASK_DELETED = "Task deleted successfully."
MSG_DELETION_CANCELED = "Deletion canceled."

# Prompts - Add Task feature
PROMPT_TITLE = "Enter Task Title: "
PROMPT_DESCRIPTION = "Enter Optional Task Description (press Enter to skip): "

# Prompts - View Task feature
PROMPT_TASK_ID = "Enter Task ID: "
MSG_NO_TASKS = "No tasks found."

# Prompts - Update Task feature
PROMPT_FIELD_SELECTION = "Select update option (1-3): "
PROMPT_NEW_TITLE = "Enter New Task Title: "
PROMPT_NEW_DESCRIPTION = "Enter New Task Description (press Enter to clear): "

# Error codes and messages - Mark Complete feature
ERROR_MARK_COMPLETE_NOT_FOUND = "ERROR 201: Task with ID {task_id} not found."
ERROR_MARK_COMPLETE_INVALID_INPUT = "ERROR 202: Invalid input. Please enter a numeric task ID."
ERROR_MARK_COMPLETE_INVALID_ID = "ERROR 203: Task ID must be a positive number."
# ERROR 204: Reserved for future use
ERROR_MARK_COMPLETE_CONFIRMATION = "ERROR 205: Invalid input. Please enter Y or N."

# Success messages - Mark Complete feature
MSG_TASK_MARKED_COMPLETE = "Task marked as complete."
MSG_TASK_MARKED_INCOMPLETE = "Task marked as incomplete."
MSG_MARK_COMPLETE_CANCELED = "Operation canceled."

# Prompts - Mark Complete feature
PROMPT_MARK_COMPLETE_ID = "Enter Task ID to mark complete/incomplete: "
