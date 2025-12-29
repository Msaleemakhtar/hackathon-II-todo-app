# Feature Specification: Advanced Task Management Foundation

**Feature Branch**: `001-foundation-api`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Feature 001: Foundation + API Layer - Database Schema Evolution with advanced task fields (priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector) and 3 new tables (categories, tags_phasev, task_tags junction). Includes 17 MCP tools (5 enhanced + 12 new) for managing tasks with priorities, categories, tags, due dates, and recurring rules. Full-text search with PostgreSQL tsvector + GIN indexes. Part of Phase V event-driven architecture foundation."

## User Scenarios & Testing

### User Story 1 - Task Prioritization (Priority: P1)

As a busy professional, I need to assign priority levels to my tasks so I can focus on what's most urgent and important without wasting time manually sorting through all my tasks.

**Why this priority**: Priority management is the most fundamental organizational capability. Without it, users can't effectively triage their workload, which is the core value proposition of advanced task management.

**Independent Test**: Can be fully tested by creating tasks with different priorities (low, medium, high, urgent) and verifying that tasks display their priority correctly. Delivers immediate value by letting users visually distinguish critical tasks.

**Acceptance Scenarios**:

1. **Given** I'm creating a new task, **When** I set the priority to "urgent", **Then** the task is saved with urgent priority and displays prominently
2. **Given** I have an existing task with "medium" priority, **When** I change it to "high" priority, **Then** the task priority updates successfully
3. **Given** I'm viewing my task list, **When** I filter by "high" priority tasks, **Then** only high-priority tasks appear
4. **Given** I try to set an invalid priority value, **When** I save the task, **Then** I receive a clear validation error message

---

### User Story 2 - Category Organization (Priority: P1)

As a user managing multiple projects and life areas, I want to create custom categories (like "Work", "Personal", "Health") to organize my tasks into meaningful groups that reflect how I think about my responsibilities.

**Why this priority**: Categories provide the primary organizational structure for task management. This is tied for P1 because it's equally fundamental - users need to separate different contexts/projects.

**Independent Test**: Can be fully tested by creating categories, assigning tasks to them, and filtering by category. Delivers immediate organizational value independent of other features.

**Acceptance Scenarios**:

1. **Given** I want to organize my tasks, **When** I create a category named "Work Projects" with a blue color, **Then** the category is saved and available for task assignment
2. **Given** I have a task without a category, **When** I assign it to my "Personal" category, **Then** the task shows the category label and color
3. **Given** I have tasks in a category called "Q1 Goals", **When** I filter by this category, **Then** only tasks from "Q1 Goals" appear
4. **Given** I delete a category that has tasks assigned to it, **When** the deletion completes, **Then** those tasks remain but show no category
5. **Given** I try to create a category with the same name as an existing one, **When** I save it, **Then** I receive an error message about duplicate names

---

### User Story 3 - Flexible Tagging (Priority: P2)

As a knowledge worker with tasks that span multiple contexts, I want to apply multiple tags (like #urgent, #meeting, #client-facing) to each task so I can categorize tasks along different dimensions and find them through multiple lenses.

**Why this priority**: While categories provide one-dimensional organization, tags enable cross-cutting organization. This is P2 because it enhances organization but users can function with just categories.

**Independent Test**: Can be fully tested by creating tags, applying multiple tags to tasks, and filtering by tag combinations. Delivers cross-categorical search capabilities.

**Acceptance Scenarios**:

1. **Given** I need flexible task labeling, **When** I create tags like "#urgent", "#meeting", "#client-project", **Then** these tags are available for task assignment
2. **Given** I have a task, **When** I apply multiple tags like "#urgent" and "#meeting", **Then** both tags appear on the task
3. **Given** I'm viewing my tasks, **When** I filter by the "#urgent" tag, **Then** all tasks with that tag appear regardless of their category
4. **Given** I have a tag applied to 20 tasks, **When** I delete that tag, **Then** it's removed from all those tasks without deleting the tasks themselves
5. **Given** I try to add an 11th tag to a task, **When** I save, **Then** I receive a validation error about the 10-tag limit

---

### User Story 4 - Due Date Management (Priority: P2)

As someone with time-sensitive responsibilities, I want to set due dates on my tasks so I can plan ahead and ensure I complete work before deadlines.

**Why this priority**: Temporal planning is critical for time management, but users can start using the system effectively without it. It's P2 because it adds significant value but isn't blocking basic organization.

**Independent Test**: Can be fully tested by setting due dates, viewing tasks sorted by due date, and filtering by date ranges. Delivers time-based task management.

**Acceptance Scenarios**:

1. **Given** I have a task, **When** I set a due date to "2025-01-15 17:00", **Then** the task shows this deadline clearly
2. **Given** I'm viewing my tasks, **When** I filter to show only tasks due this week, **Then** only tasks with due dates in the current week appear
3. **Given** I have a task with a due date in the past, **When** I view it, **Then** it displays as overdue with appropriate visual indicators
4. **Given** I set a due date, **When** I later remove it, **Then** the task no longer has a deadline

---

### User Story 5 - Keyword Search (Priority: P2)

As a user with many tasks, I want to search for tasks by typing keywords so I can quickly find specific tasks without scrolling through long lists or remembering exact categorization.

**Why this priority**: Search becomes critical as task volume grows, but it's not needed for initial adoption. It's P2 because it enhances discoverability significantly but users can navigate via categories/tags initially.

**Independent Test**: Can be fully tested by creating tasks with various titles/descriptions and searching for keywords. Delivers fast task retrieval.

**Acceptance Scenarios**:

1. **Given** I have many tasks, **When** I search for "project proposal", **Then** all tasks with those words in title or description appear, ranked by relevance
2. **Given** I search with empty keywords, **When** results load, **Then** all my tasks appear (no filtering applied)
3. **Given** I search for a keyword that doesn't match any tasks, **When** results load, **Then** I see an empty list with a helpful "no results" message
4. **Given** I search for "urgent meeting", **When** results appear, **Then** tasks with both words rank higher than tasks with only one word

---

### User Story 6 - Recurring Task Setup (Priority: P3)

As someone with routine responsibilities, I want to create tasks that automatically repeat on a schedule (daily, weekly, monthly) so I don't have to manually recreate routine tasks like "Submit weekly report" or "Review monthly metrics".

**Why this priority**: Recurring tasks are valuable for workflow automation but require other features to be in place first. It's P3 because it's a quality-of-life enhancement that builds on the foundation.

**Independent Test**: Can be fully tested by creating a task with a recurrence rule and verifying the rule is stored correctly. Full automation testing happens in later features, but validation works independently.

**Acceptance Scenarios**:

1. **Given** I create a task "Weekly team meeting", **When** I set it to recur "Every Monday", **Then** the task is saved with the recurrence rule
2. **Given** I have a recurring task, **When** I view it, **Then** it clearly indicates the recurrence pattern (e.g., "Repeats weekly on Monday")
3. **Given** I create a recurring task without a due date, **When** I save it, **Then** I receive a warning that recurrence works best with a due date
4. **Given** I have a recurring task "Daily standup", **When** I remove the recurrence rule, **Then** it becomes a one-time task

---

### Edge Cases

- **What happens when multiple filters are applied simultaneously?** System uses OR logic - e.g., filtering by "high priority" + "Work category" + "#urgent tag" returns all tasks that match ANY of these criteria (union of results).
- **How do search and filters interact when combined?** Search and filters use AND logic - e.g., searching for "proposal" while filtering by "Work category" OR "#urgent tag" returns only tasks containing "proposal" that are ALSO either in Work category or have #urgent tag.
- **What happens if creating a task with multiple tags fails partway through?** The entire operation is rolled back atomically - if assigning the 3rd of 5 tags fails, the task itself is not created and no tags are assigned. The API returns a clear error message.
- **What happens when a user reaches the 50-category limit?** System prevents creating additional categories and shows a clear message: "Maximum 50 categories reached. Delete unused categories to create new ones."
- **How does the system handle duplicate category/tag names?** System shows a validation error: "A category/tag with this name already exists. Please choose a different name."
- **What happens when a user assigns a task to a category that gets deleted by another concurrent session?** Task saves successfully with category_id set to null (graceful degradation).
- **How does search handle special characters like @ # $ ?** Special characters are automatically sanitized and treated as search keywords.
- **What happens if a user sets a priority outside the valid enum?** System rejects the save with error: "Priority must be one of: low, medium, high, urgent."
- **How does the system handle invalid recurrence rules?** System validates on save and shows error: "Invalid recurrence pattern. Examples: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,WE,FR"
- **What happens to task data if a user rolls back the database schema?** All new fields (priority, due_date, etc.) and all categories/tags are lost. Only basic task data (title, description, completed) is preserved.
- **How does search relevance work when keywords appear in both title and description?** Title matches are weighted higher and appear first in search results.

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to assign priority levels (low, medium, high, urgent) to tasks with "medium" as the default
- **FR-002**: System MUST allow users to create custom categories with a unique name (1-50 characters) and optional color (hex format)
- **FR-003**: System MUST enforce a maximum of 50 categories per user
- **FR-004**: Users MUST be able to create custom tags with a unique name (1-30 characters) and optional color
- **FR-005**: System MUST enforce a maximum of 100 tags per user and 10 tags per task
- **FR-006**: Users MUST be able to assign multiple tags to a single task
- **FR-007**: Users MUST be able to set optional due dates on tasks with date and time precision (stored as UTC; clients send/receive ISO 8601 with timezone)
- **FR-008**: System MUST allow users to define recurrence rules for tasks using standard calendar recurrence patterns (storage and validation only; instance generation is out of scope)
- **FR-009**: System MUST provide full-text keyword search across task titles and descriptions with relevance ranking
- **FR-010**: System MUST maintain data isolation - users can only see their own categories, tags, and tasks
- **FR-011**: System MUST enforce unique category names per user (case-sensitive)
- **FR-012**: System MUST enforce unique tag names per user (case-sensitive)
- **FR-013**: System MUST validate priority values and reject invalid entries
- **FR-014**: System MUST validate recurrence rule format and reject invalid patterns
- **FR-015**: System MUST validate color codes as 6-character hex format (e.g., #FF5733) or allow empty/null
- **FR-016**: When a category is deleted, system MUST preserve associated tasks by removing the category assignment (set to null)
- **FR-017**: When a tag is deleted, system MUST remove the tag from all associated tasks without deleting the tasks
- **FR-018**: System MUST prevent duplicate tag assignments (assigning the same tag twice to a task is idempotent)
- **FR-019**: System MUST preserve existing task data during data schema evolution (zero data loss requirement)
- **FR-020**: System MUST support rollback of data schema changes with documented data loss impact
- **FR-021**: When multiple filters are applied (priority, category, tags, due date), system MUST return tasks matching ANY of the filter criteria (OR logic)
- **FR-022**: System MUST allow combining keyword search with filters using AND logic (search results are filtered, returning only tasks that match search keywords AND at least one filter criterion)
- **FR-023**: All multi-table operations (e.g., create task with tags, delete category/tag) MUST be atomic transactions - either all changes succeed or all changes rollback on any failure

### Key Entities

- **Task**: Represents a to-do item with title, description, completion status, priority level, optional due date, optional category assignment, optional recurrence pattern, and optional tag assignments. Each task belongs to exactly one user.

- **Category**: Represents a user-defined organizational bucket (e.g., "Work", "Personal", "Health"). Has a unique name per user, optional display color, and creation timestamp. Tasks can optionally belong to one category.

- **Tag**: Represents a flexible label for cross-categorical organization (e.g., "#urgent", "#meeting", "#client-facing"). Has a unique name per user, optional display color, and creation timestamp. Tasks can have multiple tags (0-10).

- **Task-Tag Association**: Represents the many-to-many relationship between tasks and tags, allowing a task to have multiple tags and a tag to apply to multiple tasks.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create and assign priorities to tasks in under 10 seconds
- **SC-002**: Users can create categories and organize tasks into them in under 15 seconds
- **SC-003**: Users can create tags and apply multiple tags to tasks in under 20 seconds
- **SC-004**: Users can search and find relevant tasks using keywords in under 3 seconds (95% of searches)
- **SC-005**: System handles 10,000 tasks per user without performance degradation
- **SC-006**: Search returns results ranked by relevance (title matches appear before description matches)
- **SC-007**: 90% of users successfully complete priority assignment on first attempt
- **SC-008**: Task organization features (categories, tags) reduce time to find specific tasks by 60% compared to unorganized lists
- **SC-009**: Zero data loss during schema evolution - all existing tasks remain accessible
- **SC-010**: System maintains query response times under 200 milliseconds for filtered task lists (95th percentile)
- **SC-011**: Full-text search completes in under 200 milliseconds for collections up to 10,000 tasks (95th percentile)
- **SC-012**: Data schema changes can be rolled back in under 30 seconds if issues arise

## Assumptions

- Users are already authenticated via the existing Better Auth system before accessing task management features
- Users have basic familiarity with task management concepts (categories, tags, due dates, priorities)
- The system operates in a web-based environment with standard internet connectivity
- Users access the system through a conversational interface (ChatKit) rather than traditional forms
- Color codes are for visual differentiation only; accessibility is handled through text labels
- Recurrence pattern validation occurs at data entry but actual recurrence generation (creating new task instances) is handled by a separate background service
- Task completion rate and user engagement metrics are tracked by analytics systems outside this feature scope
- The system supports English language for search; multi-language support is deferred to future releases
- Maximum limits (50 categories, 100 tags, 10 tags per task) are set to prevent performance degradation and ensure good user experience
- Users manage their own data; no admin/supervisor oversight or task delegation features are included
- Data retention follows standard application policies; no special compliance requirements (GDPR, HIPAA) are addressed in this feature
- Due dates are stored in UTC in the database; clients handle timezone conversion for display purposes
- Performance targets assume standard cloud infrastructure; specific hardware requirements are implementation details
- Search relevance ranking uses simple weighted scoring (title > description); advanced ML-based ranking is out of scope

## Clarifications

### Session 2025-12-30

- Q: When a user creates a recurring task (e.g., "Daily standup"), should this feature implement the logic to automatically create future task instances, or just store and validate the recurrence rule? → A: Option B - Store the recurrence rule only; validation on save; instance generation is out of scope for this feature
- Q: When a user applies multiple filters (e.g., priority + category + tags), should the system return tasks that match ALL filters (AND logic) or ANY filter (OR logic)? → A: Option B - Filters use OR logic (any condition matches)
- Q: How should the system handle timezones for due dates - store as UTC, store naive datetime, store with timezone, or use date-only? → A: Option A - Store as UTC; clients send/receive ISO 8601 with timezone; server converts to UTC for storage
- Q: Can users combine keyword search with filters (priority, category, tags) in a single query, or are search and filtering separate operations? → A: Option A - Search and filters work together (AND relationship between search and filters)
- Q: For operations involving multiple tables (e.g., create task with tags, delete category affecting tasks), should these be atomic transactions with full rollback on any failure? → A: Option A - All multi-table operations are atomic (full transaction or full rollback)

## Out of Scope

- Automatic generation of future task instances from recurrence rules (handled by separate background service in later features)
- Task sharing, collaboration, or assignment to other users
- Task dependencies or hierarchical subtasks
- File attachments or rich media in task descriptions
- Integration with external calendar applications (Google Calendar, Outlook, etc.)
- Real-time collaborative editing of shared tasks
- Advanced recurrence patterns beyond standard daily/weekly/monthly/yearly schedules
- Task templates or task duplication features
- Batch operations (bulk edit, bulk delete, bulk categorize)
- Custom priority levels beyond the four predefined ones (low, medium, high, urgent)
- Task history or audit trail of changes
- Reminders or notifications (handled by separate notification service in later features)
- Natural language date parsing (e.g., "tomorrow", "next Friday")
- Task import/export functionality
- Mobile-specific optimizations or offline mode
- Advanced search with operators (AND, OR, NOT) or filter combinations
