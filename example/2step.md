### **Prompt for Specification: `002-backend-core-features`**

**Objective:**
Generate a complete feature specification (`spec.md`) for the core Task and Tag management APIs of the Todo App. This specification will serve as the blueprint for implementing all Basic (P1) and Intermediate (P2) backend features. The specification must strictly adhere to the project constitution (`.specify/memory/constitution.md`) and assume that the "Foundational Backend Setup" (`001-foundational-backend`) is complete.

**File to Create:**
`/specs/002-backend-core-features/spec.md`

**Required Specification Sections:**

1.  **Overview:**
    *   State that this specification covers the RESTful API endpoints for creating, reading, updating, and deleting Tasks and Tags, including advanced filtering, sorting, and association logic.
    *   Note that all endpoints described here **MUST** be protected by the authentication dependency created in the foundational setup.

2.  **Task Management API (P1 Features):**
    *   Define the following RESTful endpoints for Tasks. For each, specify the `Method`, `Path`, `Request Body`, `Success Response`, and `Error Responses`.
    *   **Create Task:** `POST /api/v1/tasks`
    *   **List Tasks:** `GET /api/v1/tasks` (This endpoint will be detailed further in a separate section).
    *   **Get Single Task:** `GET /api/v1/tasks/{task_id}`
    *   **Update Task:** `PUT /api/v1/tasks/{task_id}` (for full updates).
    *   **Partially Update Task:** `PATCH /api/v1/tasks/{task_id}` (for partial updates, e.g., marking a task complete).
    *   **Delete Task:** `DELETE /api/v1/tasks/{task_id}`

3.  **Tag Management API (P2 Features):**
    *   Define the following RESTful endpoints for Tags.
    *   **Create Tag:** `POST /api/v1/tags`
    *   **List Tags:** `GET /api/v1/tags`
    *   **Update Tag:** `PUT /api/v1/tags/{tag_id}`
    *   **Delete Tag:** `DELETE /api/v1/tags/{tag_id}`

4.  **Task-Tag Association API (P2 Features):**
    *   Define endpoints for managing the many-to-many relationship between tasks and tags.
    *   **Associate Tag with Task:** `POST /api/v1/tasks/{task_id}/tags/{tag_id}`
    *   **Dissociate Tag from Task:** `DELETE /api/v1/tasks/{task_id}/tags/{tag_id}`
    *   Specify error handling for cases where the task or tag does not exist or does not belong to the authenticated user.

5.  **Enhanced Task Listing Requirements (P2 Features):**
    *   This section must detail the full functionality of the `GET /api/v1/tasks` endpoint.
    *   Mandate support for all query parameters defined in the constitution:
        *   `page` & `limit` for pagination.
        *   `q` for full-text search on the `title` and `description` fields.
        *   `status` for filtering by `completed`, `pending`, or `all`.
        *   `priority` for filtering by `low`, `medium`, or `high`.
        *   `tag` for filtering tasks by a specific tag name or ID.
        *   `sort` for ordering results by `due_date`, `priority`, `created_at`, or `title`, including descending order (e.g., `-created_at`).
    *   The success response for this endpoint **MUST** follow the standardized pagination format defined in the constitution.

6.  **Non-Functional & Security Requirements:**
    *   **Data Isolation:** Reiterate that every single endpoint **MUST** enforce data isolation. A user must only be able to interact with their own tasks and tags. Attempts to access another user's resources must result in a `404 Not Found` or `403 Forbidden` error.
    *   **Business Logic:** All business logic must be placed in a dedicated `services` layer, separate from the API router handlers.
    *   **Validation:** All incoming data must be validated against the Pydantic schemas and validation rules defined in the constitution.

7.  **Acceptance Criteria:**
    *   A user can perform full CRUD operations on their own tasks and tags.
    *   A user receives a `404 Not Found` (or `403 Forbidden`) error when attempting to access, update, or delete resources belonging to another user.
    *   The `GET /tasks` endpoint correctly filters, sorts, paginates, and searches the user's tasks based on all specified query parameter combinations.
    *   A user can successfully add tags to their tasks and remove them.
    *   All API responses and error formats match the definitions in the constitution.
