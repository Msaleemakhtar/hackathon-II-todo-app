# Feature Specification: Event-Driven Architecture

**Feature Branch**: `002-event-driven`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Event-Driven Architecture with Kafka integration, consumer services, and search"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Task Reminders (Priority: P1)

A user creates a task with a due date and expects to receive timely reminders as the deadline approaches, helping them stay on track without manually checking their task list.

**Why this priority**: This is the most critical user-facing feature - reminders directly improve task completion rates and user engagement. Users can immediately see value from automated notifications.

**Independent Test**: Can be fully tested by creating a task with a due date 30 minutes in the future, waiting, and verifying that a reminder notification appears in the logs when the task is due within the reminder window (1 hour). Delivers immediate value: users get reminded about upcoming tasks.

**Acceptance Scenarios**:

1. **Given** a user has created a task with a due date 30 minutes from now, **When** the system checks for tasks needing reminders (every 5 seconds), **Then** the system logs a reminder notification and marks the task's reminder_sent flag as true.

2. **Given** a user has multiple tasks with due dates approaching, **When** the reminder service polls the database, **Then** reminders are sent for all tasks due within the next hour that haven't already been reminded.

3. **Given** a task's reminder has already been sent (reminder_sent = true), **When** the reminder service polls again, **Then** no duplicate reminder is sent for that task.

4. **Given** a task is completed before its reminder time, **When** the reminder service polls, **Then** no reminder is sent for the completed task.

---

### User Story 2 - Recurring Task Automation (Priority: P1)

A user creates a recurring task (e.g., "Daily standup meeting" or "Weekly report") with a recurrence rule, and when they complete it, the system automatically creates a new instance for the next occurrence without manual intervention.

**Why this priority**: Recurring tasks eliminate repetitive manual work and are essential for users with routine responsibilities. This is a core productivity feature that differentiates advanced task management from basic to-do lists.

**Independent Test**: Can be fully tested by creating a task with recurrence_rule "FREQ=DAILY", completing it, and verifying that a new task with the same properties but tomorrow's due date is automatically created. Delivers standalone value: automates routine task recreation.

**Acceptance Scenarios**:

1. **Given** a user completes a task with recurrence_rule "FREQ=DAILY" and due_date "2025-01-10", **When** the recurring task service processes the completion event, **Then** a new task is created with the same title, description, priority, and category, but with due_date "2025-01-11".

2. **Given** a user completes a weekly recurring task (FREQ=WEEKLY;BYDAY=MO) on a Monday, **When** the service calculates the next occurrence, **Then** a new task is created for the following Monday.

3. **Given** a user completes a monthly recurring task (FREQ=MONTHLY;BYMONTHDAY=15) on the 15th, **When** the service processes it, **Then** a new task is created for the 15th of the next month.

4. **Given** a recurring task has no future occurrences (e.g., COUNT=1 in RRULE), **When** the user completes it, **Then** no new task is created and the recurrence stops.

---

### User Story 3 - Fast Task Search (Priority: P2)

A user with hundreds of tasks needs to quickly find specific tasks by searching for keywords in titles or descriptions, getting relevant results ranked by relevance without scrolling through their entire task list.

**Why this priority**: Search becomes critical as task count grows, but it's not needed for users with few tasks. It's a scaling feature that improves usability for power users.

**Independent Test**: Can be fully tested by creating 100 tasks with varied titles/descriptions, executing a search query like "project meeting", and verifying that relevant tasks appear in ranked order within 200ms. Delivers standalone value: fast task discovery.

**Acceptance Scenarios**:

1. **Given** a user has tasks titled "Project kickoff meeting" and "Submit project report", **When** they search for "project", **Then** both tasks appear in the results, ranked by relevance (title matches ranked higher).

2. **Given** a user searches for "buy groceries", **When** the search executes, **Then** tasks with "buy", "groceries", "buying groceries" in title or description are returned, even with different word forms.

3. **Given** a user searches with an empty query, **When** the search executes, **Then** all tasks are returned (no filter applied).

4. **Given** a user searches for a term with no matches, **When** the search executes, **Then** an empty result set is returned without errors.

---

### User Story 4 - Event-Driven System Reliability (Priority: P3)

The system processes task operations (create, update, complete, delete) asynchronously through an event streaming platform, ensuring that downstream services (reminders, recurrence) can operate independently without blocking user interactions.

**Why this priority**: This is infrastructure that enables P1 and P2 features. Users don't directly interact with events, but they benefit from improved system responsiveness and reliability.

**Independent Test**: Can be tested by creating a task with due_date and recurrence_rule, verifying that the MCP tool returns success immediately (synchronous), and then confirming that events are published to Kafka topics and consumed by notification/recurring services (asynchronous). Delivers value: system scalability and resilience.

**Acceptance Scenarios**:

1. **Given** a user creates a new task via MCP tool, **When** the task is saved to the database, **Then** the user receives an immediate success response AND a TaskCreatedEvent is published to the task-events Kafka topic asynchronously.

2. **Given** a user completes a task, **When** the completion is processed, **Then** the user receives immediate confirmation AND a TaskCompletedEvent is published to the task-recurrence topic for processing.

3. **Given** the Kafka broker is temporarily unavailable, **When** a user creates a task, **Then** the task is saved to the database and the user receives success, but event publishing fails gracefully without blocking the response.

4. **Given** the notification service is down, **When** tasks are created with due dates, **Then** events are stored in Kafka and will be processed when the service recovers (at-least-once delivery).

---

### Edge Cases

- **What happens when a task is deleted between the time a reminder is queried and when it's sent?**
  - The reminder service should skip silently (task not found) without errors.

- **What happens when a user completes a recurring task multiple times in rapid succession (duplicate events)?**
  - Each completion event creates a new recurring task instance. The service processes each event idempotently (duplicate events = duplicate new tasks, which users can delete if undesired).

- **How does the system handle invalid RRULE formats in recurring tasks?**
  - The recurring task service should log an error, skip the event, and optionally move it to a dead-letter queue for manual review. No new task is created.

- **What happens when the reminder service has multiple replicas running (risk of duplicate reminders)?**
  - Use atomic database update (`UPDATE ... WHERE reminder_sent = false AND id = ?`) to ensure only one replica sends the reminder. For MVP, deploy with 1 replica to avoid this complexity.

- **How does the system handle very large numbers of tasks (10,000+) when querying for reminders?**
  - Database indexes on `due_date` and `reminder_sent` ensure query performance stays under 200ms p95. Limit query to tasks due within next hour (bounded result set).

- **What happens when a recurring task's next occurrence is in the past (task completed months late)?**
  - The recurring task service should skip creating a new task if the calculated next occurrence is before the current time.

- **How does the system handle special characters or very long search queries?**
  - PostgreSQL `plainto_tsquery` sanitizes special characters automatically. Queries over 500 characters are rejected with a validation error.

- **What happens when the search_vector column is not populated for old tasks (created before Feature 001 migration)?**
  - The database trigger automatically populates `search_vector` on the next UPDATE. Old tasks may not appear in search results until updated.

## Clarifications

### Session 2026-01-01

- Q: How should the system determine the Kafka partition key when publishing events? → A: Use task_id as partition key (ensures all events for a task go to same partition, guarantees ordering per task)
- Q: What offset commit strategy should Kafka consumer services use? → A: Commit after each successfully processed message (safest, minimal duplicates, slight performance overhead)
- Q: How should the system validate recurrence_rule values when users create tasks? → A: Validate against allowed patterns whitelist (safest, prevents unsupported RRULEs, requires maintaining pattern list)
- Q: What should the health check endpoints verify before returning success (200 OK)? → A: Check both Kafka consumer connectivity and database connection pool (comprehensive, catches real failures)
- Q: How should Kafka topics be created and configured? → A: Create topics programmatically in service startup code using AdminClient (automated, but requires admin credentials in pods)

## Requirements *(mandatory)*

### Functional Requirements

**Event Streaming Infrastructure**:

- **FR-001**: System MUST integrate with a managed Kafka cluster (Redpanda Cloud) for event streaming with SASL/SCRAM authentication and TLS encryption.

- **FR-002**: System MUST create and maintain three Kafka topics programmatically via AdminClient during service startup:
  - `task-events` (3 partitions, 7 days retention) for task lifecycle events
  - `task-reminders` (1 partition, 1 day retention) for reminder notifications
  - `task-recurrence` (1 partition, 7 days retention) for recurring task regeneration

- **FR-003**: System MUST publish events to Kafka asynchronously from MCP tools without blocking user responses (fire-and-forget pattern with error logging).

- **FR-003a**: System MUST use task_id as the Kafka partition key when publishing events to ensure all events for the same task are processed in order within the same partition.

- **FR-004**: System MUST use Pydantic schemas to validate all event payloads before publishing, ensuring type safety and schema consistency.

- **FR-005**: System MUST implement at-least-once delivery semantics with producer acknowledgments (acks=1) and idempotent producers (enable_idempotence=true).

**Event Types and Schemas**:

- **FR-006**: System MUST publish a TaskCreatedEvent when a new task is created via the `add_task` MCP tool, containing: event_id (UUID), event_type, timestamp (UTC), user_id, task_id, title, priority, due_date, recurrence_rule, category_id, tag_ids.

- **FR-007**: System MUST publish a TaskCompletedEvent when a task is marked complete via the `complete_task` MCP tool, containing: event_id, event_type, timestamp, user_id, task_id, recurrence_rule, completed_at.

- **FR-008**: System MUST publish a TaskUpdatedEvent when task metadata is modified via the `update_task` MCP tool, containing: event_id, event_type, timestamp, user_id, task_id, updated_fields (dictionary of changed fields).

- **FR-009**: System MUST publish a TaskDeletedEvent when a task is deleted via the `delete_task` MCP tool, containing: event_id, event_type, timestamp, user_id, task_id.

**Notification Service (Reminder System)**:

- **FR-010**: System MUST run an independent notification service that consumes events from the `task-events` and `task-reminders` Kafka topics as a member of the `notification-service-group` consumer group.

- **FR-011**: Notification service MUST poll the database every 5 seconds to query for tasks where: `due_date <= now() + 1 hour`, `reminder_sent = false`, and `completed = false`.

- **FR-012**: Notification service MUST log a reminder message for each task found, in the format: "🔔 REMINDER: Task '[title]' (ID: [id]) is due in [N] minutes".

- **FR-013**: Notification service MUST atomically update the task's `reminder_sent` flag to `true` in the database after logging the reminder, using `UPDATE ... WHERE reminder_sent = false AND id = ?` to prevent duplicate reminders.

- **FR-014**: Notification service MUST publish a ReminderSentEvent to the `task-reminders` topic after sending each reminder (for audit trail and future notification expansion).

- **FR-015**: Notification service MUST handle database connection failures with automatic retry logic (exponential backoff, max 3 retries) and graceful degradation.

- **FR-016**: Notification service MUST respond to Kubernetes SIGTERM signals by gracefully shutting down within 30 seconds (close Kafka consumer, commit offsets, close database connections).

**Recurring Task Service (Auto-Regeneration)**:

- **FR-017**: System MUST run an independent recurring task service that consumes TaskCompletedEvent messages from the `task-recurrence` Kafka topic as a member of the `recurring-task-service-group` consumer group.

- **FR-018**: Recurring task service MUST parse the `recurrence_rule` field using the iCalendar RRULE format (RFC 5545) with the `dateutil.rrule` library.

- **FR-019**: Recurring task service MUST calculate the next occurrence date by applying the RRULE to the original task's `due_date` (or `completed_at` if due_date is null).

- **FR-020**: Recurring task service MUST create a new task with identical properties (title, description, priority, category_id, tag_ids, recurrence_rule) but with the calculated next occurrence as the new `due_date`, and `completed = false`, `reminder_sent = false`.

- **FR-021**: Recurring task service MUST publish a TaskCreatedEvent to the `task-events` topic after creating the new recurring task instance.

- **FR-022**: Recurring task service MUST handle invalid RRULE formats by logging an error, skipping the event, and continuing processing (no new task created for invalid rules).

- **FR-023**: Recurring task service MUST skip regeneration if the calculated next occurrence is in the past (task completed late).

- **FR-024**: Recurring task service MUST support the following RRULE patterns:
  - `FREQ=DAILY`: Daily recurrence
  - `FREQ=WEEKLY;BYDAY=MO,WE,FR`: Weekly on specific weekdays
  - `FREQ=MONTHLY;BYMONTHDAY=15`: Monthly on specific day
  - `FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25`: Yearly on specific date

- **FR-024a**: MCP tools (add_task, update_task) MUST validate recurrence_rule values against the allowed RRULE patterns whitelist defined in FR-024 before task creation/update, rejecting invalid or unsupported patterns with a validation error.

**Full-Text Search Service**:

- **FR-025**: System MUST provide a `search_tasks` MCP tool that accepts a user_id and search query string, returning tasks ranked by relevance.

- **FR-026**: Search MUST use the existing `search_vector` tsvector column (created in Feature 001) with PostgreSQL's `plainto_tsquery` for natural language query parsing.

- **FR-027**: Search MUST rank results using PostgreSQL's `ts_rank` function, with title matches weighted higher (weight 'A') than description matches (weight 'B').

- **FR-028**: Search MUST support case-insensitive queries, word stemming (e.g., "running" matches "run"), and automatic stop word removal (e.g., "the", "a", "is").

- **FR-029**: Search MUST return results in under 200ms p95 for databases with up to 10,000 tasks (verified via EXPLAIN ANALYZE using GIN index).

- **FR-030**: Search MUST handle empty queries by returning all tasks (no filter applied) and queries with no matches by returning an empty array (not an error).

- **FR-031**: Search MUST reject queries longer than 500 characters with a validation error (400 Bad Request).

**Consumer Idempotency and Reliability**:

- **FR-032**: All Kafka consumer services MUST be idempotent, meaning processing the same event multiple times produces the same result (safe duplicate processing).

- **FR-033**: All Kafka consumer services MUST commit offsets after each successfully processed message to minimize duplicate event reprocessing on consumer restart.

- **FR-034**: All Kafka consumer services MUST automatically reconnect to Kafka brokers on connection failure within 5 seconds.

- **FR-035**: All Kafka consumer services MUST expose health check endpoints for Kubernetes liveness and readiness probes that verify both Kafka consumer connectivity and database connection pool status before returning success (200 OK).

### Key Entities *(include if feature involves data)*

**Event Entities**:

- **TaskCreatedEvent**: Represents the creation of a new task. Contains task metadata (title, priority, due_date, recurrence_rule, etc.) along with event metadata (event_id, timestamp, user_id). Published to `task-events` topic.

- **TaskCompletedEvent**: Represents the completion of a task. Contains task_id, recurrence_rule (if applicable), and completion timestamp. Published to `task-recurrence` topic to trigger recurring task regeneration.

- **TaskUpdatedEvent**: Represents changes to task metadata. Contains task_id and a dictionary of updated fields (e.g., `{"due_date": "2025-01-15T10:00:00", "priority": "high"}`). Published to `task-events` topic.

- **TaskDeletedEvent**: Represents the deletion of a task. Contains task_id and deletion timestamp. Published to `task-events` topic for audit trail.

- **ReminderSentEvent**: Represents a reminder notification sent for a task. Contains task_id and reminder timestamp. Published to `task-reminders` topic for audit and future notification expansion.

**Service Entities**:

- **Notification Service**: A Kafka consumer service that monitors tasks with approaching due dates and sends reminder notifications. Deployed as an independent Kubernetes pod with database and Kafka connectivity.

- **Recurring Task Service**: A Kafka consumer service that regenerates recurring tasks when completed. Parses RRULE patterns, calculates next occurrences, and creates new task instances. Deployed as an independent Kubernetes pod.

**Infrastructure Entities**:

- **Kafka Topic**: A message queue in Redpanda Cloud storing events. Three topics: `task-events` (task lifecycle), `task-reminders` (notifications), `task-recurrence` (recurring task automation).

- **Consumer Group**: A Kafka concept representing a set of consumers that share consumption of a topic. Each service uses a unique consumer group ID to track its offset independently.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Performance Metrics**:

- **SC-001**: Event publishing from MCP tools to Kafka completes in under 50ms at the 95th percentile (p95), ensuring minimal impact on user response times.

- **SC-002**: Notification service processes reminder checks and database updates in under 200ms p95, ensuring timely reminder delivery.

- **SC-003**: Recurring task service processes TaskCompletedEvent and creates new task instance in under 200ms p95, ensuring immediate task regeneration.

- **SC-004**: Full-text search queries return results in under 200ms p95 for databases with up to 10,000 tasks, providing fast task discovery.

- **SC-005**: Kafka event throughput supports at least 1,000 events per second without message loss or consumer lag exceeding 1,000 messages.

**Reliability Metrics**:

- **SC-006**: At least 99% of tasks with due dates receive reminder notifications within 1 minute of entering the reminder window (due_date - 1 hour).

- **SC-007**: At least 99% of completed recurring tasks successfully regenerate with correct next occurrence dates (verified by RRULE calculation accuracy).

- **SC-008**: No message loss occurs during normal operations (at-least-once delivery guarantee), verified by comparing events published vs. events consumed.

- **SC-009**: Consumer services automatically recover from Kafka broker failures within 5 seconds, resuming event processing from last committed offset.

- **SC-010**: System remains responsive to user operations (MCP tool calls) even when Kafka broker is temporarily unavailable (events fail to publish but user receives success response).

**User Experience Metrics**:

- **SC-011**: Users creating tasks with due dates receive immediate confirmation (synchronous response under 500ms) while reminder scheduling happens asynchronously in the background.

- **SC-012**: Users completing recurring tasks see the new instance created within 5 seconds of completion (includes event publish, consumer processing, and database insert).

- **SC-013**: Users searching for tasks with common keywords (e.g., "meeting", "project") see relevant results ranked correctly (title matches appear before description matches).

**Operational Metrics**:

- **SC-014**: Notification and recurring task services handle graceful shutdowns (SIGTERM) within 30 seconds, committing Kafka offsets and closing database connections cleanly.

- **SC-015**: All services expose health check endpoints that respond within 100ms, enabling Kubernetes to detect and restart unhealthy pods automatically.

## Assumptions *(optional - document key assumptions made)*

### Architecture Assumptions

- **Kafka Broker**: Redpanda Cloud Starter plan provides sufficient capacity (1 node, 10 GB storage) for MVP event volumes (estimated <10,000 events/day).

- **Event Ordering**: Events for the same task are processed in order because task_id is used as the partition key (same partition = guaranteed order within that partition).

- **Consumer Replicas**: Notification and recurring task services deploy with 1 replica each to avoid duplicate processing complexity (horizontal scaling deferred to future phases).

- **Network Connectivity**: Kubernetes pods can reach Redpanda Cloud brokers via public internet (TLS + SASL authentication secures the connection).

### Data Assumptions

- **Search Vector Population**: The `search_vector` column is already populated for existing tasks via the database trigger created in Feature 001 migration.

- **GIN Index Availability**: The GIN index on `search_vector` exists and is used by the query planner (verified with EXPLAIN ANALYZE).

- **Reminder Window**: The default reminder window (1 hour before due_date) meets user needs for MVP. Configurable windows deferred to future phases.

- **Recurrence Patterns**: The supported RRULE patterns (DAILY, WEEKLY, MONTHLY, YEARLY) cover 95% of user recurrence needs. Complex patterns (BYDAY with INTERVAL, BYSETPOS, etc.) are future enhancements.

### Operational Assumptions

- **Database Performance**: Neon PostgreSQL can handle the reminder query load (executes every 5 seconds) without performance degradation, given proper indexing.

- **Event Retention**: 7-day retention for `task-events` and `task-recurrence` topics is sufficient for debugging and event replay. 1-day retention for `task-reminders` is sufficient for audit trail.

- **Consumer Lag**: Consumer services can keep up with event production rates (processing time < event arrival rate), preventing unbounded lag growth.

- **Graceful Degradation**: It's acceptable for reminders and recurring tasks to be delayed if services are temporarily down (events will be processed when services recover).

## Out of Scope *(optional - explicitly state what is NOT included)*

### Not Included in This Feature

- **Push Notifications**: Email, SMS, or browser push notifications for reminders. Only log-based reminders are implemented (future enhancement: integrate with notification providers).

- **Complex Event Processing (CEP)**: Event aggregation, windowing, or stream joins. Events are processed independently without stateful stream processing.

- **Distributed Transactions**: Saga patterns or two-phase commits. Services use at-least-once delivery with idempotency instead of exactly-once guarantees.

- **Dead-Letter Queue Automation**: Automatic retry or manual review UI for failed events. Failed events are logged but require manual intervention (future enhancement: DLQ dashboard).

- **Reminder Customization**: User-configurable reminder windows (e.g., 30 minutes vs. 1 hour before due date). Fixed 1-hour window for MVP.

- **Recurring Task Editing**: Ability to edit a single instance vs. all future instances of a recurring task. Editing applies to individual tasks only (future enhancement: series editing).

- **Event Versioning**: Schema evolution or backward compatibility for event formats. Initial v1 schema with no migration strategy (future enhancement: event versioning).

- **Multi-Datacenter Replication**: Kafka mirroring or cross-region event streaming. Single-region deployment only (future enhancement: geo-distributed architecture).

- **Exactly-Once Semantics**: Kafka transactions or idempotent consumers. At-least-once delivery with idempotency is sufficient for MVP.

- **OAuth Calendar Integration**: Sync recurring tasks with Google Calendar, Outlook, etc. Standalone task management only (future enhancement: calendar sync).

## Dependencies *(optional - list required features or external systems)*

### Internal Dependencies (Blocking)

- **Feature 001 - Foundation + API Layer** (COMPLETED):
  - Enhanced task models with `priority`, `due_date`, `category_id`, `recurrence_rule`, `reminder_sent` fields.
  - Database migration creating `search_vector` tsvector column with GIN index.
  - MCP tools for task CRUD operations (`add_task`, `complete_task`, `update_task`, `delete_task`).
  - Database trigger `task_search_update` that automatically populates `search_vector` on INSERT/UPDATE.

### External Dependencies

- **Redpanda Cloud Kafka Cluster**:
  - Managed Kafka service (Starter plan: 1 node, 10 GB storage).
  - SASL/SCRAM-SHA-256 authentication configured.
  - TLS encryption enabled.
  - Network accessibility from Kubernetes cluster (public internet or VPN).

- **Python Libraries**:
  - `aiokafka==0.11.0`: Async Kafka client for Python.
  - `python-dateutil==2.8.2`: RRULE parsing and date calculations.
  - `pydantic==2.5.0`: Event schema validation and serialization.
  - `asyncpg==0.29.0`: Async PostgreSQL driver (already in use from Feature 001).

- **Database**:
  - Neon PostgreSQL Serverless (already provisioned).
  - Sufficient connection pool capacity for additional consumer service connections.

### Blocked Features

This feature blocks the following future features:

- **Feature 003 - ChatKit UI Enhancements**: Needs event-driven features (reminders, recurrence) working to display in UI.
- **Feature 004 - Dapr Foundation**: Will migrate from direct Kafka integration to Dapr Pub/Sub components.
- **Feature 005 - Dapr Migration**: Replaces `aiokafka` library with Dapr HTTP API for infrastructure-agnostic event streaming.

## Risks and Mitigations *(optional - identify potential issues)*

### High-Risk Areas

**Risk 1: Kafka Broker Connectivity Issues**
- **Description**: Kubernetes pods unable to reach Redpanda Cloud cluster due to network restrictions or firewall rules.
- **Impact**: Events cannot be published or consumed, breaking reminders and recurring tasks.
- **Mitigation**:
  - Test connectivity from Kubernetes pod before deployment: `nc -zv <broker>:9092`
  - Verify SASL credentials with `kafkacat` CLI tool.
  - Configure producer/consumer retry logic (3 retries with exponential backoff).
  - Implement graceful degradation: MCP tools succeed even if Kafka is unreachable (async failure).

**Risk 2: Duplicate Reminders (Multiple Service Replicas)**
- **Description**: If notification service scales to multiple replicas, each replica might send duplicate reminders for the same task.
- **Impact**: Users receive multiple reminder notifications for the same task, degrading user experience.
- **Mitigation**:
  - Deploy notification service with 1 replica for MVP (simplest solution).
  - Use atomic database update: `UPDATE tasks SET reminder_sent = true WHERE id = ? AND reminder_sent = false` (only one UPDATE succeeds).
  - If horizontal scaling is needed in the future, implement distributed locking (e.g., Redis) to coordinate reminder sending.

**Risk 3: RRULE Parsing Failures (Invalid Recurrence Rules)**
- **Description**: Users might create tasks with invalid or overly complex RRULE patterns that the `dateutil.rrule` library cannot parse.
- **Impact**: Recurring task service crashes or skips regeneration, breaking recurring task automation.
- **Mitigation**:
  - Validate RRULE against allowed patterns whitelist (FR-024a) on task creation in `add_task` MCP tool (fail-fast validation preventing unsupported patterns).
  - Wrap RRULE parsing in try/except block in recurring task service.
  - Log parsing errors with task details for debugging.
  - Move failed events to dead-letter topic (future enhancement) for manual review.

**Risk 4: Consumer Lag and Backpressure**
- **Description**: Consumer services fall behind event production rate, causing growing lag and delayed reminders/recurrence.
- **Impact**: Reminders arrive late, recurring tasks regenerate with delay, degrading user experience.
- **Mitigation**:
  - Monitor consumer lag using Kafka consumer metrics (implement in Feature 008 - Monitoring).
  - Optimize database queries with proper indexes (already in place from Feature 001).
  - Alert if lag exceeds 1,000 messages (indicates capacity issue).
  - If needed, scale consumer services horizontally (requires distributed locking for notification service).

**Risk 5: Search Performance Degradation (Large Datasets)**
- **Description**: As task count grows to 10,000+, full-text search queries may slow down, exceeding 200ms p95 target.
- **Impact**: Users experience slow search results, degrading usability.
- **Mitigation**:
  - Verify GIN index exists and is used by query planner (EXPLAIN ANALYZE).
  - Monitor slow queries (log queries >500ms).
  - Limit search results to 50 tasks (pagination for future enhancement).
  - Consider partial GIN index (only index non-deleted tasks) to reduce index size.

**Risk 6: Event Ordering Violations (Multiple Partitions)**
- **Description**: Events for the same task might be processed out of order if they end up in different partitions.
- **Impact**: Stale events overwrite newer events (e.g., TaskDeletedEvent processed before TaskUpdatedEvent).
- **Mitigation**:
  - Use `task_id` as partition key when publishing events (ensures events for same task go to same partition).
  - Single partition guarantees ordering within that partition.
  - Consumer processes events in partition order (Kafka guarantee).

### Medium-Risk Areas

**Risk 7: Database Connection Pool Exhaustion**
- **Description**: Consumer services create additional database connections, potentially exhausting Neon PostgreSQL connection pool.
- **Impact**: Database queries fail, breaking reminders and recurring tasks.
- **Mitigation**:
  - Configure connection pooling in consumer services (limit max connections per service).
  - Monitor active database connections (Neon dashboard).
  - Increase connection pool size if needed (Neon configuration).

**Risk 8: Reminder Service Polling Overhead**
- **Description**: Querying the database every 5 seconds for tasks with approaching due dates creates continuous database load.
- **Impact**: Increased database CPU usage, potential performance degradation.
- **Mitigation**:
  - Use efficient query with indexed columns (`due_date`, `reminder_sent`, `completed`).
  - Limit query to tasks due within next hour (bounded result set).
  - Monitor database performance metrics (CPU, query latency).
  - If needed, increase polling interval to 10 seconds or move to event-driven scheduling (Dapr Jobs API in Feature 005).

## Notes *(optional - additional context or decisions)*

### Why Redpanda Cloud Instead of Self-Hosted Kafka?

- **Managed Service**: Eliminates Kafka cluster management complexity (no ZooKeeper, broker configuration, replication management).
- **Cost-Effective**: Starter plan ($0.50/hour) provides sufficient capacity for MVP without infrastructure overhead.
- **Performance**: Redpanda is Kafka-compatible but faster (C++ implementation vs. Java), with lower latency.
- **Simple Setup**: No need to provision infrastructure, configure networking, or manage upgrades.
- **Future-Ready**: Easy to scale to production by adding more nodes, partitions, or regions as event volume grows.

### Why At-Least-Once Delivery Instead of Exactly-Once?

- **Simpler Implementation**: Exactly-once semantics require Kafka transactions and complex coordinator logic.
- **Acceptable for MVP**: Idempotent consumers (notification and recurring task services) handle duplicate events safely.
- **Performance**: At-least-once delivery has lower latency (no transaction commit overhead).
- **Trade-off**: Some duplicate events may occur (rare), but services are designed to handle them correctly (duplicate reminders prevented by atomic DB update, duplicate recurring tasks can be deleted by user).

### Why Polling for Reminders Instead of Event-Driven Scheduling?

- **Simpler Implementation**: No need for distributed scheduler (Celery, Temporal, Airflow) or scheduled task management.
- **Acceptable Latency**: 5-second poll interval provides sufficient reminder timeliness (not real-time, but adequate for "due in 1 hour" notifications).
- **Lower Complexity**: No scheduler state management, job queue, or worker coordination.
- **Future Enhancement**: Can migrate to event-driven scheduling using Dapr Jobs API in Feature 005 (scheduled task execution without polling).

### Why Single Replica for Consumer Services?

- **Avoid Duplicate Processing**: Notification and recurring task services should process each event exactly once (idempotency handles duplicates, but single replica is simpler).
- **Acceptable for MVP**: Low event volume (<10,000 events/day) can be handled by single replica.
- **Kubernetes Resilience**: Single replica auto-restarts on failure (liveness probe detects crashes, scheduler restarts pod).
- **Future Scaling**: Can add multiple replicas with distributed locking (Redis SETNX) or partitioned consumption if throughput increases.

### Event Publishing as "Fire-and-Forget"

- **User Experience Priority**: MCP tools return success immediately to users, even if Kafka event publishing fails (async failure).
- **Graceful Degradation**: If Kafka is down, users can still create/update/delete tasks (core functionality intact), but reminders and recurrence may be delayed until Kafka recovers.
- **Monitoring Required**: Log all Kafka publish failures for alerting and debugging (implement in Feature 008 - Monitoring).
- **Trade-off**: Some events may be lost if Kafka is unreachable during the async publish attempt, but this is acceptable for MVP (reminders and recurrence are enhancements, not core functionality).
