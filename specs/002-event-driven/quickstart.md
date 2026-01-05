# Quickstart Guide: Event-Driven Architecture

**Feature**: 002-event-driven
**Audience**: Developers implementing this feature
**Date**: 2026-01-01

## Prerequisites

Before starting implementation, ensure you have:

1. ✅ **Feature 001 (Foundation + API Layer) completed**:
   - Enhanced `tasks_phaseiii` table with `priority`, `due_date`, `category_id`
   - Database trigger for `search_vector` auto-update
   - GIN index on `search_vector`
   - 17 MCP tools (5 basic + 12 advanced)

2. ✅ **Redpanda Cloud cluster provisioned**:
   - Serverless free tier account created
   - Bootstrap server URL obtained
   - SASL/SCRAM credentials generated
   - Network connectivity from Kubernetes pods verified

3. ✅ **Development environment**:
   - Python 3.11+ with `uv` package manager
   - PostgreSQL client (psql) for schema verification
   - kubectl + Minikube for local Kubernetes
   - kafkacat (optional) for Kafka topic inspection

---

## Step 1: Database Migration

### Add Event-Driven Fields

Create Alembic migration to add `recurrence_rule` and `reminder_sent` fields:

```bash
cd phaseV/backend
uv run alembic revision -m "add event driven fields"
```

Edit the generated migration file:

```python
# alembic/versions/YYYYMMDD_add_event_driven_fields.py

def upgrade():
    # Add recurrence_rule field
    op.add_column('tasks_phaseiii',
        sa.Column('recurrence_rule', sa.String(), nullable=True)
    )

    # Add reminder_sent field
    op.add_column('tasks_phaseiii',
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false')
    )

    # Create index for reminder queries
    op.create_index('idx_tasks_reminder_sent', 'tasks_phaseiii', ['reminder_sent'])

    # Composite index for efficient reminder polling
    op.execute("""
        CREATE INDEX idx_tasks_reminder_query
        ON tasks_phaseiii(due_date, reminder_sent, completed)
        WHERE deleted_at IS NULL;
    """)

def downgrade():
    op.drop_index('idx_tasks_reminder_query', 'tasks_phaseiii')
    op.drop_index('idx_tasks_reminder_sent', 'tasks_phaseiii')
    op.drop_column('tasks_phaseiii', 'reminder_sent')
    op.drop_column('tasks_phaseiii', 'recurrence_rule')
```

Run migration:

```bash
uv run alembic upgrade head
```

Verify:

```sql
\d tasks_phaseiii
-- Should show recurrence_rule (text) and reminder_sent (boolean) columns
-- Should show idx_tasks_reminder_sent and idx_tasks_reminder_query indexes
```

---

## Step 2: Kafka Integration Setup

### Install Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "aiokafka>=0.11.0",           # NEW: Kafka client
    "python-dateutil>=2.8.2",     # NEW: RRULE parsing
    "pydantic>=2.5.0",
]
```

Install:

```bash
uv sync
```

### Create Kafka Configuration

Create `app/kafka/config.py`:

```python
from pydantic_settings import BaseSettings

class KafkaConfig(BaseSettings):
    bootstrap_servers: str
    sasl_username: str
    sasl_password: str
    security_protocol: str = "SASL_SSL"
    sasl_mechanism: str = "SCRAM-SHA-256"

    class Config:
        env_file = ".env"
        env_prefix = "KAFKA_"

kafka_config = KafkaConfig()
```

Add to `.env`:

```env
# Kafka Configuration (Redpanda Cloud)
KAFKA_BOOTSTRAP_SERVERS=<cluster-id>.c.redpanda.cloud:9092
KAFKA_SASL_USERNAME=<username>
KAFKA_SASL_PASSWORD=<password>
```

---

## Step 3: Define Event Schemas

Create `app/kafka/events.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, List

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int
    schema_version: str = "1.0"

class TaskCreatedEvent(BaseEvent):
    event_type: str = "task.created"
    task_id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)

class TaskCompletedEvent(BaseEvent):
    event_type: str = "task.completed"
    task_id: int
    recurrence_rule: Optional[str] = None
    completed_at: datetime

class TaskUpdatedEvent(BaseEvent):
    event_type: str = "task.updated"
    task_id: int
    updated_fields: dict

class TaskDeletedEvent(BaseEvent):
    event_type: str = "task.deleted"
    task_id: int

class ReminderSentEvent(BaseEvent):
    event_type: str = "reminder.sent"
    task_id: int
    reminder_time: datetime
```

---

## Step 4: Implement Kafka Producer

Create `app/kafka/producer.py`:

```python
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from app.kafka.config import kafka_config
from app.kafka.events import BaseEvent
import logging

logger = logging.getLogger(__name__)

class KafkaProducerManager:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            security_protocol=kafka_config.security_protocol,
            sasl_mechanism=kafka_config.sasl_mechanism,
            sasl_plain_username=kafka_config.sasl_username,
            sasl_plain_password=kafka_config.sasl_password,
            acks=1,
            enable_idempotence=True,
            compression_type='gzip'
        )
        await self.producer.start()
        await self._create_topics()

    async def _create_topics(self):
        admin = AIOKafkaAdminClient(
            bootstrap_servers=kafka_config.bootstrap_servers,
            security_protocol=kafka_config.security_protocol,
            sasl_mechanism=kafka_config.sasl_mechanism,
            sasl_plain_username=kafka_config.sasl_username,
            sasl_plain_password=kafka_config.sasl_password
        )
        await admin.start()

        topics = [
            NewTopic(name='task-events', num_partitions=3, replication_factor=1,
                    topic_configs={'retention.ms': '604800000'}),
            NewTopic(name='task-reminders', num_partitions=1, replication_factor=1,
                    topic_configs={'retention.ms': '86400000'}),
            NewTopic(name='task-recurrence', num_partitions=1, replication_factor=1,
                    topic_configs={'retention.ms': '604800000'})
        ]

        try:
            await admin.create_topics(topics, validate_only=False)
            logger.info("Kafka topics created successfully")
        except Exception as e:
            logger.warning(f"Topic creation failed (may already exist): {e}")
        finally:
            await admin.close()

    async def publish(self, topic: str, event: BaseEvent, key: str):
        try:
            await self.producer.send(
                topic,
                value=event.model_dump_json().encode('utf-8'),
                key=key.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            # Fire-and-forget: don't raise, just log

    async def stop(self):
        if self.producer:
            await self.producer.stop()

# Global producer instance
kafka_producer = KafkaProducerManager()
```

---

## Step 5: Enhance MCP Tools with Event Publishing

Modify `app/mcp/tools.py` to publish events:

```python
from app.kafka.producer import kafka_producer
from app.kafka.events import TaskCreatedEvent, TaskCompletedEvent, TaskUpdatedEvent, TaskDeletedEvent

@mcp_server.tool()
async def add_task(
    user_id: int,
    title: str,
    priority: Optional[str] = None,
    due_date: Optional[datetime] = None,
    recurrence_rule: Optional[str] = None,
    # ... other params
):
    # 1. Validate recurrence_rule if provided
    if recurrence_rule and not validate_rrule(recurrence_rule):
        return {"error": "Invalid recurrence rule"}

    # 2. Create task in database
    task = Task(
        user_id=user_id,
        title=title,
        priority=priority,
        due_date=due_date,
        recurrence_rule=recurrence_rule
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 3. Publish TaskCreatedEvent (async, non-blocking)
    event = TaskCreatedEvent(
        user_id=user_id,
        task_id=task.id,
        title=title,
        priority=priority,
        due_date=due_date,
        recurrence_rule=recurrence_rule
    )
    await kafka_producer.publish('task-events', event, key=str(task.id))

    # 4. Return success immediately
    return {"success": True, "task_id": task.id}
```

**Repeat for `complete_task`, `update_task`, `delete_task`**.

---

## Step 6: Implement Notification Service

Create `app/services/notification_service.py`:

```python
import asyncio
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from app.models.task import Task
from app.database import get_db
from app.kafka.producer import kafka_producer
from app.kafka.events import ReminderSentEvent
import logging

logger = logging.getLogger(__name__)

async def notification_service_loop():
    """Poll database every 5 seconds for tasks needing reminders"""
    while True:
        try:
            async for db in get_db():
                # Query tasks due within next hour that haven't been reminded
                stmt = (
                    select(Task)
                    .where(
                        Task.due_date <= datetime.now(timezone.utc) + timedelta(hours=1),
                        Task.reminder_sent == False,
                        Task.completed == False,
                        Task.deleted_at.is_(None)
                    )
                )
                result = await db.execute(stmt)
                tasks = result.scalars().all()

                for task in tasks:
                    # Atomic update to prevent duplicate reminders
                    update_stmt = (
                        update(Task)
                        .where(Task.id == task.id, Task.reminder_sent == False)
                        .values(reminder_sent=True)
                    )
                    result = await db.execute(update_stmt)
                    await db.commit()

                    if result.rowcount > 0:
                        # Only log if we successfully updated (prevents duplicate reminders)
                        minutes = int((task.due_date - datetime.now(timezone.utc)).total_seconds() / 60)
                        logger.info(f"🔔 REMINDER: Task '{task.title}' (ID: {task.id}) due in {minutes} minutes")

                        # Publish ReminderSentEvent
                        event = ReminderSentEvent(
                            user_id=task.user_id,
                            task_id=task.id,
                            reminder_time=datetime.now(timezone.utc)
                        )
                        await kafka_producer.publish('task-reminders', event, key=str(task.id))

        except Exception as e:
            logger.error(f"Notification service error: {e}")

        await asyncio.sleep(5)  # Poll every 5 seconds
```

---

## Step 7: Implement Recurring Task Service

Create `app/services/recurring_task_service.py`:

```python
from aiokafka import AIOKafkaConsumer
from dateutil.rrule import rrulestr
from datetime import datetime, timezone
from app.kafka.config import kafka_config
from app.kafka.events import TaskCompletedEvent, TaskCreatedEvent
from app.models.task import Task
from app.database import get_db
from app.kafka.producer import kafka_producer
import logging

logger = logging.getLogger(__name__)

async def recurring_task_service_loop():
    """Consume TaskCompletedEvent and create next recurring task"""
    consumer = AIOKafkaConsumer(
        'task-recurrence',
        bootstrap_servers=kafka_config.bootstrap_servers,
        security_protocol=kafka_config.security_protocol,
        sasl_mechanism=kafka_config.sasl_mechanism,
        sasl_plain_username=kafka_config.sasl_username,
        sasl_plain_password=kafka_config.sasl_password,
        group_id='recurring-task-service-group',
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    await consumer.start()
    try:
        async for msg in consumer:
            try:
                event = TaskCompletedEvent.model_validate_json(msg.value)

                if not event.recurrence_rule:
                    await consumer.commit()
                    continue

                # Parse RRULE and calculate next occurrence
                rrule = rrulestr(event.recurrence_rule, dtstart=event.completed_at)
                next_occurrence = rrule.after(event.completed_at, inc=False)

                # Skip if next occurrence is in the past
                if not next_occurrence or next_occurrence < datetime.now(timezone.utc):
                    logger.warning(f"Skipping recurring task {event.task_id}: next occurrence in past")
                    await consumer.commit()
                    continue

                # Fetch original task to copy metadata
                async for db in get_db():
                    original_task = await db.get(Task, event.task_id)
                    if not original_task:
                        logger.error(f"Original task {event.task_id} not found")
                        await consumer.commit()
                        continue

                    # Create new task with next occurrence
                    new_task = Task(
                        user_id=original_task.user_id,
                        title=original_task.title,
                        description=original_task.description,
                        priority=original_task.priority,
                        category_id=original_task.category_id,
                        recurrence_rule=original_task.recurrence_rule,
                        due_date=next_occurrence,
                        completed=False,
                        reminder_sent=False
                    )
                    db.add(new_task)
                    await db.commit()
                    await db.refresh(new_task)

                    logger.info(f"Created recurring task {new_task.id} for {next_occurrence}")

                    # Publish TaskCreatedEvent
                    created_event = TaskCreatedEvent(
                        user_id=new_task.user_id,
                        task_id=new_task.id,
                        title=new_task.title,
                        due_date=new_task.due_date,
                        recurrence_rule=new_task.recurrence_rule
                    )
                    await kafka_producer.publish('task-events', created_event, key=str(new_task.id))

                await consumer.commit()

            except Exception as e:
                logger.error(f"Failed to process recurring task event: {e}")
                continue

    finally:
        await consumer.stop()
```

---

## Step 8: Add Service Startup

Modify `app/main.py` to start Kafka producer and consumer services:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.kafka.producer import kafka_producer
from app.services.notification_service import notification_service_loop
from app.services.recurring_task_service import recurring_task_service_loop
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await kafka_producer.start()
    asyncio.create_task(notification_service_loop())
    asyncio.create_task(recurring_task_service_loop())
    yield
    # Shutdown
    await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)
```

---

## Step 9: Test Event Flow

### Unit Test: Event Publishing

```python
# tests/test_kafka_events.py
import pytest
from app.kafka.events import TaskCreatedEvent

def test_task_created_event_serialization():
    event = TaskCreatedEvent(
        user_id=1,
        task_id=101,
        title="Test task",
        priority="high"
    )
    json_str = event.model_dump_json()
    assert "task.created" in json_str
    assert "Test task" in json_str
```

### Integration Test: MCP Tool with Event

```python
# tests/test_mcp_tools.py
@pytest.mark.asyncio
async def test_add_task_publishes_event(db, kafka_producer_mock):
    result = await add_task(user_id=1, title="Test", priority="high")
    assert result["success"] == True

    # Verify event was published
    kafka_producer_mock.publish.assert_called_once()
    event = kafka_producer_mock.publish.call_args[0][1]
    assert event.event_type == "task.created"
```

---

## Step 10: Deploy to Kubernetes

### Add Kafka Credentials to Secrets

```bash
kubectl create secret generic kafka-credentials \
  --from-literal=bootstrap_servers=<cluster>.c.redpanda.cloud:9092 \
  --from-literal=sasl_username=<username> \
  --from-literal=sasl_password=<password> \
  -n todo-phasev
```

### Create Notification Service Deployment

`kubernetes/helm/todo-app/templates/notification-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
    spec:
      containers:
      - name: notification
        image: todo-backend:latest
        command: ["python", "-m", "app.services.notification_service"]
        envFrom:
        - secretRef:
            name: kafka-credentials
        - secretRef:
            name: database-credentials
```

---

## Testing Checklist

- [ ] Database migration applied (`recurrence_rule`, `reminder_sent` fields exist)
- [ ] Kafka topics created (`task-events`, `task-reminders`, `task-recurrence`)
- [ ] Event schemas validate correctly (Pydantic models)
- [ ] `add_task` publishes `TaskCreatedEvent`
- [ ] `complete_task` publishes `TaskCompletedEvent` to `task-recurrence`
- [ ] Notification Service polls database and logs reminders
- [ ] Recurring Task Service creates new task on completion
- [ ] Full-text search returns ranked results

---

## Next Steps

After completing this quickstart, proceed to `/sp.tasks` to generate the implementation task breakdown.
