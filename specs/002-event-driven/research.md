# Research: Event-Driven Architecture with Kafka

**Feature**: 002-event-driven
**Date**: 2026-01-01
**Status**: Complete

## Overview

This document consolidates research findings for implementing event-driven architecture with Kafka/Redpanda integration, recurring task automation with iCalendar RRULE parsing, and full-text search with PostgreSQL.

---

## 1. Kafka Client for Python (aiokafka)

### Decision: aiokafka 0.11.0

### Rationale
- **Async/await native**: Integrates seamlessly with FastAPI's async architecture
- **Production-ready**: Mature library with 4+ years of active development
- **Kafka-compatible**: Works with both Apache Kafka and Redpanda Cloud
- **API parity**: Mirrors kafka-python API with async support

### Key Features
- Async producer with configurable acknowledgments (acks=1, acks=all)
- Async consumer with consumer groups and offset management
- Connection pooling and automatic reconnection
- Built-in serialization support (JSON, Avro, Protobuf)
- Support for SASL/SCRAM authentication and TLS encryption

### Best Practices
1. **Producer Configuration**:
   ```python
   producer = AIOKafkaProducer(
       bootstrap_servers='bootstrap.redpanda.cloud:9092',
       security_protocol='SASL_SSL',
       sasl_mechanism='SCRAM-SHA-256',
       sasl_plain_username=username,
       sasl_plain_password=password,
       acks=1,  # At-least-once delivery
       enable_idempotence=True,  # Prevent duplicates on retry
       compression_type='gzip',  # Reduce network bandwidth
       max_request_size=1048576  # 1MB max message size
   )
   ```

2. **Consumer Configuration**:
   ```python
   consumer = AIOKafkaConsumer(
       'task-events',
       bootstrap_servers='bootstrap.redpanda.cloud:9092',
       security_protocol='SASL_SSL',
       sasl_mechanism='SCRAM-SHA-256',
       sasl_plain_username=username,
       sasl_plain_password=password,
       group_id='notification-service-group',
       auto_offset_reset='earliest',  # Start from beginning on first run
       enable_auto_commit=False,  # Manual commit for control
       max_poll_records=100  # Batch size for efficiency
   )
   ```

3. **Error Handling**:
   - Retry transient errors (network failures) with exponential backoff
   - Log and skip malformed messages (dead letter queue in future)
   - Gracefully handle broker unavailability (continue operation, log failures)

4. **Graceful Shutdown**:
   ```python
   async def shutdown(consumer, producer):
       await consumer.stop()
       await producer.stop()
   ```

### Alternatives Considered
- **kafka-python**: Synchronous, would block FastAPI event loop (rejected)
- **confluent-kafka-python**: C-based librdkafka wrapper, more complex setup (overkill for MVP)

### References
- aiokafka docs: https://aiokafka.readthedocs.io/en/stable/
- Redpanda Kafka compatibility: https://docs.redpanda.com/

---

## 2. Redpanda Cloud vs Self-Hosted Kafka

### Decision: Redpanda Cloud (Serverless Free Tier)

### Rationale
- **Zero operational overhead**: No ZooKeeper, no cluster management, no capacity planning
- **Cost-effective**: Free tier provides 10GB storage, sufficient for MVP (<10,000 events/day)
- **Kafka-compatible**: Works with aiokafka without code changes
- **Performance**: C++ implementation, lower latency than Java-based Kafka
- **SASL/SCRAM + TLS**: Built-in authentication and encryption

### Free Tier Limits (Serverless)
- 10 GB storage
- 10 MB/s ingress
- 30 MB/s egress
- Unlimited topics
- SASL/SCRAM authentication
- TLS encryption

### Topic Configuration Strategy
```python
# Programmatic topic creation via AdminClient
topics = [
    NewTopic(
        name='task-events',
        num_partitions=3,  # Parallel processing, ordered by task_id key
        replication_factor=1,  # Serverless manages replication
        config={'retention.ms': '604800000'}  # 7 days
    ),
    NewTopic(
        name='task-reminders',
        num_partitions=1,  # Sequential processing (reminder order)
        replication_factor=1,
        config={'retention.ms': '86400000'}  # 1 day
    ),
    NewTopic(
        name='task-recurrence',
        num_partitions=1,  # Sequential processing
        replication_factor=1,
        config={'retention.ms': '604800000'}  # 7 days
    )
]
```

### Connection Details
- **Bootstrap server**: `<cluster-id>.c.redpanda.cloud:9092`
- **Authentication**: SASL/SCRAM-SHA-256
- **Encryption**: TLS (mandatory)
- **Credentials**: Stored in Kubernetes Secrets

### Alternatives Considered
- **Self-hosted Kafka (Strimzi operator)**: Requires cluster resources, complex setup, maintenance burden (rejected for MVP)
- **AWS MSK**: Vendor lock-in, higher cost, overkill for MVP (rejected)
- **Redis Streams**: Not Kafka-compatible, different semantics (rejected for constitutional compliance)

### References
- Redpanda Cloud docs: https://docs.redpanda.com/current/deploy/deployment-option/cloud/
- Pricing: https://redpanda.com/pricing

---

## 3. iCalendar RRULE Parsing (python-dateutil)

### Decision: python-dateutil 2.8.2 (rrule module)

### Rationale
- **RFC 5545 compliant**: Implements iCalendar RRULE specification correctly
- **Battle-tested**: Used by Google Calendar, Outlook, and major calendar apps
- **Pythonic API**: Easy to use with datetime objects
- **Comprehensive support**: FREQ, COUNT, UNTIL, INTERVAL, BYDAY, BYMONTH, etc.

### Supported RRULE Patterns (Whitelist)
```python
from dateutil.rrule import rrulestr, DAILY, WEEKLY, MONTHLY, YEARLY

# Daily recurrence
"FREQ=DAILY"  # Every day
"FREQ=DAILY;INTERVAL=2"  # Every 2 days
"FREQ=DAILY;COUNT=30"  # 30 occurrences

# Weekly recurrence
"FREQ=WEEKLY;BYDAY=MO,WE,FR"  # Every Monday, Wednesday, Friday
"FREQ=WEEKLY;INTERVAL=2;BYDAY=TU"  # Every other Tuesday

# Monthly recurrence
"FREQ=MONTHLY;BYMONTHDAY=15"  # 15th of every month
"FREQ=MONTHLY;BYDAY=1MO"  # First Monday of each month

# Yearly recurrence
"FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"  # December 25th every year
```

### Best Practices
1. **Validation on Task Creation**:
   ```python
   ALLOWED_RRULE_PATTERNS = [
       r'^FREQ=DAILY',
       r'^FREQ=WEEKLY;BYDAY=[A-Z,]+',
       r'^FREQ=MONTHLY;BYMONTHDAY=\d+',
       r'^FREQ=YEARLY;BYMONTH=\d+;BYMONTHDAY=\d+'
   ]

   def validate_rrule(rule: str) -> bool:
       try:
           rrulestr(rule, dtstart=datetime.now())
           return any(re.match(p, rule) for p in ALLOWED_RRULE_PATTERNS)
       except ValueError:
           return False
   ```

2. **Calculate Next Occurrence**:
   ```python
   from dateutil.rrule import rrulestr

   def get_next_occurrence(rule: str, from_date: datetime) -> datetime | None:
       try:
           rrule = rrulestr(rule, dtstart=from_date)
           next_date = rrule.after(from_date, inc=False)

           # Skip if next occurrence is in the past
           if next_date and next_date < datetime.now(timezone.utc):
               return None

           return next_date
       except ValueError:
           return None  # Invalid rule, skip regeneration
   ```

3. **Error Handling**:
   - Catch `ValueError` for invalid RRULE formats
   - Log errors with task details for debugging
   - Skip event processing (don't create new task)
   - Optionally publish to dead-letter topic (future enhancement)

### RRULE Examples
- `FREQ=DAILY`: Daily standup meeting
- `FREQ=WEEKLY;BYDAY=MO`: Weekly team meeting every Monday
- `FREQ=MONTHLY;BYMONTHDAY=1`: Monthly report due on the 1st
- `FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=15`: Annual tax deadline (Jan 15)

### Alternatives Considered
- **rrule library (standalone)**: Less mature than dateutil (rejected)
- **Custom RRULE parser**: High complexity, error-prone, reinventing the wheel (rejected)

### References
- dateutil docs: https://dateutil.readthedocs.io/en/stable/rrule.html
- RFC 5545 spec: https://datatracker.ietf.org/doc/html/rfc5545

---

## 4. PostgreSQL Full-Text Search (tsvector + GIN Index)

### Decision: PostgreSQL built-in FTS with tsvector and GIN index

### Rationale
- **No external dependencies**: Built into PostgreSQL, no Elasticsearch/Solr needed
- **Fast for <10k tasks**: GIN index provides <200ms p95 for target dataset size
- **Integrated with SQLModel**: Direct queries via SQLAlchemy
- **Natural language support**: Stemming, stop words, ranking built-in
- **Maintenance-free**: Automatic via database trigger

### Implementation Strategy

1. **Database Schema**:
   ```sql
   -- Add search_vector column (tsvector)
   ALTER TABLE tasks_phaseiii ADD COLUMN search_vector tsvector;

   -- Create GIN index for fast lookups
   CREATE INDEX idx_tasks_search ON tasks_phaseiii USING GIN(search_vector);

   -- Trigger to auto-update search_vector on INSERT/UPDATE
   CREATE TRIGGER task_search_update
   BEFORE INSERT OR UPDATE ON tasks_phaseiii
   FOR EACH ROW EXECUTE FUNCTION
   tsvector_update_trigger(
       search_vector,
       'pg_catalog.english',
       title,
       description
   );
   ```

2. **Search Query** (SQLAlchemy):
   ```python
   from sqlalchemy import func, select

   async def search_tasks(
       db: AsyncSession,
       user_id: int,
       query: str
   ) -> List[Task]:
       # Convert query to tsquery (handles stemming, stop words)
       tsquery = func.plainto_tsquery('english', query)

       # Search with ranking (title matches ranked higher)
       stmt = (
           select(Task)
           .where(
               Task.user_id == user_id,
               Task.search_vector.op('@@')(tsquery)
           )
           .order_by(func.ts_rank(Task.search_vector, tsquery).desc())
           .limit(50)  # Pagination in future
       )

       result = await db.execute(stmt)
       return result.scalars().all()
   ```

3. **Performance Optimization**:
   - **Weighting**: Use setweight() to boost title matches over description
     ```sql
     setweight(to_tsvector('english', title), 'A') ||
     setweight(to_tsvector('english', coalesce(description, '')), 'B')
     ```
   - **Partial GIN index**: Only index non-deleted tasks
     ```sql
     CREATE INDEX idx_tasks_search_active
     ON tasks_phaseiii USING GIN(search_vector)
     WHERE deleted_at IS NULL;
     ```

4. **Query Features**:
   - **Stemming**: "running" matches "run", "runs", "runner"
   - **Stop words**: Automatically removes "the", "a", "is", "and"
   - **Phrase search**: Use `phraseto_tsquery` for exact phrases
   - **Prefix matching**: Use `to_tsquery` with `:*` suffix for autocomplete

### Scaling Considerations
- **Up to 10k tasks/user**: GIN index sufficient (<200ms p95)
- **10k-100k tasks/user**: Consider partial indexes, pagination
- **100k+ tasks/user**: Migrate to Elasticsearch (separate search service)

### Alternatives Considered
- **LIKE/ILIKE queries**: No ranking, no stemming, slow for large datasets (rejected)
- **Elasticsearch**: Overkill for MVP, adds operational complexity, requires sync (deferred to future)
- **Meilisearch**: Lighter than Elasticsearch, but still external service (deferred)

### References
- PostgreSQL FTS docs: https://www.postgresql.org/docs/current/textsearch.html
- GIN index performance: https://www.postgresql.org/docs/current/textsearch-indexes.html

---

## 5. Event Schema Design (Pydantic)

### Decision: Pydantic v2 models with JSON serialization

### Rationale
- **Type safety**: Runtime validation prevents malformed events
- **FastAPI integration**: Native support for request/response validation
- **JSON serialization**: Built-in `model_dump_json()` for Kafka messages
- **Versioning support**: Field aliases and deprecation strategies

### Event Schema Pattern
```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int

class TaskCreatedEvent(BaseEvent):
    event_type: str = "task.created"
    task_id: int
    title: str
    priority: str | None = None
    due_date: datetime | None = None
    recurrence_rule: str | None = None
    category_id: int | None = None
    tag_ids: List[int] = Field(default_factory=list)

class TaskCompletedEvent(BaseEvent):
    event_type: str = "task.completed"
    task_id: int
    recurrence_rule: str | None = None
    completed_at: datetime

class TaskUpdatedEvent(BaseEvent):
    event_type: str = "task.updated"
    task_id: int
    updated_fields: dict  # e.g., {"due_date": "2025-01-15T10:00:00", "priority": "high"}

class TaskDeletedEvent(BaseEvent):
    event_type: str = "task.deleted"
    task_id: int

class ReminderSentEvent(BaseEvent):
    event_type: str = "reminder.sent"
    task_id: int
    reminder_time: datetime
```

### Best Practices
1. **Immutability**: Events are immutable once published (append-only log)
2. **Event ID**: Use UUID for unique identification and idempotency
3. **Timestamps**: Always UTC with timezone awareness
4. **Versioning**: Include schema_version field for future evolution
   ```python
   class BaseEvent(BaseModel):
       schema_version: str = "1.0"
   ```
4. **Validation**: Validate before publishing
   ```python
   event = TaskCreatedEvent(user_id=1, task_id=123, title="Test")
   await producer.send(
       topic='task-events',
       value=event.model_dump_json().encode('utf-8'),
       key=str(event.task_id).encode('utf-8')  # Partition by task_id
   )
   ```

### Alternatives Considered
- **Avro/Protobuf**: Requires schema registry, binary serialization (overkill for MVP, deferred)
- **Plain dictionaries**: No validation, error-prone (rejected)

### References
- Pydantic docs: https://docs.pydantic.dev/latest/

---

## 6. Consumer Idempotency Strategies

### Decision: At-least-once delivery with idempotent consumers

### Rationale
- **Simpler implementation**: No distributed transactions or exactly-once coordinators
- **Acceptable for MVP**: Duplicate events are rare and handled gracefully
- **Lower latency**: No transaction commit overhead

### Idempotency Patterns

1. **Notification Service** (Atomic Database Update):
   ```python
   # Only one consumer successfully updates reminder_sent flag
   result = await db.execute(
       update(Task)
       .where(Task.id == task_id, Task.reminder_sent == False)
       .values(reminder_sent=True)
   )

   if result.rowcount == 0:
       # Another consumer already sent reminder, skip
       return

   # Send reminder notification
   logger.info(f"🔔 REMINDER: Task '{task.title}' due in {minutes} minutes")
   ```

2. **Recurring Task Service** (Duplicate Detection):
   ```python
   # Check if next occurrence already created
   existing = await db.execute(
       select(Task).where(
           Task.user_id == user_id,
           Task.title == original_task.title,
           Task.due_date == next_occurrence_date
       )
   )

   if existing.scalar_one_or_none():
       # Already created, skip (idempotent)
       return

   # Create new recurring task
   new_task = Task(
       user_id=user_id,
       title=original_task.title,
       due_date=next_occurrence_date,
       recurrence_rule=original_task.recurrence_rule
   )
   await db.add(new_task)
   ```

3. **Offset Management**:
   ```python
   async for msg in consumer:
       try:
           event = TaskCompletedEvent.model_validate_json(msg.value)
           await process_recurring_task(event)

           # Commit offset after successful processing
           await consumer.commit()
       except Exception as e:
           logger.error(f"Failed to process event: {e}")
           # Don't commit offset, retry on restart
           continue
   ```

### Alternatives Considered
- **Exactly-once semantics**: Requires Kafka transactions, complex coordinator logic (deferred to future)
- **Distributed locks**: Redis SETNX for multi-replica coordination (deferred, single replica for MVP)

---

## Summary

| Technology | Decision | Version | Rationale |
|------------|----------|---------|-----------|
| Kafka Client | aiokafka | 0.11.0 | Async/await native, production-ready |
| Kafka Broker | Redpanda Cloud | Serverless | Zero ops, free tier, Kafka-compatible |
| RRULE Parser | python-dateutil | 2.8.2 | RFC 5545 compliant, battle-tested |
| Full-Text Search | PostgreSQL FTS | Built-in | No external deps, GIN index fast for <10k tasks |
| Event Schema | Pydantic v2 | 2.5.0 | Type safety, FastAPI integration |
| Delivery Semantics | At-least-once | - | Simpler, idempotent consumers handle duplicates |

**All technical unknowns resolved. Ready to proceed to Phase 1: Design.**
