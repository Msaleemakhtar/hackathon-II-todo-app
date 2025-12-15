# Task Breakdown: Task Management Dashboard UI

**Feature**: Task Management Dashboard UI
**Branch**: `003-task-dashboard-ui`
**Spec**: [./spec.md](./spec.md)
**Plan**: [./plan.md](./plan.md)

This document breaks down the implementation of the Task Management Dashboard UI into a dependency-ordered series of actionable tasks.

## Implementation Strategy

The implementation will follow an incremental, MVP-first approach. We will start with foundational setup, then build out the core functionality for viewing tasks. Subsequent user stories will be implemented one by one, ensuring that each phase results in a testable, complete piece of functionality.

- **MVP Scope**: Phase 1, 2, and 3 (Setup, Foundational, and User Story 1). This will deliver a view-only dashboard.
- **Incremental Delivery**: Each subsequent phase (user story) can be developed and tested independently.

## Dependencies

The following is the recommended completion order for the user stories. Most P1 stories can be worked on in parallel after the foundation is complete. P2 stories can be started after all P1 stories are done.

1.  **US1**: View Task Dashboard (BLOCKER for almost all others)
2.  **US2**: Mark Task Complete/Incomplete
3.  **US3**: Create New Task
4.  **US4**: View Task Details
5.  **US9**: View Task Status Statistics
6.  **US5**: Search Tasks
7.  **US6**: Filter Tasks
8.  **US12**: Sort Tasks
9.  **US7**: Edit Task
10. **US8**: Delete Task
11. **US10**: Navigate Application Sections
12. **US11**: View Completed Tasks History

---

## Phase 1: Project Setup & Configuration

**Goal**: Initialize the Next.js project and configure all required tools and dependencies.

- [x] T001 Verify Next.js project is initialized in `frontend/`.
- [x] T002 [P] Install npm dependencies: `shadcn-ui`, `tailwindcss`, `zustand`, `axios`, `lucide-react`. Run `bun install`.
- [x] T003 [P] Initialize `shadcn/ui` and configure `tailwind.config.js` and `globals.css` in `frontend/`.
- [x] T004 Create directory structure in `frontend/src/`: `app`, `components`, `lib`, `hooks`, `types`, `store`.

## Phase 2: Foundational Implementation

**Goal**: Build the core layout, authentication, and data management layers.

- [x] T005 [P] Define core data types (`Task`, `Tag`, `UserProfile`) in `frontend/src/types/index.ts`.
- [x] T006 [P] Create a custom hook `useAuth` in `frontend/src/hooks/useAuth.ts` to manage user authentication state.
- [x] T007 Configure a global Zustand store for UI state in `frontend/src/store/ui-store.ts`.
- [x] T008 Implement a reusable API client with `axios` in `frontend/src/lib/api-client.ts`, including interceptors for JWT token handling and automated refresh.
- [x] T009 Create the main app layout in `frontend/src/app/layout.tsx`, including basic structure for a sidebar and main content.
- [x] T010 [P] Create a `Sidebar` component in `frontend/src/components/layout/Sidebar.tsx`.
- [x] T011 [P] Create a `Header` component in `frontend/src/components/layout/Header.tsx`.
- [x] T012 Implement a protected route mechanism that redirects unauthenticated users to a login page.

## Phase 3: User Story 1 - View Task Dashboard

**Goal**: An authenticated user can see an overview of all their tasks.
**Independent Test**: Log in as a user with existing tasks and verify the dashboard displays them correctly.

- [x] T013 [P] [US1] Create a `TaskCard.tsx` component in `frontend/src/components/tasks/` to display a single task with its title, priority, and status.
- [x] T014 [US1] Create a `TaskList.tsx` component in `frontend/src/components/tasks/` to render a list of `TaskCard` components.
- [x] T015 [US1] Implement a `useTasks` hook in `frontend/src/hooks/useTasks.ts` that fetches tasks from `GET /api/v1/tasks`.
- [x] T016 [US1] Create the main dashboard page at `frontend/src/app/dashboard/page.tsx`.
- [x] T017 [US1] Use the `useTasks` hook in the dashboard page and pass the data to the `TaskList` component.
- [x] T018 [US1] Implement the "empty state" view within `TaskList.tsx` to be shown when no tasks are returned.

## Phase 4: User Story 2 - Mark Task Complete/Incomplete

**Goal**: A user can toggle the completion status of a task.
**Independent Test**: Click the completion toggle on a task and verify its status changes visually and persists on reload.

- [x] T019 [US2] Add a checkbox or similar toggle to the `TaskCard.tsx` component.
- [x] T020 [US2] Add an `updateTaskStatus` function to the `useTasks` hook to call `PATCH /api/v1/tasks/{id}`.
- [x] T021 [US2] Implement the optimistic update logic within the `updateTaskStatus` function.
- [x] T022 [US2] Connect the `TaskCard` toggle to the `updateTaskStatus` function, disabling the control while the request is pending.

## Phase 5: User Story 3 - Create New Task

**Goal**: A user can create a new task.
**Independent Test**: Use the UI to create a task and verify it appears in the task list.

- [x] T023 [P] [US3] Create a `CreateTaskForm.tsx` component in `frontend/src/components/tasks/` with fields for title, description, priority, and due date.
- [x] T024 [P] [US3] Use a `shadcn/ui` Dialog or Sheet component to create `CreateTaskModal.tsx` which will contain the form.
- [x] T025 [US3] Add a `createTask` function to the `useTasks` hook to call `POST /api/v1/tasks`.
- [x] T026 [US3] Add a global "Add Task" button to the `Header.tsx` or `Sidebar.tsx` that opens the `CreateTaskModal`.

## Phase 6: Later User Stories (P2 & P3)

**Goal**: Implement the remaining user stories. These can largely be implemented in parallel after the P1 stories are complete.

- [x] T027 [P] [US9] Create and implement the `TaskStatusChart.tsx` component in `frontend/src/components/dashboard/`.
- [x] T028 [P] [US5] Implement search functionality in the `Header.tsx` component, updating the Zustand store and `useTasks` hook.
- [ ] T029 [P] [US6] Create and implement filter components (`StatusFilter`, `PriorityFilter`, `TagFilter`) in `frontend/src/components/filters/`.
- [ ] T030 [P] [US12] Create and implement a `SortMenu.tsx` component in `frontend/src/components/tasks/`.
- [ ] T031 [P] [US7] Create and implement the `EditTaskForm.tsx` and its modal, adding an `updateTask` function to the `useTasks` hook.
- [ ] T032 [P] [US8] Implement the delete confirmation dialog and add a `deleteTask` function to the `useTasks` hook.
- [ ] T033 [P] [US10] Add navigation links to the `Sidebar.tsx` component.
- [ ] T034 [P] [US11] Create a dedicated view for completed task history.

## Final Phase: Polish & Cross-Cutting Concerns

**Goal**: Add loading states, notifications, and perform final accessibility and responsive design checks.

- [ ] T035 [P] Implement skeleton loading states for `TaskList.tsx` while data is being fetched.
- [ ] T036 [P] Integrate a toast notification library (e.g., from `shadcn/ui`) to show success/error messages for all API operations.
- [_] T037 [P] Review and add ARIA labels to all interactive elements.
- [ ] T038 [P] Test and refine responsive behavior on mobile and tablet screen sizes.
- [ ] T039 Integrate APM tool for logging errors and performance metrics as per `FR-039`, `FR-040`, `FR-041`.
- [ ] T040 Write unit and integration tests for all new components and hooks, aiming for the coverage goals in the constitution.
