Dapr Integration Plan for Phase V

 Part B Features: Migrating Event-Driven Architecture to Dapr

 Branch: integration-of-dapr
 Features: 004-dapr-foundation, 005-dapr-migration
 Goal: Seamless migration from direct Kafka clients (aiokafka) to Dapr-based infrastructure while maintaining 100%
 functional equivalence

 ---
 Executive Summary

 This plan migrates Phase V's event-driven architecture from direct Kafka clients to Dapr's distributed application runtime.
  Current implementation uses aiokafka with SASL_SSL authentication, background thread publishing, and 3 Kafka consumer
 services. After migration, services will use Dapr's Pub/Sub HTTP API, gaining portability across cloud providers while
 maintaining identical functionality.

 Current State (Features 001-003 ✅ COMPLETE):
 - ✅ Enhanced database schema with priority, categories, tags, due dates, recurrence
 - ✅ 17 MCP tools for task management
 - ✅ Kafka event streaming with 3 topics (task-events, task-reminders, task-recurrence)
 - ✅ 3 consumer services: Notification (DB poller), Email Delivery (SMTP), Recurring Task (RRULE)
 - ✅ ChatKit UI with enhanced prompts

 Target State (Features 004-005):
 - Dapr runtime deployed on Kubernetes with 4 components
 - All Kafka producers migrated to Dapr Pub/Sub HTTP API
 - All Kafka consumers migrated to Dapr declarative subscriptions
 - Notification service polling replaced with Dapr Jobs API
 - Zero functional regressions, same performance characteristics

 ---
 Migration Strategy: Infrastructure-First Phased Approach

 Phase 1: Infrastructure Foundation (Feature 004 - 4 hours)

 Goal: Deploy Dapr without code changes

 1. Install Dapr CLI and initialize on Kubernetes (dapr init -k)
 2. Create 4 Dapr component YAMLs
 3. Verify components deployed and healthy
 4. Risk: Zero - existing services continue using aiokafka

 Phase 2: Code Migration (Feature 005 - 16 hours)

 Goal: Replace aiokafka with Dapr HTTP API

 1. Create Dapr HTTP client wrapper
 2. Migrate producers (backend + notification service)
 3. Migrate consumers (email + recurring services)
 4. Replace notification polling with Dapr Jobs API
 5. Update Kubernetes deployments with Dapr annotations
 6. Remove aiokafka dependencies

 ---
 Dapr Component Configurations

 1. Pub/Sub Component (Kafka)

 File: phaseV/kubernetes/dapr-components/pubsub-kafka.yaml

 apiVersion: dapr.io/v1alpha1
 kind: Component
 metadata:
   name: pubsub-kafka
   namespace: todo-phasev
 spec:
   type: pubsub.kafka
   version: v1
   metadata:
     # Redpanda Cloud brokers
     - name: brokers
       value: "{{ KAFKA_BOOTSTRAP_SERVERS }}"

     # SASL/SCRAM-SHA-256 authentication
     - name: authType
       value: "sasl"
     - name: saslMechanism
       value: "SCRAM-SHA-256"
     - name: saslUsername
       secretKeyRef:
         name: todo-app-secrets
         key: KAFKA_SASL_USERNAME
     - name: saslPassword
       secretKeyRef:
         name: todo-app-secrets
         key: KAFKA_SASL_PASSWORD

     # TLS configuration
     - name: enableTLS
       value: "true"
     - name: skipVerify
       value: "false"

     # Producer configuration
     - name: producerIdempotence
       value: "true"
     - name: compressionType
       value: "gzip"
     - name: requiredAcks
       value: "all"

     # Consumer configuration
     - name: consumerFetchDefault
       value: "1048576"
     - name: channelBufferSize
       value: "10"
     - name: initialOffset
       value: "oldest"
     - name: version
       value: "2.8.0"
 scopes:
   - backend
   - notification-service
   - email-delivery-service
   - recurring-task-service

 Key Features:
 - Matches current SASL_SSL + SCRAM-SHA-256 authentication
 - Preserves idempotency and at-least-once delivery guarantees
 - CloudEvents format for standardized message wrapping

 2. State Store Component (PostgreSQL)

 File: phaseV/kubernetes/dapr-components/statestore-postgres.yaml

 apiVersion: dapr.io/v1alpha1
 kind: Component
 metadata:
   name: statestore-postgres
   namespace: todo-phasev
 spec:
   type: state.postgresql
   version: v2
   metadata:
     - name: connectionString
       secretKeyRef:
         name: todo-app-secrets
         key: POSTGRES_CONNECTION_STRING
     - name: tableName
       value: "dapr_state_store"
     - name: metadataTableName
       value: "dapr_state_metadata"
     - name: cleanupInterval
       value: "3600"
     - name: timeout
       value: "30s"
     - name: maxConns
       value: "10"
 scopes:
   - notification-service

 Use Case: Track notification service polling state for idempotency

 3. Secrets Component (Kubernetes)

 File: phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml

 apiVersion: dapr.io/v1alpha1
 kind: Component
 metadata:
   name: kubernetes-secrets
   namespace: todo-phasev
 spec:
   type: secretstores.kubernetes
   version: v1
 scopes:
   - backend
   - notification-service
   - email-delivery-service
   - recurring-task-service

 Use Case: Centralized secret access via Dapr API

 4. Jobs Scheduler Component (Etcd)

 File: phaseV/kubernetes/dapr-components/jobs-scheduler.yaml

 apiVersion: dapr.io/v1alpha1
 kind: Component
 metadata:
   name: jobs-scheduler
   namespace: todo-phasev
 spec:
   type: scheduler.etcd
   version: v1
   metadata:
     - name: endpoints
       value: "dapr-scheduler.dapr-system.svc.cluster.local:2379"
     - name: enablePersistence
       value: "true"
     - name: defaultJobTTL
       value: "86400"
 scopes:
   - notification-service

 Use Case: Replace 5-second DB polling loop with scheduled jobs
 - Guarantees single execution across replicas (no duplicate reminders)

 ---
 Code Migration Approach

 1. Create Dapr HTTP Client Wrapper

 New File: phaseV/backend/app/dapr/client.py

 """Dapr HTTP client wrapper for pub/sub and state management."""
 import httpx
 from typing import Any, Dict, Optional

 class DaprClient:
     def __init__(self, dapr_http_port: int = 3500):
         self.base_url = f"http://localhost:{dapr_http_port}"
         self.client = httpx.AsyncClient(timeout=30.0)

     async def publish_event(
         self,
         pubsub_name: str,
         topic: str,
         data: Dict[str, Any],
         metadata: Optional[Dict[str, str]] = None
     ) -> bool:
         """Publish event to Kafka via Dapr Pub/Sub API."""
         url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"
         headers = {"Content-Type": "application/json"}

         if metadata:
             headers.update({f"ce-{k}": v for k, v in metadata.items()})

         response = await self.client.post(url, json=data, headers=headers)
         response.raise_for_status()
         return True

     async def save_state(self, store_name: str, key: str, value: Any) -> bool:
         """Save state to PostgreSQL via Dapr State API."""
         url = f"{self.base_url}/v1.0/state/{store_name}"
         response = await self.client.post(url, json=[{"key": key, "value": value}])
         response.raise_for_status()
         return True

 dapr_client = DaprClient()

 2. Producer Migration Pattern

 Current (aiokafka):
 # phaseV/backend/app/mcp/tools.py (multiple locations)
 await kafka_producer.publish_event(
     topic="task-events",
     event=TaskCreatedEvent(...),
     key=str(task.id),
     wait=False
 )

 New (Dapr):
 await dapr_client.publish_event(
     pubsub_name="pubsub-kafka",
     topic="task-events",
     data=event.model_dump(),
     metadata={"partitionKey": str(task.id)}
 )

 Files to Modify:
 - phaseV/backend/app/main.py - Remove kafka_producer startup/shutdown
 - phaseV/backend/app/mcp/tools.py - Replace all publish_event calls
 - phaseV/backend/app/services/notification_service.py - Replace ReminderSentEvent publishing
 - phaseV/backend/app/services/recurring_task_service.py - Replace TaskCreatedEvent publishing

 3. Consumer Migration Pattern

 Create Declarative Subscriptions:

 File: phaseV/kubernetes/dapr-subscriptions/email-delivery-sub.yaml
 apiVersion: dapr.io/v2alpha1
 kind: Subscription
 metadata:
   name: email-delivery-subscription
   namespace: todo-phasev
 spec:
   pubsubname: pubsub-kafka
   topic: task-reminders
   routes:
     default: /events/reminder-sent
   scopes:
     - email-delivery-service
   bulkSubscribe:
     enabled: true
     maxMessagesCount: 10
     maxAwaitDurationMs: 1000

 Add HTTP Endpoints:

 # phaseV/backend/app/services/email_delivery_service_standalone.py

 @app.get("/dapr/subscribe")
 async def dapr_subscriptions():
     """Dapr pub/sub subscription configuration."""
     return [{
         "pubsubname": "pubsub-kafka",
         "topic": "task-reminders",
         "route": "/events/reminder-sent"
     }]

 @app.post("/events/reminder-sent")
 async def handle_reminder_event(request: Request):
     """Process ReminderSentEvent from Dapr."""
     cloud_event = await request.json()
     event_data = cloud_event.get("data", {})
     event = ReminderSentEvent(**event_data)

     await email_delivery_service._process_reminder(event)
     return {"status": "SUCCESS"}  # 200 OK = commit offset

 Files to Modify:
 - phaseV/backend/app/services/email_delivery_service.py - Remove AIOKafkaConsumer, add HTTP endpoints
 - phaseV/backend/app/services/email_delivery_service_standalone.py - Add Dapr subscription endpoints
 - phaseV/backend/app/services/recurring_task_service.py - Remove AIOKafkaConsumer, add HTTP endpoints
 - phaseV/backend/app/services/recurring_task_service_standalone.py - Add Dapr subscription endpoints

 4. Notification Service: Polling → Jobs API

 Current Pattern: Async polling loop (lines 99-117 in notification_service.py)

 New Pattern:

 # Register job on startup
 async def register_reminder_job():
     job_config = {
         "name": "check-due-tasks",
         "schedule": "@every 5s",
         "repeats": -1,
         "dueTime": "0s",
         "data": {}
     }
     url = "http://localhost:3500/v1.0-alpha1/jobs/jobs-scheduler/check-due-tasks"
     async with httpx.AsyncClient() as client:
         await client.put(url, json=job_config)

 # Job handler endpoint
 @app.post("/jobs/check-due-tasks")
 async def handle_check_due_tasks():
     await notification_service._process_reminders()
     return {"status": "SUCCESS"}

 Benefits:
 - Dapr guarantees single execution across replicas
 - No duplicate reminders even with multiple pods
 - Automatic retry on failure

 Files to Modify:
 - phaseV/backend/app/services/notification_service.py - Remove async loop (lines 99-117)
 - phaseV/backend/app/services/notification_service_standalone.py - Add job registration and handler

 ---
 Kubernetes Deployment Updates

 Add Dapr Annotations to All Services

 Pattern for notification-deployment.yaml:
 apiVersion: apps/v1
 kind: Deployment
 metadata:
   name: notification-service
   namespace: todo-phasev
 spec:
   template:
     metadata:
       annotations:
         dapr.io/enabled: "true"
         dapr.io/app-id: "notification-service"
         dapr.io/app-port: "8002"
         dapr.io/app-protocol: "http"
         dapr.io/sidecar-cpu-limit: "200m"
         dapr.io/sidecar-memory-limit: "256Mi"
         dapr.io/log-level: "info"
         dapr.io/enable-metrics: "true"

 Apply to:
 - backend-deployment.yaml - Add dapr.io/app-id: "backend"
 - notification-deployment.yaml - Add dapr.io/app-id: "notification-service"
 - email-delivery-deployment.yaml - Add dapr.io/app-id: "email-delivery-service"
 - recurring-deployment.yaml - Add dapr.io/app-id: "recurring-task-service"

 Remove Kafka Environment Variables

 Delete from all deployments:
 - name: KAFKA_BOOTSTRAP_SERVERS  # ❌ REMOVE
 - name: KAFKA_SASL_USERNAME      # ❌ REMOVE
 - name: KAFKA_SASL_PASSWORD      # ❌ REMOVE
 - name: KAFKA_SECURITY_PROTOCOL  # ❌ REMOVE
 - name: KAFKA_SASL_MECHANISM     # ❌ REMOVE

 Keep:
 - name: DATABASE_URL  # ✅ KEEP

 Remove aiokafka Dependency

 File: phaseV/backend/requirements.txt
 - aiokafka==0.11.0

 ---
 Testing Strategy

 1. Unit Tests

 New File: phaseV/backend/tests/test_dapr_migration.py

 @pytest.mark.asyncio
 async def test_publish_event_via_dapr():
     """Verify Dapr publishes CloudEvents format."""
     event = TaskCreatedEvent(user_id=1, task_id=123, title="Test")
     result = await dapr_client.publish_event(
         pubsub_name="pubsub-kafka",
         topic="task-events",
         data=event.model_dump()
     )
     assert result is True

 2. Integration Tests

 Scenario 1: End-to-End Reminder Flow
 1. Create task with due_date = now + 30 minutes
 2. Wait for Dapr job trigger (5s)
 3. Verify ReminderSentEvent published
 4. Verify email sent via SMTP
 5. Verify Kafka offset committed

 Scenario 2: Recurring Task Flow
 1. Create task with recurrence_rule = "FREQ=DAILY"
 2. Mark task completed
 3. Verify TaskCompletedEvent published
 4. Verify new task created
 5. Verify no duplicate tasks

 Scenario 3: Idempotency
 1. Publish same event twice
 2. Verify only one processing

 3. Performance Validation

 Metrics:
 - Pub/sub latency < 100ms (baseline)
 - Consumer throughput 10 msg/batch (baseline)
 - Memory overhead < 128MB per Dapr sidecar
 - No consumer rebalance storms

 ---
 Rollback Plan

 If Migration Fails

 Indicators:
 - Dapr sidecar crash loops
 - Message delivery failures > 5%
 - Latency spikes > 2x baseline

 Rollback Steps:

 1. Revert Kubernetes Deployments (2 min)
 kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/backend-deployment.yaml.backup
 kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml.backup
 kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/email-delivery-deployment.yaml.backup
 kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/recurring-deployment.yaml.backup

 2. Revert Code (Git)
 git checkout <pre-migration-commit-sha>
 docker build -t todo-app-backend:rollback phaseV/backend
 kubectl set image deployment/backend backend=todo-app-backend:rollback -n todo-phasev

 3. Remove Dapr Components
 kubectl delete -f phaseV/kubernetes/dapr-components/

 4. Verify Rollback
 - Check kafka_producer health: /health/kafka
 - Verify consumer offsets progressing
 - Monitor for 1 hour

 Data Integrity:
 - No data loss: Same Kafka topics, no schema changes
 - Consumer group IDs unchanged (offset preservation)
 - No Dapr-specific database tables created

 ---
 Risk Mitigation

 Critical Risks & Contingencies

 Risk 1: CloudEvents Format Incompatibility
 - Impact: Consumers can't parse Dapr-wrapped CloudEvents
 - Mitigation: Test with single consumer first, use rawPayload: true if needed
 - Fallback: Custom CloudEvents unwrapper in consumer

 Risk 2: Dapr Sidecar Crash Loops
 - Impact: Service pods unhealthy, no event processing
 - Mitigation: Increase sidecar resources (500m CPU), enable debug logging
 - Fallback: Disable Dapr for specific service, use hybrid mode

 Risk 3: Kafka Authentication Failures
 - Impact: Dapr can't connect to Redpanda Cloud
 - Mitigation: Test component with dapr run locally first, verify secret refs
 - Fallback: Use direct Kafka client for affected service

 Risk 4: Jobs API Unavailable
 - Impact: Notification service polling broken
 - Mitigation: Verify Dapr Scheduler running: kubectl get pods -n dapr-system
 - Fallback: Keep async loop as backup, feature flag to switch

 Risk 5: Duplicate Reminders
 - Impact: Users receive multiple emails
 - Mitigation: Verify consumer group IDs preserved, add idempotency tracking in state store
 - Fallback: Add reminder_sent flag check in email service

 ---
 Implementation Task Breakdown

 Feature 004: Dapr Foundation (4 hours)

 Task 004-1: Install Dapr Runtime (30 min)
 - Install Dapr CLI
 - Run dapr init -k on Kubernetes
 - Verify Dapr system pods running
 - Acceptance: dapr status -k shows healthy

 Task 004-2: Create Pub/Sub Component (1 hour)
 - Create pubsub-kafka.yaml
 - Apply to cluster
 - Test with dapr publish CLI
 - Acceptance: Component visible in dapr components -k

 Task 004-3: Create State Store Component (1 hour)
 - Create statestore-postgres.yaml
 - Create Postgres connection secret
 - Apply and test
 - Acceptance: State saved in dapr_state_store table

 Task 004-4: Create Secrets Component (30 min)
 - Create secrets-kubernetes.yaml
 - Apply and test secret retrieval
 - Acceptance: Secrets accessible via Dapr API

 Task 004-5: Create Jobs Scheduler Component (1 hour)
 - Create jobs-scheduler.yaml
 - Verify Dapr Scheduler healthy
 - Create test job
 - Acceptance: Job executes on schedule

 Feature 005: Code Migration (16 hours)

 Task 005-1: Create Dapr HTTP Client (2 hours)
 - Implement DaprClient in app/dapr/client.py
 - Add publish_event, save_state, get_state
 - Write unit tests
 - Acceptance: All methods work

 Task 005-2: Migrate Producer - Backend (3 hours)
 - Replace kafka_producer with dapr_client
 - Update MCP tools publish calls
 - Update main.py lifespan
 - Acceptance: TaskCreatedEvent published via Dapr

 Task 005-3: Migrate Producer - Notification Service (2 hours)
 - Update notification_service.py publish calls
 - Replace Kafka producer with Dapr
 - Acceptance: ReminderSentEvent published via Dapr

 Task 005-4: Migrate Consumer - Email Delivery (4 hours)
 - Remove AIOKafkaConsumer
 - Add Dapr subscription endpoints
 - Create declarative subscription YAML
 - Test email flow
 - Acceptance: Emails sent, offsets committed

 Task 005-5: Migrate Consumer - Recurring Task (4 hours)
 - Remove AIOKafkaConsumer
 - Add Dapr subscription endpoints
 - Create declarative subscription YAML
 - Test recurring task creation
 - Acceptance: New tasks created, events published

 Task 005-6: Notification Service Jobs Migration (1 hour)
 - Replace polling loop with Dapr job registration
 - Add job handler endpoint
 - Acceptance: Reminders processed every 5s, no duplicates

 Task 005-7: Kubernetes Deployment Updates (4 hours)
 - Add Dapr annotations to all deployments
 - Remove Kafka environment variables
 - Update resource limits for sidecars
 - Remove aiokafka from requirements.txt
 - Rebuild and push Docker images
 - Run integration tests
 - Acceptance: All tests pass, no functional regressions

 ---
 Validation Checklist

 Pre-Deployment

 - Dapr components created and applied
 - Dapr system pods healthy (operator, sidecar-injector, scheduler)
 - Kafka component connects to Redpanda Cloud
 - State store creates PostgreSQL tables
 - Secrets accessible via Dapr API

 Post-Deployment

 - All pods show 2/2 containers ready (app + sidecar)
 - Dapr sidecar logs show "Dapr Runtime started"
 - Task creation publishes events (CloudEvents format)
 - Notification job registered with scheduler
 - Email service subscribes to task-reminders
 - Recurring service subscribes to task-recurrence
 - Consumer offsets progress (check Kafka lag)

 Functional

 - Create task → TaskCreatedEvent published
 - Task due in 30 min → Email sent
 - Mark recurring task complete → New task created
 - No duplicate reminders (test with 2 replicas)
 - Graceful shutdown (30s termination)

 Performance

 - Pub/sub latency < 100ms
 - Consumer throughput 10 msg/batch
 - Memory overhead < 128MB per sidecar
 - No rebalance storms

 ---
 Critical Files for Implementation

 Code Files

 1. phaseV/backend/app/kafka/producer.py (441 lines) - Replace with Dapr HTTP calls
 2. phaseV/backend/app/services/notification_service.py (lines 99-117, 201-203) - Jobs API migration
 3. phaseV/backend/app/services/email_delivery_service.py (lines 95-109, 216-278) - Consumer migration
 4. phaseV/backend/app/main.py (lines 58-63, 74-78) - Kafka lifecycle removal

 Kubernetes Files

 5. phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml - Dapr annotations pattern
 6. phaseV/kubernetes/helm/todo-app/templates/backend-deployment.yaml - Dapr annotations
 7. phaseV/kubernetes/helm/todo-app/templates/email-delivery-deployment.yaml - Dapr annotations
 8. phaseV/kubernetes/helm/todo-app/templates/recurring-deployment.yaml - Dapr annotations

 New Files to Create

 9. phaseV/backend/app/dapr/client.py - Dapr HTTP client wrapper
 10. phaseV/kubernetes/dapr-components/pubsub-kafka.yaml - Kafka component
 11. phaseV/kubernetes/dapr-components/statestore-postgres.yaml - State store
 12. phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml - Secrets
 13. phaseV/kubernetes/dapr-components/jobs-scheduler.yaml - Jobs scheduler
 14. phaseV/kubernetes/dapr-subscriptions/email-delivery-sub.yaml - Email subscription
 15. phaseV/kubernetes/dapr-subscriptions/recurring-task-sub.yaml - Recurring subscription

 ---
 References

 Dapr Official Documentation (2026)

 - https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-overview/
 - https://docs.dapr.io/developing-applications/building-blocks/state-management/state-management-overview/
 - https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/
 - https://docs.dapr.io/getting-started/tutorials/configure-state-pubsub/
 - https://docs.dapr.io/getting-started/quickstarts/pubsub-quickstart/

 Project Documentation

 - /home/salim/Desktop/hackathon-II-todo-app/docs/PHASE_V_FEATURE_BREAKDOWN.md - Feature requirements
 - /home/salim/Desktop/hackathon-II-todo-app/phaseV/ARCHITECTURE_FLOW.md - Current architecture
 - /home/salim/Desktop/hackathon-II-todo-app/.specify/memory/constitution.md - Phase V governance

 ---
 Next Steps After Plan Approval

 1. Create feature branch: git checkout -b 004-dapr-foundation
 2. Install Dapr CLI and initialize on Kubernetes
 3. Create all 4 Dapr component YAMLs
 4. Test components with Dapr CLI tools
 5. Merge Feature 004, create branch for Feature 005
 6. Implement Dapr HTTP client wrapper
 7. Migrate producers and consumers incrementally
 8. Update Kubernetes deployments with annotations
 9. Run comprehensive integration tests
 10. Create PR with complete test results

 ---
 Estimated Total Effort: 20 hours (4 hours infrastructure + 16 hours code migration)
 Risk Level: Medium (well-documented migration path, comprehensive rollback plan)
 Success Criteria: 100% functional equivalence with current Feature 002, all integration tests passing
