---
description: "Implementation tasks for Event-Driven Architecture feature"
---

# Tasks: Event-Driven Architecture

**Input**: Design documents from `/specs/002-event-driven/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in this feature specification. Test tasks are omitted per specification guidelines.

**Organization**: Tasks ar/.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Per plan.md, this is a web application with the following structure:
- Backend: `phaseV/backend/`
- Kubernetes: `phaseV/kubernetes/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Kafka integration structure

- [ ] T001 Install dependencies (aiokafka 0.11.0, python-dateutil 2.8.2) in phaseV/backend/pyproject.toml
- [ ] T002 [P] Create Kafka configuration module in phaseV/backend/app/kafka/config.py
- [ ] T003 [P] Create event schema definitions in phaseV/backend/app/kafka/events.py
- [ ] T004 [P] Create Kafka producer manager in phaseV/backend/app/kafka/producer.py
- [ ] T005 [P] Create RRULE validation utility in phaseV/backend/app/utils/rrule_parser.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create Alembic migration to add recurrence_rule and reminder_sent fields in phaseV/backend/alembic/versions/YYYYMMDD_add_event_driven_fields.py
- [ ] T007 Run database migration to add event-driven fields to tasks_phaseiii table
- [ ] T008 Update Task model with recurrence_rule and reminder_sent fields in phaseV/backend/app/models/task.py
- [ ] T009 Initialize Kafka producer on FastAPI startup in phaseV/backend/app/main.py
- [ ] T010 Create programmatic Kafka topic creation (task-events, task-reminders, task-recurrence) in phaseV/backend/app/kafka/producer.py
- [ ] T011 Add Kafka credentials to Kubernetes secrets (kafka-credentials secret in todo-phasev namespace)
- [ ] T012 Verify Redpanda Cloud connectivity from Kubernetes pods

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automatic Task Reminders (Priority: P1) 🎯 MVP

**Goal**: Users receive timely reminder notifications for tasks with approaching due dates

**Independent Test**: Create a task with due_date 30 minutes in the future, wait, verify reminder notification appears in logs when task is due within 1 hour

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create notification service module in phaseV/backend/app/services/notification_service.py
- [ ] T014 [P] [US1] Implement database polling logic (every 5 seconds) for tasks due within 1 hour in phaseV/backend/app/services/notification_service.py
- [ ] T015 [US1] Implement atomic reminder_sent flag update to prevent duplicates in phaseV/backend/app/services/notification_service.py
- [ ] T016 [US1] Implement reminder logging with format "🔔 REMINDER: Task '[title]' (ID: [id]) is due in [N] minutes" in phaseV/backend/app/services/notification_service.py
- [ ] T017 [US1] Publish ReminderSentEvent to task-reminders topic after sending reminder in phaseV/backend/app/services/notification_service.py
- [ ] T018 [US1] Add graceful shutdown handling (SIGTERM) for notification service in phaseV/backend/app/services/notification_service.py
- [ ] T019 [US1] Create Kubernetes deployment for notification service in phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml
- [ ] T020 [US1] Add health check endpoint for notification service (verify Kafka + DB connectivity) in phaseV/backend/app/services/notification_service.py
- [ ] T021 [US1] Start notification service loop on FastAPI startup in phaseV/backend/app/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - tasks with due dates should trigger reminder notifications

---

## Phase 4: User Story 2 - Recurring Task Automation (Priority: P1) 🎯 MVP

**Goal**: Recurring tasks automatically regenerate the next occurrence when completed

**Independent Test**: Create a task with recurrence_rule "FREQ=DAILY", complete it, verify new task created with tomorrow's due date

### Implementation for User Story 2

- [ ] T022 [P] [US2] Enhance add_task MCP tool to validate recurrence_rule against whitelist in phaseV/backend/app/mcp/tools.py
- [ ] T023 [P] [US2] Enhance add_task MCP tool to publish TaskCreatedEvent to task-events topic in phaseV/backend/app/mcp/tools.py
- [ ] T024 [P] [US2] Enhance complete_task MCP tool to publish TaskCompletedEvent to task-recurrence topic in phaseV/backend/app/mcp/tools.py
- [ ] T025 [P] [US2] Enhance update_task MCP tool to validate recurrence_rule and publish TaskUpdatedEvent in phaseV/backend/app/mcp/tools.py
- [ ] T026 [P] [US2] Enhance delete_task MCP tool to publish TaskDeletedEvent to task-events topic in phaseV/backend/app/mcp/tools.py
- [ ] T027 [US2] Create recurring task service module in phaseV/backend/app/services/recurring_task_service.py
- [ ] T028 [US2] Implement Kafka consumer for task-recurrence topic in phaseV/backend/app/services/recurring_task_service.py
- [ ] T029 [US2] Implement RRULE parsing with dateutil.rrule in phaseV/backend/app/services/recurring_task_service.py
- [ ] T030 [US2] Implement next occurrence calculation logic in phaseV/backend/app/services/recurring_task_service.py
- [ ] T031 [US2] Implement new recurring task creation (copy title, description, priority, category, tags, recurrence_rule) in phaseV/backend/app/services/recurring_task_service.py
- [ ] T032 [US2] Handle invalid RRULE formats (log error, skip event, continue processing) in phaseV/backend/app/services/recurring_task_service.py
- [ ] T033 [US2] Skip regeneration if next occurrence is in the past in phaseV/backend/app/services/recurring_task_service.py
- [ ] T034 [US2] Publish TaskCreatedEvent for new recurring task instance in phaseV/backend/app/services/recurring_task_service.py
- [ ] T035 [US2] Implement manual offset commit after successful processing in phaseV/backend/app/services/recurring_task_service.py
- [ ] T036 [US2] Add graceful shutdown handling (SIGTERM) for recurring task service in phaseV/backend/app/services/recurring_task_service.py
- [ ] T037 [US2] Create Kubernetes deployment for recurring task service in phaseV/kubernetes/helm/todo-app/templates/recurring-deployment.yaml
- [ ] T038 [US2] Add health check endpoint for recurring task service (verify Kafka + DB connectivity) in phaseV/backend/app/services/recurring_task_service.py
- [ ] T039 [US2] Start recurring task service loop on FastAPI startup in phaseV/backend/app/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - reminders work AND recurring tasks regenerate on completion

---

## Phase 5: User Story 3 - Fast Task Search (Priority: P2)

**Goal**: Users can quickly find tasks by searching keywords in titles/descriptions with ranked results

**Independent Test**: Create 100 tasks with varied titles/descriptions, execute search query "project meeting", verify relevant tasks appear in ranked order within 200ms

### Implementation for User Story 3

- [ ] T040 [P] [US3] Create search service module in phaseV/backend/app/services/search_service.py
- [ ] T041 [US3] Implement full-text search query using PostgreSQL tsvector and plainto_tsquery in phaseV/backend/app/services/search_service.py
- [ ] T042 [US3] Implement result ranking with ts_rank (title matches weighted higher) in phaseV/backend/app/services/search_service.py
- [ ] T043 [US3] Implement empty query handling (return all tasks) in phaseV/backend/app/services/search_service.py
- [ ] T044 [US3] Implement no-match handling (return empty array) in phaseV/backend/app/services/search_service.py
- [ ] T045 [US3] Implement query length validation (reject queries >500 characters) in phaseV/backend/app/services/search_service.py
- [ ] T046 [US3] Create search_tasks MCP tool in phaseV/backend/app/mcp/tools.py
- [ ] T047 [US3] Add result limit (50 tasks) for performance in phaseV/backend/app/services/search_service.py

**Checkpoint**: All high-priority user stories (US1, US2, US3) should now be independently functional

---

## Phase 6: User Story 4 - Event-Driven System Reliability (Priority: P3)

**Goal**: System processes task operations asynchronously through Kafka, ensuring downstream services operate independently without blocking user interactions

**Independent Test**: Create task with due_date and recurrence_rule, verify MCP tool returns success immediately (synchronous), confirm events published to Kafka and consumed by services (asynchronous)

### Implementation for User Story 4

- [ ] T048 [P] [US4] Implement fire-and-forget event publishing in Kafka producer (log failures, don't block) in phaseV/backend/app/kafka/producer.py
- [ ] T049 [P] [US4] Configure Kafka producer with acks=1 and enable_idempotence=true in phaseV/backend/app/kafka/config.py
- [ ] T050 [P] [US4] Implement automatic Kafka reconnection on connection failure (within 5 seconds) in phaseV/backend/app/kafka/producer.py
- [ ] T051 [P] [US4] Add exponential backoff retry logic for database connection failures in notification service in phaseV/backend/app/services/notification_service.py
- [ ] T052 [P] [US4] Add exponential backoff retry logic for database connection failures in recurring task service in phaseV/backend/app/services/recurring_task_service.py
- [ ] T053 [US4] Implement idempotent event processing in notification service (atomic database update check) in phaseV/backend/app/services/notification_service.py
- [ ] T054 [US4] Implement idempotent event processing in recurring task service (duplicate detection) in phaseV/backend/app/services/recurring_task_service.py
- [ ] T055 [US4] Use task_id as Kafka partition key when publishing events in phaseV/backend/app/kafka/producer.py
- [ ] T056 [US4] Configure consumer group IDs (notification-service-group, recurring-task-service-group) in phaseV/backend/app/services/notification_service.py and recurring_task_service.py
- [ ] T057 [US4] Update backend deployment with Kafka environment variables in phaseV/kubernetes/helm/todo-app/templates/backend-deployment.yaml
- [ ] T058 [US4] Update Helm values.yaml with Kafka configuration in phaseV/kubernetes/helm/todo-app/values.yaml

**Checkpoint**: All user stories (US1, US2, US3, US4) should now be fully functional with robust event-driven infrastructure

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T059 [P] Add comprehensive error logging for Kafka publish failures across all MCP tools
- [ ] T060 [P] Add performance monitoring for event publishing latency (<50ms p95 target)
- [ ] T061 [P] Add performance monitoring for search queries (<200ms p95 target)
- [ ] T062 [P] Add performance monitoring for reminder processing (<200ms p95 target)
- [ ] T063 [P] Add performance monitoring for recurring task processing (<200ms p95 target)
- [ ] T064 Update phaseV/README.md with event-driven architecture documentation
- [ ] T065 Verify composite index idx_tasks_reminder_query is used by reminder query (EXPLAIN ANALYZE)
- [ ] T066 Verify GIN index idx_tasks_search is used by search query (EXPLAIN ANALYZE)
- [ ] T067 Run quickstart.md validation to ensure all steps work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Reminders)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - Recurring)**: Can start after Foundational (Phase 2) - Integrates with event publishing but independently testable
- **User Story 3 (P2 - Search)**: Can start after Foundational (Phase 2) - No dependencies on other stories (read-only, no events)
- **User Story 4 (P3 - Reliability)**: Can start after Foundational (Phase 2) - Enhances existing event infrastructure

### Within Each User Story

**User Story 1 (Reminders)**:
- T013, T014 can run in parallel (different concerns)
- T015 depends on T014 (adds to polling logic)
- T016, T017 depend on T015 (reminder flow completion)
- T018 can be done in parallel with T016-T017
- T019 depends on notification service implementation (T013-T018)
- T020 can be done in parallel with T019
- T021 depends on T019, T020 (deployment ready)

**User Story 2 (Recurring)**:
- T022-T026 can all run in parallel (different MCP tools)
- T027-T036 must be sequential (recurring service implementation flow)
- T037, T038 depend on recurring service implementation (T027-T036)
- T039 depends on T037, T038 (deployment ready)

**User Story 3 (Search)**:
- T040, T041 sequential (service module then implementation)
- T042-T045 can run in parallel (different search features)
- T046 depends on T040-T045 (service complete)
- T047 can be done in parallel with T046

**User Story 4 (Reliability)**:
- T048-T050 can run in parallel (Kafka producer enhancements)
- T051, T052 can run in parallel (service-specific retry logic)
- T053, T054 can run in parallel (service-specific idempotency)
- T055 can be done with T048 (producer enhancement)
- T056 can run in parallel with T053, T054
- T057, T058 can run in parallel (Kubernetes configuration)

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T004, T005 can all run in parallel
- **Phase 3 (US1)**: T013, T014 parallel; T016, T017, T018 parallel after T015
- **Phase 4 (US2)**: T022-T026 parallel (MCP tools); T037, T038 parallel (K8s)
- **Phase 5 (US3)**: T042-T045 parallel (search features)
- **Phase 6 (US4)**: T048-T050 parallel; T051-T052 parallel; T053-T054 parallel; T057-T058 parallel
- **Phase 7 (Polish)**: T059-T063 parallel (monitoring); T065, T066 parallel (index verification)
- **Cross-Story Parallelism**: After Phase 2, US1, US2, US3, US4 can all be worked on in parallel by different developers

---

## Parallel Example: User Story 1 (Reminders)

```bash
# After Phase 2 completes, launch notification service implementation in parallel:
Task T013: "Create notification service module in phaseV/backend/app/services/notification_service.py"
Task T014: "Implement database polling logic in phaseV/backend/app/services/notification_service.py"

# After T015 completes, launch reminder flow tasks in parallel:
Task T016: "Implement reminder logging in phaseV/backend/app/services/notification_service.py"
Task T017: "Publish ReminderSentEvent in phaseV/backend/app/services/notification_service.py"
Task T018: "Add graceful shutdown handling in phaseV/backend/app/services/notification_service.py"
```

---

## Parallel Example: User Story 2 (Recurring Tasks)

```bash
# Launch all MCP tool enhancements in parallel:
Task T022: "Enhance add_task to validate recurrence_rule in phaseV/backend/app/mcp/tools.py"
Task T023: "Enhance add_task to publish TaskCreatedEvent in phaseV/backend/app/mcp/tools.py"
Task T024: "Enhance complete_task to publish TaskCompletedEvent in phaseV/backend/app/mcp/tools.py"
Task T025: "Enhance update_task to validate and publish in phaseV/backend/app/mcp/tools.py"
Task T026: "Enhance delete_task to publish TaskDeletedEvent in phaseV/backend/app/mcp/tools.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Reminders)
4. Complete Phase 4: User Story 2 (Recurring Tasks)
5. **STOP and VALIDATE**: Test both US1 and US2 independently
6. Deploy/demo if ready (core event-driven features working)

### Incremental Delivery

1. Complete Setup + Foundational → Kafka infrastructure ready
2. Add User Story 1 (Reminders) → Test independently → Deploy/Demo (MVP Part 1!)
3. Add User Story 2 (Recurring) → Test independently → Deploy/Demo (MVP Part 2!)
4. Add User Story 3 (Search) → Test independently → Deploy/Demo (Enhanced features)
5. Add User Story 4 (Reliability) → Test independently → Deploy/Demo (Production-ready)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Reminders) - T013-T021
   - Developer B: User Story 2 (Recurring) - T022-T039
   - Developer C: User Story 3 (Search) - T040-T047
   - Developer D: User Story 4 (Reliability) - T048-T058
3. Stories complete and integrate independently

---

## Summary

**Total Tasks**: 67 tasks

**Task Count per User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 7 tasks
- User Story 1 - Reminders (P1): 9 tasks
- User Story 2 - Recurring (P1): 18 tasks
- User Story 3 - Search (P2): 8 tasks
- User Story 4 - Reliability (P3): 11 tasks
- Polish (Phase 7): 9 tasks

**Parallel Opportunities Identified**:
- Phase 1: 4 parallel tasks (T002-T005)
- Phase 3 (US1): 2 sets of parallel tasks
- Phase 4 (US2): 2 sets of parallel tasks (MCP tools, K8s)
- Phase 5 (US3): 1 set of parallel tasks (search features)
- Phase 6 (US4): 4 sets of parallel tasks (producer, retries, idempotency, K8s)
- Phase 7: 2 sets of parallel tasks (monitoring, indexes)
- Cross-story: All 4 user stories can be developed in parallel after Foundational phase

**Independent Test Criteria**:
- US1: Create task with due_date 30min future → verify reminder logs appear
- US2: Create task with FREQ=DAILY → complete it → verify new task with tomorrow's due_date created
- US3: Create 100 tasks → search "project meeting" → verify ranked results in <200ms
- US4: Create task with due_date+recurrence → verify immediate MCP response + async Kafka events

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)
- Rationale: Both US1 and US2 are P1 priority and represent the core event-driven features (reminders and recurring tasks)

---

## Notes

- [P] tasks = different files/concerns, no dependencies within same phase
- [Story] label maps task to specific user story (US1, US2, US3, US4) for traceability
- Each user story should be independently completable and testable
- Tests are NOT included as they were not explicitly requested in the specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Format validation: ALL tasks follow checklist format (checkbox, ID, optional [P], [Story] for user story phases, description with file path)
