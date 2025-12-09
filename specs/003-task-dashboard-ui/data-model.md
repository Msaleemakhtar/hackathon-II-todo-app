# Frontend Data Model: Task Management Dashboard

This document outlines the data models used by the frontend application. These models define the shape of data consumed from the backend API and the state managed within the UI.

## 1. Core Data Entities (from API)

These models represent the data retrieved from the backend. They align with the schemas defined in the `002-task-tag-api` feature.

### Task

Represents a single task item.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `number` | Unique identifier for the task. |
| `title` | `string` | The title of the task (1-200 characters). |
| `description` | `string \| null` | A detailed description of the task (max 1000 characters). |
| `completed` | `boolean` | The completion status of the task. |
| `priority` | `'low' \| 'medium' \| 'high'` | The priority level of the task. |
| `due_date` | `string \| null` | ISO 8601 datetime string for the due date. |
| `created_at` | `string` | ISO 8601 datetime string of when the task was created. |
| `updated_at` | `string` | ISO 8601 datetime string of the last update. |
| `tags` | `Tag[]` | An array of tags associated with the task. |

### Tag

Represents a single tag.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `number` | Unique identifier for the tag. |
| `name` | `string` | The name of the tag (1-50 characters). |
| `color` | `string \| null` | A hex color code for the tag's UI display. |

### UserProfile

Represents the currently authenticated user.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | The user's unique identifier. |
| `email` | `string` | The user's email address. |
| `name` | `string \| null` | The user's display name. |

## 2. Frontend-Specific UI Models

These models extend the core entities with properties needed for UI rendering and state management.

### TaskDisplay

A decorated `Task` model for display purposes.

| Field | Type | Description |
| :--- | :--- | :--- |
| `...task` | `Task` | All properties of the core `Task` model. |
| `ui_status` | `'Not Started' \| 'In Progress' \| 'Completed'` | The calculated status for the UI, based on `completed` and `updated_at` vs `created_at`. |
| `is_loading` | `boolean` | `true` if this specific task is undergoing an API operation (e.g., update, delete). |

## 3. Global UI State (Zustand Store)

This model defines the global state managed by Zustand.

| Field | Type | Description |
| :--- | :--- | :--- |
| `tasks` | `TaskDisplay[]` | The list of all tasks fetched from the server. |
| `tags` | `Tag[]` | The list of all tags fetched from the server. |
| `userProfile` | `UserProfile \| null` | The profile of the logged-in user. |
| `isLoadingTasks` | `boolean` | `true` when initially fetching the list of tasks. |
| `error` | `string \| null` | A global error message to display to the user. |
| `searchTerm` | `string` | The current value of the search input. |
| `filters` | `object` | An object containing active filters for status, priority, and tags. |
| `sort` | `object` | An object defining the current sort key and direction. |
| `isCreateTaskModalOpen` | `boolean` | `true` if the modal for creating a new task is open. |
| `editingTaskId` | `number \| null` | The ID of the task currently being edited, or `null`. |
| `taskStats`| `object` | Object with `{ completed: number, inProgress: number, notStarted: number }` percentages. |
