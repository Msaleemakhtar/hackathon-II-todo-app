# Feature Specification: Dapr Integration for Event-Driven Architecture

**Feature Branch**: `004-dapr-integration`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "use @"spec-architect (agent)" and create a speecification for integration of dapr as discussed above in planning phase"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Transparent Event Processing (Priority: P0 - Critical)

As a **system operator**, I need the event-driven task management system to continue functioning identically after Dapr integration, so that users experience zero disruption while gaining infrastructure portability.

**Why this priority**: This is the foundation requirement - the system must maintain 100% functional equivalence with the current Kafka-based implementation. Without this, all other benefits are meaningless.

**Independent Test**: Can be fully tested by executing the complete end-to-end task lifecycle (create → reminder → email delivery → recurring task generation) and verifying identical behavior before and after Dapr migration. Delivers immediate value by proving the migration succeeded without breaking existing functionality.

**Acceptance Scenarios**:

1. **Given** a task is created with a due date 30 minutes in the future, **When** the notification service job triggers after 5 seconds, **Then** a reminder event is published to the task-reminders topic via Dapr and an email is delivered to the user
2. **Given** a recurring task (FREQ=DAILY) is marked complete, **When** the recurring service processes the completion event, **Then** a new task instance is created for the next day and a TaskCreatedEvent is published via Dapr
3. **Given** the same task completion event is processed twice, **When** the idempotency check runs, **Then** only one new task is created (no duplicates)
4. **Given** 100 tasks are created simultaneously, **When** events are published via Dapr Pub/Sub, **Then** all 100 events are delivered with latency under 100ms per event
5. **Given** a service pod is restarted during event processing, **When** the pod comes back online, **Then** Dapr resumes processing from the last committed offset with no message loss

---

### User Story 2 - Infrastructure Portability (Priority: P1 - High)

As a **DevOps engineer**, I need the event-driven architecture to be infrastructure-agnostic through Dapr components, so that I can migrate between Kafka providers (Redpanda, Confluent, AWS MSK) or even different message brokers (Redis Streams, RabbitMQ) without code changes.

**Why this priority**: This delivers the core value proposition of Dapr - decoupling application logic from infrastructure. Enables cloud migration flexibility and vendor independence.

**Independent Test**: Can be tested by swapping the Dapr Pub/Sub component configuration from Kafka to Redis Streams, restarting services, and verifying all event flows still work. Delivers value by proving infrastructure independence.

**Acceptance Scenarios**:

1. **Given** the Dapr Pub/Sub component is configured for Kafka, **When** I change the component to use Redis Streams and restart services, **Then** all event publishing and consumption continues without application code changes
2. **Given** Kafka credentials are rotated, **When** I update only the Dapr component YAML with new credentials, **Then** services reconnect automatically without code deployment
3. **Given** I need to migrate from Redpanda Cloud to AWS MSK, **When** I update the broker URLs in the Dapr component, **Then** the migration completes with zero downtime using rolling updates

---

### User Story 3 - Simplified Operations (Priority: P2 - Medium)

As a **platform engineer**, I need Dapr to handle infrastructure concerns (authentication, retries, dead letter queues) declaratively through YAML configuration, so that I can manage operational complexity without modifying application code.

**Why this priority**: Reduces operational burden by moving infrastructure concerns out of application code into declarative configuration. Improves maintainability and reduces error surface area.

**Independent Test**: Can be tested by configuring dead letter topic handling in the Dapr component YAML, simulating a poison message, and verifying automatic routing to the dead letter queue without application intervention. Delivers value by proving operational simplification.

**Acceptance Scenarios**:

1. **Given** a message fails processing 3 times, **When** Dapr's retry policy is exhausted, **Then** the message is automatically routed to the dead letter topic configured in the component YAML
2. **Given** Kafka authentication requires SASL_SSL, **When** credentials are provided in the Dapr component, **Then** all services connect automatically without individual connection code
3. **Given** I need to enable message tracing, **When** I add OpenTelemetry configuration to Dapr, **Then** all pub/sub operations are automatically traced without code instrumentation

---

### User Story 4 - Guaranteed Job Execution (Priority: P1 - High)

As a **system administrator**, I need the notification service's 5-second polling job to be guaranteed by Dapr's scheduler across multiple replicas, so that reminders are sent exactly once even when scaling horizontally.

**Why this priority**: Critical for reliability and scalability. Current single-replica polling is a single point of failure. Dapr Jobs API enables horizontal scaling without duplicate reminder risk.

**Independent Test**: Can be tested by scaling notification service to 3 replicas, creating 10 tasks due within the hour, and verifying exactly 10 reminder emails are sent (no duplicates). Delivers value by proving multi-replica safety.

**Acceptance Scenarios**:

1. **Given** notification service runs with 3 replicas, **When** the scheduled job triggers every 5 seconds, **Then** only one replica processes the job (Dapr guarantees single execution)
2. **Given** a notification service replica crashes during job execution, **When** Dapr detects the failure, **Then** the job is automatically reassigned to a healthy replica and completes within the next 5-second interval
3. **Given** the scheduler service is restarted, **When** it comes back online, **Then** all registered jobs resume execution from persistence without manual intervention

---

### Edge Cases

- **What happens when Dapr sidecar crashes during event publishing?** The application retry logic should detect the failure (HTTP 503 from localhost:3500) and buffer the event for retry. On sidecar recovery, buffered events are published. Maximum event loss window is the time between crash and application retry.

- **How does the system handle CloudEvents format incompatibility?** If consumers cannot parse Dapr's CloudEvents wrapper, enable `rawPayload: true` in the publish metadata to disable CloudEvents wrapping. This provides an escape hatch while preserving Dapr benefits.

- **What happens if the Dapr Pub/Sub component references an invalid Kafka broker?** Dapr sidecar logs connection errors, health checks fail (HTTP 500 on /healthz), and Kubernetes restarts the pod. The deployment should include readiness probes to prevent traffic routing to unhealthy pods.

- **How does the system prevent duplicate reminders when jobs are rescheduled?** Dapr Jobs API guarantees at-most-once execution across replicas. Additionally, the notification service updates the `reminder_sent` flag atomically in the database before publishing events, providing defense-in-depth.

- **What happens when message processing takes longer than the consumer timeout?** Dapr's default timeout is 60 seconds. For long-running operations (email delivery with retries), configure `pubsub.kafka/messageHandlerTimeout` metadata to increase the timeout or implement async processing patterns.

- **How does rollback work if Dapr migration fails?** The rollback plan involves reverting Kubernetes deployment manifests to remove Dapr annotations, redeploying pre-migration Docker images with aiokafka, and removing Dapr component YAMLs. Consumer offsets are preserved because consumer group IDs remain unchanged.

## Requirements *(mandatory)*

### Functional Requirements

#### Pub/Sub Migration

- **FR-001**: System MUST publish all task lifecycle events (TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent) to Kafka topics via Dapr Pub/Sub HTTP API instead of direct aiokafka producer
- **FR-002**: System MUST consume events from Kafka topics (task-reminders, task-recurrence) via Dapr declarative subscriptions instead of direct aiokafka consumers
- **FR-003**: Dapr Pub/Sub component MUST use SASL_SSL authentication with SCRAM-SHA-256 mechanism to connect to Redpanda Cloud, preserving current security configuration
- **FR-004**: Event publishing MUST maintain idempotency guarantees (at-least-once delivery) through Dapr's producer configuration matching current aiokafka settings (enable_idempotence: true, acks: all)
- **FR-005**: System MUST support partition key specification for events to ensure ordering within partitions (e.g., all events for task_id=123 go to the same partition)
- **FR-006**: Dapr MUST wrap published events in CloudEvents 1.0 format for standardization, with option to disable wrapping via `rawPayload: true` metadata if needed

#### Consumer Migration

- **FR-007**: Email delivery service MUST subscribe to the `task-reminders` topic via Dapr declarative subscription YAML, with HTTP endpoint `/events/reminder-sent` receiving CloudEvents
- **FR-008**: Recurring task service MUST subscribe to the `task-recurrence` topic via Dapr declarative subscription YAML, with HTTP endpoint `/events/task-completed` receiving CloudEvents
- **FR-009**: Dapr MUST commit consumer offsets automatically on HTTP 200 OK response from subscription endpoints, and retry on 4xx/5xx responses
- **FR-010**: Consumer subscriptions MUST support bulk message delivery (10 messages per batch) to match current `max_poll_records` configuration
- **FR-011**: Consumer group IDs MUST remain unchanged during migration (Dapr uses `app-id` annotation as consumer group) to preserve offset continuity

#### Jobs API Migration

- **FR-012**: Notification service MUST register a scheduled job named "check-due-tasks" with Dapr Scheduler API to run every 5 seconds, replacing the current async polling loop
- **FR-013**: Dapr Jobs API MUST guarantee at-most-once execution of the scheduled job across multiple notification service replicas to prevent duplicate reminders
- **FR-014**: Scheduled job MUST invoke HTTP endpoint `/jobs/check-due-tasks` on the notification service, triggering reminder processing logic
- **FR-015**: Jobs MUST persist in Dapr's etcd backend to survive scheduler service restarts without manual re-registration
- **FR-016**: Job execution failures MUST be logged by Dapr and automatically retried on the next scheduled interval

#### State Management

- **FR-017**: Notification service MUST use Dapr State Store (PostgreSQL v2) to track last poll timestamp and reminder processing state for idempotency validation
- **FR-018**: State store MUST create separate tables (`dapr_state_store`, `dapr_state_metadata`) to avoid conflicts with application schema
- **FR-019**: State entries MUST support TTL (time-to-live) with automatic cleanup every 3600 seconds to prevent unbounded growth

#### Deployment & Operations

- **FR-020**: All service deployments (backend, notification, email-delivery, recurring) MUST include Dapr sidecar annotations (`dapr.io/enabled: true`, `dapr.io/app-id`, `dapr.io/app-port`) to enable sidecar injection
- **FR-021**: Dapr sidecars MUST expose health check endpoints at `/healthz` for Kubernetes liveness probes
- **FR-022**: Services MUST communicate with Dapr sidecars via localhost HTTP on port 3500 (default Dapr HTTP port)
- **FR-023**: Dapr component configurations MUST be scoped to specific apps using the `scopes` field to prevent unauthorized access
- **FR-024**: Kafka connection credentials MUST be referenced from Kubernetes secrets in Dapr components using `secretKeyRef` instead of inline values

#### Performance & Reliability

- **FR-025**: Event publishing latency via Dapr MUST remain under 100ms p95 (matching current aiokafka baseline)
- **FR-026**: Consumer throughput via Dapr MUST support 10 messages per batch with processing latency under 200ms p95
- **FR-027**: Dapr sidecar memory overhead MUST not exceed 128MB per pod under normal load
- **FR-028**: Services MUST implement graceful shutdown with 30-second termination grace period to allow Dapr to flush pending events and commit offsets

#### Backward Compatibility

- **FR-029**: Migration MUST preserve Kafka topic names (task-events, task-reminders, task-recurrence) to maintain compatibility with external monitoring tools
- **FR-030**: Consumer offsets MUST continue from last committed position (no reprocessing of old messages) by maintaining consumer group IDs
- **FR-031**: Event schemas (TaskCreatedEvent, TaskUpdatedEvent, etc.) MUST remain unchanged in the data payload, with CloudEvents wrapper adding only metadata fields

#### Dependency Management

- **FR-032**: Python dependencies MUST remove `aiokafka==0.11.0` from requirements.txt after successful migration
- **FR-033**: System MUST add new dependency on `httpx` for Dapr HTTP client communication
- **FR-034**: Dapr runtime version MUST be v1.12+ to support Jobs API and PostgreSQL State Store v2

### Key Entities *(include if feature involves data)*

- **Dapr Component**: Represents infrastructure configuration (Pub/Sub, State Store, Secrets, Jobs Scheduler) defined in YAML and deployed to Kubernetes. Each component has metadata (connection strings, credentials) and scopes (which apps can access it).

- **CloudEvent**: Standard event envelope format (version 1.0) wrapping application events. Contains metadata fields (id, source, type, time) and data payload (TaskCreatedEvent, TaskUpdatedEvent, etc.). Enables event routing and tracing.

- **Scheduled Job**: Represents a recurring execution unit registered with Dapr Jobs API. Contains schedule expression (@every 5s), target endpoint (/jobs/check-due-tasks), and persistence state (etcd).

- **Dapr Subscription**: Declarative configuration linking a Pub/Sub topic to an application HTTP endpoint. Contains topic name, route path, consumer group (app-id), and delivery options (bulk settings).

- **State Entry**: Key-value pair stored in Dapr State Store. Contains key (e.g., "last_poll_timestamp"), value (JSON data), optional ETag (for optimistic concurrency), and optional TTL (automatic expiration).

- **Dapr Sidecar**: Per-pod proxy container injected by Kubernetes that handles all infrastructure communication. Exposes HTTP/gRPC APIs on localhost for application interaction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All task lifecycle operations (create, update, complete, delete) continue functioning identically after Dapr migration, verified through 100 end-to-end test scenarios with zero functional regressions
- **SC-002**: Event publishing latency remains under 100ms p95 when measured from application code to Dapr sidecar HTTP response
- **SC-003**: Notification service successfully scales to 3 replicas with exactly one job execution per 5-second interval (zero duplicate reminders in 1-hour test period)
- **SC-004**: System handles 1000 concurrent task creations with all 1000 events published successfully via Dapr Pub/Sub within 10 seconds
- **SC-005**: Infrastructure swap test succeeds: changing Dapr Pub/Sub component from Kafka to Redis Streams and back results in zero message loss and zero code changes
- **SC-006**: Rollback test completes in under 5 minutes: reverting to aiokafka-based deployment and verifying all services healthy with no data loss
- **SC-007**: Dapr sidecar memory overhead stays under 128MB per pod during 1-hour load test with 100 events/second throughput
- **SC-008**: Consumer offset continuity maintained: migration preserves last committed offset for each consumer group with no message reprocessing
- **SC-009**: End-to-end email delivery flow (task due → reminder published → email sent) completes in under 10 seconds via Dapr subscriptions
- **SC-010**: Dead letter queue test succeeds: intentionally failing message processing 3 times results in automatic routing to dead letter topic without manual intervention

## Scope & Boundaries *(mandatory)*

### In Scope

- Migrating all Kafka event producers from aiokafka to Dapr Pub/Sub HTTP API (backend, notification service)
- Migrating all Kafka event consumers from aiokafka to Dapr declarative subscriptions (email delivery service, recurring task service)
- Replacing notification service database polling loop with Dapr Jobs API scheduled job
- Creating 4 Dapr component configurations (Pub/Sub, State Store, Secrets, Jobs Scheduler)
- Updating all Kubernetes deployment manifests with Dapr sidecar annotations
- Removing aiokafka dependency from requirements.txt
- Implementing Dapr HTTP client wrapper for pub/sub and state management operations
- Creating declarative subscription YAMLs for all consumer services
- Comprehensive testing: unit tests, integration tests, performance tests, rollback tests
- Documentation: Dapr component configuration guide, migration runbook, troubleshooting guide

### Out of Scope

- Changing Kafka topic names or event schemas (backward compatibility requirement)
- Migrating database access to Dapr State Store (database operations remain direct via SQLModel/asyncpg)
- Implementing Dapr service invocation for inter-service communication (services remain independent)
- Adding Dapr bindings for SMTP email delivery (email service continues using direct SMTP client)
- Implementing Dapr Workflow API for task orchestration (out of scope for this migration)
- Changing consumer group IDs or reprocessing historical messages
- Upgrading Kafka broker version or changing from Redpanda to another provider
- Modifying task data models or database schema (purely infrastructure migration)
- Adding new features or changing existing task management functionality
- Performance optimization beyond maintaining baseline metrics (not a performance improvement project)

## Assumptions *(mandatory)*

- **Infrastructure Assumption**: Kubernetes cluster supports Dapr installation via `dapr init -k` with sufficient permissions to create CRDs and system namespaces
- **Dapr Version Assumption**: Dapr v1.12 or higher is available, providing Jobs API and PostgreSQL State Store v2 support
- **Kafka Broker Assumption**: Redpanda Cloud Kafka cluster remains the production broker during migration (no broker migration in scope)
- **Authentication Assumption**: Current SASL_SSL credentials for Kafka remain valid and can be referenced in Dapr components via Kubernetes secrets
- **Database Assumption**: Neon PostgreSQL database supports Dapr State Store v2 tables (`dapr_state_store`, `dapr_state_metadata`) without conflicts
- **Network Assumption**: Kubernetes cluster allows localhost communication between application containers and Dapr sidecars on port 3500 (HTTP) and 50001 (gRPC)
- **Deployment Assumption**: Current Helm chart structure supports adding Dapr annotations and component YAMLs without major restructuring
- **Testing Assumption**: Test environment has access to Redpanda Cloud Kafka cluster for integration testing (not using embedded Kafka)
- **Monitoring Assumption**: Existing Kafka monitoring tools (consumer lag dashboards) can continue working with Dapr-managed consumer groups
- **Backwards Compatibility Assumption**: Existing Phase V features (001-003) remain operational during and after migration with zero downtime requirement
- **Rollback Assumption**: Pre-migration Docker images with aiokafka dependencies are retained for rollback scenarios
- **Performance Assumption**: Baseline performance metrics (event latency, consumer throughput) are measured before migration for comparison
- **CloudEvents Assumption**: Consumer services can be updated to parse CloudEvents format (extracting data from envelope), or `rawPayload: true` can be used as escape hatch

## Dependencies *(mandatory)*

### External Dependencies

- **Dapr Runtime v1.12+**: Required for Jobs API and PostgreSQL State Store v2 support
- **Kubernetes Cluster v1.21+**: Required for Dapr CRD support and sidecar injection
- **Redpanda Cloud Kafka**: Existing message broker continues as backend for Dapr Pub/Sub component
- **Neon PostgreSQL**: Database for Dapr State Store (separate tables from application schema)
- **Kubernetes Secrets**: Stores Kafka credentials, PostgreSQL connection string for Dapr component references
- **httpx Python library**: HTTP client for Dapr sidecar communication (replaces aiokafka)

### Internal Dependencies

- **Feature 001 (Foundation + API)**: Database schema with enhanced task models (priority, due_date, category, tags) must be in place
- **Feature 002 (Event-Driven Architecture)**: Current Kafka-based implementation serves as baseline for functional equivalence testing
- **Feature 003 (ChatKit UI)**: Frontend remains unchanged but depends on backend event publishing continuing to work
- **Helm Chart Infrastructure**: Deployment templates must support Dapr annotations and component YAML inclusion
- **Docker Image Build Pipeline**: Must rebuild backend images with updated dependencies (remove aiokafka, add httpx)

### Blocking Dependencies

- **Dapr CLI Installation**: Must be installed on developer machines and CI/CD runners before migration work begins
- **Dapr Kubernetes Initialization**: `dapr init -k` must complete successfully, creating Dapr system pods (operator, sidecar-injector, scheduler) before deploying components
- **Kubernetes Secret Creation**: `todo-app-secrets` must include `POSTGRES_CONNECTION_STRING` derived from existing `DATABASE_URL` for state store component
- **Baseline Performance Metrics**: Must capture current aiokafka performance (latency, throughput) before migration for comparison testing

## Risks & Mitigations *(optional)*

### High-Risk Areas

**Risk 1: CloudEvents Format Breaking Consumers**
- **Impact**: Consumer services fail to parse Dapr-wrapped CloudEvents, causing message processing failures and consumer lag buildup
- **Probability**: Medium (CloudEvents adds envelope around existing event schema)
- **Mitigation Strategy**:
  - Test with single consumer first (email delivery service) before migrating all consumers
  - Implement CloudEvents parser that extracts `data` field from envelope
  - Configure `rawPayload: true` in publish metadata as fallback to disable CloudEvents wrapping
  - Create comprehensive integration tests validating CloudEvents parsing before production deployment
- **Fallback Plan**: Revert to aiokafka for affected consumer while fixing CloudEvents handling

**Risk 2: Dapr Sidecar Resource Exhaustion**
- **Impact**: Dapr sidecars consume excessive memory/CPU, causing pod evictions and service degradation
- **Probability**: Low (Dapr is production-ready, but resource limits must be tuned)
- **Mitigation Strategy**:
  - Set conservative resource limits in annotations: `dapr.io/sidecar-memory-limit: 256Mi`, `dapr.io/sidecar-cpu-limit: 200m`
  - Monitor sidecar resource usage during load testing and adjust limits
  - Configure Dapr log level to `info` (not `debug`) to reduce log volume
  - Enable Dapr metrics (`dapr.io/enable-metrics: true`) for observability
- **Fallback Plan**: Increase resource limits or reduce event throughput temporarily

**Risk 3: Jobs API Single Execution Guarantee Failure**
- **Impact**: Notification service scaled to multiple replicas sends duplicate reminders to users
- **Probability**: Low (Dapr guarantees at-most-once execution, but edge cases may exist)
- **Mitigation Strategy**:
  - Add defense-in-depth: notification service checks `reminder_sent` flag in database before publishing events
  - Use Dapr State Store to track processed task IDs with TTL for idempotency validation
  - Test with 3 replicas in staging environment before production deployment
  - Monitor for duplicate emails using SMTP logs and task database flags
- **Fallback Plan**: Revert to single-replica deployment if duplicates detected

**Risk 4: Kafka Authentication Failures with Dapr Component**
- **Impact**: Dapr Pub/Sub component cannot connect to Redpanda Cloud, blocking all event publishing
- **Probability**: Medium (SASL_SSL configuration is complex, secret references may fail)
- **Mitigation Strategy**:
  - Test Kafka component configuration with `dapr run` locally before Kubernetes deployment
  - Verify secret keys match exactly: `KAFKA_SASL_USERNAME`, `KAFKA_SASL_PASSWORD`, `KAFKA_BOOTSTRAP_SERVERS`
  - Enable Dapr debug logging temporarily to diagnose connection issues
  - Use `kubectl describe component pubsub-kafka -n todo-phasev` to check for initialization errors
- **Fallback Plan**: Temporarily use `localhost:9092` with embedded Kafka for testing, then fix production credentials

**Risk 5: Consumer Offset Loss During Migration**
- **Impact**: Consumers reprocess old messages or skip new messages after migration
- **Probability**: Low (consumer group IDs preserved via app-id)
- **Mitigation Strategy**:
  - Verify consumer group IDs before and after migration using `kafka-consumer-groups.sh --describe`
  - Ensure Dapr `app-id` annotation matches original consumer group name exactly
  - Commit offsets manually before migration using `kafka-consumer-groups.sh --reset-offsets`
  - Test migration in staging environment with non-empty topics
- **Fallback Plan**: Manually reset offsets to last known good position using Kafka admin tools

**Risk 6: Rollback Complexity**
- **Impact**: Rollback takes longer than expected, extending downtime window
- **Probability**: Medium (multiple components must be reverted: deployments, images, components)
- **Mitigation Strategy**:
  - Document detailed rollback procedure with exact commands in migration runbook
  - Practice rollback in staging environment before production migration
  - Retain pre-migration Docker images with aiokafka for fast rollback
  - Create backup Kubernetes manifests (`.backup` files) before applying Dapr changes
  - Set 30-minute rollback time target and practice achieving it
- **Fallback Plan**: If rollback exceeds 30 minutes, maintain partial Dapr deployment and fix issues forward

## Open Questions *(optional - for tracking unresolved items)*

*No critical open questions remain. All key architectural decisions have been made during the planning phase.*

## Notes *(optional)*

### Migration Phases

The migration follows a two-phase approach as defined in PHASE_V_FEATURE_BREAKDOWN.md:

**Phase 1: Feature 004 - Dapr Foundation (4 hours)**
- Install Dapr runtime on Kubernetes
- Create 4 Dapr component YAMLs
- Validate components without code changes
- Zero risk to existing services

**Phase 2: Feature 005 - Code Migration (16 hours)**
- Implement Dapr HTTP client wrapper
- Migrate producers and consumers incrementally
- Update Kubernetes deployments with Dapr annotations
- Comprehensive testing and validation

### Testing Strategy

Comprehensive testing is critical for this infrastructure migration:

1. **Unit Tests**: Validate Dapr HTTP client methods (publish_event, save_state, get_state)
2. **Integration Tests**: End-to-end flows (reminder delivery, recurring task creation, idempotency)
3. **Performance Tests**: Latency benchmarks (< 100ms p95), throughput tests (1000 events in 10s)
4. **Resilience Tests**: Pod restarts, sidecar crashes, network partitions
5. **Rollback Tests**: Full rollback procedure in staging environment

### Configuration Management

Dapr components use declarative YAML configuration with these best practices:

- Store Kafka credentials in Kubernetes secrets, reference via `secretKeyRef`
- Use `scopes` field to limit component access to specific apps
- Version component YAMLs in Git for change tracking
- Apply components to correct namespace (`todo-phasev`)
- Use consistent naming: `pubsub-kafka`, `statestore-postgres`, `kubernetes-secrets`, `jobs-scheduler`

### Monitoring & Observability

Post-migration monitoring focuses on:

- Dapr sidecar health: `/healthz` endpoint status
- Pub/Sub metrics: Event publish success rate, consumer lag
- Jobs API metrics: Job execution count, execution duration
- Resource usage: Sidecar memory/CPU consumption
- CloudEvents tracing: Correlation IDs for end-to-end flow tracking

### CloudEvents Compatibility

Dapr wraps events in CloudEvents 1.0 format by default. Example structure:

```json
{
  "specversion": "1.0",
  "id": "unique-event-id",
  "source": "backend",
  "type": "TaskCreatedEvent",
  "time": "2026-01-15T12:00:00Z",
  "data": {
    "user_id": 1,
    "task_id": 123,
    "title": "Complete project"
  }
}
```

Consumer endpoints receive this structure and must extract the `data` field. Alternatively, use `rawPayload: true` metadata to disable CloudEvents wrapping.
