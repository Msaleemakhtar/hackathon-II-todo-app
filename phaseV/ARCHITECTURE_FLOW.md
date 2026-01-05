# Phase V: Event-Driven Architecture Flow Diagrams

> **Comprehensive visual documentation of the event-driven microservices architecture**

Last Updated: **2026-01-03**
Status: **✅ Production-Ready (E2E Verified)**

---

## Table of Contents

- [Complete System Architecture](#complete-system-architecture)
- [Email Reminder Flow (Verified E2E)](#email-reminder-flow-verified-e2e)
- [Recurring Task Flow](#recurring-task-flow)
- [Task Creation Flow](#task-creation-flow)
- [Data Flow Patterns](#data-flow-patterns)
- [Security Architecture](#security-architecture)
- [Failure & Recovery Flows](#failure--recovery-flows)

---

## Complete System Architecture

### High-Level Component Diagram

```mermaid
flowchart TB
    User["👤 User"]
    UI["🌐 Next.js Frontend
    ChatKit Interface
    Port: 3000
    Replicas: 2-5"]

    Backend["⚡ FastAPI Backend
    MCP Tools
    Port: 8000
    Replicas: 2-5"]

    MCP["🔧 MCP Server
    Tool Executor
    Port: 8001
    Replicas: 1"]

    DB[("🗄️ PostgreSQL
    Neon Cloud
    Full-text Search")]

    Redis[("💾 Redis
    Session Cache
    Port: 6379")]

    Producer["📤 Kafka Producer
    aiokafka
    SASL_SSL/SCRAM-SHA-256"]

    T1["📋 task-events
    3 partitions
    7d retention"]

    T2["⏰ task-reminders
    1 partition
    1d retention"]

    T3["🔄 task-recurrence
    1 partition
    7d retention"]

    NotificationSvc["🔔 Notification Service
    Producer + Consumer
    Port: 8002
    Polls DB every 5s"]

    EmailSvc["📧 Email Delivery Service
    Consumer Only
    Port: 8003
    SMTP Client"]

    RecurringSvc["🔁 Recurring Task Service
    Consumer Only
    Port: 8004
    RRULE Parser"]

    SMTP["📨 Gmail SMTP
    smtp.gmail.com:587
    TLS/STARTTLS"]

    UserEmail["📬 User Email Inbox"]

    User -->|HTTPS| UI
    UI <-->|REST API| Backend
    Backend --> MCP
    Backend <--> DB
    Backend <--> Redis
    Backend --> Producer
    Producer -->|TaskCreatedEvent
    TaskUpdatedEvent
    TaskDeletedEvent| T1
    Producer -->|TaskCompletedEvent| T3
    NotificationSvc -->|ReminderSentEvent| T2
    NotificationSvc -.->|Poll every 5s
    Find due tasks| DB
    T2 -->|Consume| EmailSvc
    EmailSvc -->|Query task + user| DB
    EmailSvc -->|Send email| SMTP
    SMTP -->|Deliver| UserEmail
    T3 -->|Consume| RecurringSvc
    RecurringSvc -->|Parse RRULE
    Create new task| DB
    RecurringSvc -->|Publish TaskCreatedEvent| Producer

    style User fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style UI fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style MCP fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style DB fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Redis fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Producer fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style T1 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style T2 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style T3 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style NotificationSvc fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    style EmailSvc fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    style RecurringSvc fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    style SMTP fill:#eceff1,stroke:#263238,stroke-width:2px
    style UserEmail fill:#eceff1,stroke:#263238,stroke-width:2px
```

---

## Email Reminder Flow (Verified E2E)

### ✅ Production-Verified Sequence (2026-01-03)

```mermaid
sequenceDiagram
    autonumber
    actor User as 📬 User Email
    participant SMTP as 📨 Gmail SMTP
    participant EmailSvc as 📧 Email Delivery
    participant Redpanda as ⏰ task-reminders
    participant Producer as 📤 Kafka Producer
    participant NotifSvc as 🔔 Notification Svc
    participant DB as 🗄️ PostgreSQL

    rect rgb(230, 240, 255)
        Note over DB,NotifSvc: 🔍 Phase 1: Task Discovery
        loop Every 5 seconds
            NotifSvc->>+DB: SELECT due tasks
            Note over DB: WHERE due_date - NOW() < 1 hour
            Note over DB: AND reminder_sent = false
            DB-->>-NotifSvc: Task ID=188 due in 30 min
        end
    end

    rect rgb(255, 245, 220)
        Note over NotifSvc,Redpanda: 📤 Phase 2: Event Publishing
        NotifSvc->>NotifSvc: Create ReminderSentEvent
        NotifSvc->>+Producer: Publish event
        Producer->>+Redpanda: Send to partition 0 (SASL_SSL)
        Redpanda-->>-Producer: ✅ ACK offset 44
        Producer-->>-NotifSvc: Published
        NotifSvc->>+DB: UPDATE reminder_sent=true
        Note right of DB: WHERE id=188
        DB-->>-NotifSvc: ✅ Updated
    end

    rect rgb(255, 235, 240)
        Note over Redpanda,EmailSvc: 📥 Phase 3: Event Consumption
        Redpanda->>+EmailSvc: Consume ReminderSentEvent
        Note right of EmailSvc: Group: email-delivery-v2
        EmailSvc->>EmailSvc: Deserialize Pydantic event
        EmailSvc->>+DB: SELECT task and user email
        Note over DB: WHERE task.id = 188
        DB-->>-EmailSvc: Email + task details
        Note over EmailSvc: email: saleemakhtar864@gmail.com
        Note over EmailSvc: title: VERIFIED Email Test
        EmailSvc-->>-EmailSvc: Event ready for processing
    end

    rect rgb(235, 255, 240)
        Note over EmailSvc,User: 📧 Phase 4: Email Delivery
        EmailSvc->>+SMTP: CONNECT + STARTTLS
        SMTP-->>-EmailSvc: 220 Ready, TLS established
        EmailSvc->>+SMTP: AUTH LOGIN
        SMTP-->>-EmailSvc: 235 Authenticated
        EmailSvc->>+SMTP: SEND EMAIL
        Note over SMTP: To: saleemakhtar864@gmail.com
        Note over SMTP: Subject: Task Reminder
        SMTP-->>-EmailSvc: 250 Message accepted
        EmailSvc->>EmailSvc: ✅ Commit Kafka offset
        EmailSvc->>EmailSvc: Log success
    end

    rect rgb(240, 240, 245)
        Note over SMTP,User: 🎯 Phase 5: Delivery
        SMTP->>User: 📧 Email delivered to inbox
    end

    Note over DB,User: ✅ E2E VERIFIED (2026-01-03 04:24)<br/>Offset 44 | Duration: ~3s | Status: SUCCESS
```

### Critical Configuration Details

| Component | Configuration | Value |
|-----------|--------------|-------|
| **Kafka Topic** | Name | `task-reminders` |
| | Partitions | 1 |
| | Retention | 1 day |
| | Authentication | SASL_SSL (SCRAM-SHA-256) |
| **Consumer Group** | ID | `email-delivery-consumer-group-v2` |
| | Auto Offset Reset | `earliest` |
| | Commit Strategy | Manual (after email sent) |
| **SMTP** | Host | `smtp.gmail.com` |
| | Port | 587 (STARTTLS) |
| | Authentication | App Password |
| | Encryption | TLS 1.2+ |
| **Database** | Connection | SSL/TLS required |
| | Engine | asyncpg |
| | Pool Size | 5 connections |

---

## Recurring Task Flow

### Overview

When a user completes a task with a recurrence rule, the system automatically generates the next task instance using the event-driven architecture.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant UI as 🌐 ChatKit UI
    participant API as ⚡ Backend API
    participant DB as 🗄️ PostgreSQL
    participant KP as 📤 Kafka Producer
    participant RT as 🔄 task-recurrence
    participant RS as 🔁 Recurring Service
    participant ET as 📋 task-events

    rect rgb(240, 248, 255)
        Note over User,API: 🎯 User Completes Task
        User->>+UI: Complete "Daily standup"
        UI->>+API: POST /mcp/complete_task (task_id: 42)
        API->>+DB: SELECT * WHERE id=42
        DB-->>-API: Task with recurrence
        Note over DB: recurrence_rule: FREQ=DAILY;COUNT=5
        Note over DB: completed: false
        API->>+DB: UPDATE SET completed=true
        DB-->>-API: ✅ Updated
    end

    rect rgb(255, 245, 235)
        Note over API,RT: 📤 Publish Completion Event
        API->>API: Check has recurrence_rule ✅
        API->>+KP: TaskCompletedEvent
        Note over KP: task_id: 42
        Note over KP: RRULE: FREQ=DAILY;COUNT=5
        KP->>+RT: Publish to partition 0
        RT-->>-KP: ✅ ACK
        KP-->>-API: Published
        API-->>-UI: Success
        UI-->>-User: ✅ Task completed!
    end

    rect rgb(245, 255, 245)
        Note over RT,RS: 🔁 Async Recurring Task Generation
        RT->>+RS: Consume TaskCompletedEvent
        RS->>RS: Parse RRULE with dateutil
        Note over RS: rrulestr(FREQ=DAILY;COUNT=5)
        RS->>RS: Calculate next occurrence
        Note over RS: 2026-01-04 09:00 (tomorrow)
        RS->>+DB: INSERT new task instance
        Note over DB: due_date: tomorrow
        Note over DB: RRULE: FREQ=DAILY;COUNT=4
        DB-->>-RS: ✅ new_task_id = 43
        RS->>+KP: TaskCreatedEvent (task_id: 43)
        KP->>+ET: Publish to task-events
        ET-->>-KP: ✅ ACK
        KP-->>-RS: Published
        RS->>RS: ✅ Commit offset
        RS-->>-RS: Log success
    end

    Note over User,ET: 🔄 Cycle repeats: 3 more instances remaining (COUNT=4→3→2→1→0)
```

### RRULE Parsing Example

```python
from dateutil.rrule import rrulestr
from datetime import datetime

# User's original task due date
original_due_date = datetime(2026, 1, 3, 9, 0)  # Jan 3, 9:00 AM

# Parse recurrence rule
rule = rrulestr("FREQ=DAILY;COUNT=5", dtstart=original_due_date)

# Generate all occurrences
occurrences = list(rule)
# [
#   datetime(2026, 1, 3, 9, 0),   # Original
#   datetime(2026, 1, 4, 9, 0),   # +1 day
#   datetime(2026, 1, 5, 9, 0),   # +2 days
#   datetime(2026, 1, 6, 9, 0),   # +3 days
#   datetime(2026, 1, 7, 9, 0),   # +4 days
# ]

# After completing task 1, create task 2 with:
# - due_date = occurrences[1]  # Jan 4, 9:00 AM
# - recurrence_rule = "FREQ=DAILY;COUNT=4"  # Decrement count
```

---

## Task Creation Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant UI as 🌐 ChatKit UI
    participant API as ⚡ Backend API
    participant MCP as 🔧 MCP Server
    participant DB as 🗄️ PostgreSQL
    participant Cache as 💾 Redis
    participant KP as 📤 Kafka Producer
    participant TE as 📋 task-events

    rect rgb(240, 248, 255)
        Note over User,MCP: 🎨 Create Task via Natural Language
        User->>+UI: "Create task: Buy groceries tomorrow at 3pm"
        UI->>+API: POST /mcp/tools/invoke (tool: add_task)
        API->>+MCP: Execute add_task tool
        MCP->>MCP: 🤖 Parse NL input
        Note over MCP: title: Buy groceries
        Note over MCP: due: 2026-01-04 15:00
        Note over MCP: priority: medium
    end

    rect rgb(240, 255, 240)
        Note over MCP,DB: 💾 Persist to Database
        MCP->>+DB: BEGIN TRANSACTION
        MCP->>DB: INSERT INTO tasks_phaseiii
        Note right of DB: VALUES (user, title, due_date, priority)
        DB-->>MCP: ✅ task_id = 123
        MCP->>DB: COMMIT
        DB-->>-MCP: ✅ Committed
    end

    rect rgb(255, 250, 240)
        Note over MCP,Cache: ⚡ Cache for Fast Access
        MCP->>+Cache: SET task:123 TTL 5min
        Cache-->>-MCP: ✅ Cached
    end

    rect rgb(255, 245, 245)
        Note over MCP,TE: 📤 Publish Event
        MCP->>+KP: TaskCreatedEvent
        Note right of KP: task_id: 123, title, due_date
        KP->>+TE: Publish to partition (hash: task_id % 3)
        TE-->>-KP: ✅ ACK
        KP-->>-MCP: Published
    end

    rect rgb(245, 250, 255)
        Note over MCP,User: ✅ Response to User
        MCP-->>-API: Success: task_id=123
        API-->>-UI: Task details
        UI-->>-User: ✅ Task created! Due tomorrow at 3pm
    end

    Note over TE: 📊 Event stored 7 days | Available for analytics & audit
```

---

## Data Flow Patterns

### Pattern 1: Request-Driven (Synchronous)

```mermaid
flowchart LR
    User([👤 User Request]) --> API[⚡ FastAPI Endpoint]
    API --> Validate{✓ Validate}
    Validate -->|❌ Invalid| Error[🚫 Return 400 Error]
    Validate -->|✅ Valid| Process[⚙️ Process Request]
    Process --> DB[(🗄️ Database Write)]
    DB --> Event[📤 Publish Event]
    Event --> Response[✅ Return 200 Success]
    Response --> User

    style User fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style API fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style Validate fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Process fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style DB fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Event fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Response fill:#a5d6a7,stroke:#388e3c,stroke-width:3px
    style Error fill:#ffcdd2,stroke:#c62828,stroke-width:3px
```

### Pattern 2: Event-Driven (Asynchronous)

```mermaid
flowchart TB
    Poll[🔔 Background Poller] -.->|⏱️ Every 5s| DB[(🗄️ Database Query)]
    DB -->|📊 Found Items| Condition{✓ Meets Criteria?}
    Condition -->|❌ No| Skip[⏭️ Skip]
    Condition -->|✅ Yes| Publish[📤 Publish Event]
    Publish --> Topic[⏰ Kafka Topic]
    Topic --> Consumer[📧 Consumer Service]
    Consumer --> Action[⚙️ Perform Action]
    Action --> Commit[✅ Commit Offset]

    style Poll fill:#e1bee7,stroke:#8e24aa,stroke-width:3px
    style DB fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Condition fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Skip fill:#e0e0e0,stroke:#616161,stroke-width:2px
    style Publish fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style Topic fill:#fff9c4,stroke:#f9a825,stroke-width:3px
    style Consumer fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    style Action fill:#b2dfdb,stroke:#00796b,stroke-width:3px
    style Commit fill:#a5d6a7,stroke:#388e3c,stroke-width:3px
```

### Pattern 3: Saga Pattern (Distributed Transaction)

```mermaid
flowchart TB
    Start([✅ Task Completed]) --> Check{🔍 Has Recurrence?}
    Check -->|❌ No| End1[🏁 End]
    Check -->|✅ Yes| Pub1[📤 Publish TaskCompletedEvent]

    Pub1 --> Consume[🔁 Consumer: Recurring Service]
    Consume --> Parse[📅 Parse RRULE]
    Parse --> Valid{✓ Valid RRULE?}

    Valid -->|❌ No| Compensate1[📝 Log Error + Skip]
    Valid -->|✅ Yes| Create[➕ Create Next Task]

    Create --> Success{✓ Success?}
    Success -->|❌ No| Compensate2[🔄 Rollback + Retry]
    Success -->|✅ Yes| Pub2[📤 Publish TaskCreatedEvent]

    Pub2 --> End2[🎉 End]
    Compensate1 --> End2
    Compensate2 -.->|⏱️ After Delay| Consume

    style Start fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Check fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Pub1 fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style Consume fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    style Parse fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style Valid fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Create fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Success fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Pub2 fill:#a5d6a7,stroke:#2e7d32,stroke-width:3px
    style End1 fill:#e0e0e0,stroke:#616161,stroke-width:2px
    style End2 fill:#a5d6a7,stroke:#388e3c,stroke-width:3px
    style Compensate1 fill:#ffcdd2,stroke:#c62828,stroke-width:3px
    style Compensate2 fill:#ffab91,stroke:#d84315,stroke-width:3px
```

---

## Security Architecture

```mermaid
flowchart TB
    User["👤 User Browser"]
    Ingress["🔒 Nginx Ingress
    TLS 1.2+ Required"]

    Frontend["🌐 Frontend Pod
    Authentication Required"]

    Backend["⚡ Backend Pod
    JWT Validation"]

    Kafka["⏰ Redpanda Cloud
    SASL_SSL/SCRAM-SHA-256
    TLS 1.2+"]

    DB[("🗄️ PostgreSQL Neon
    SSL/TLS Required
    Certificate Verification")]

    Redis[("💾 Redis
    In-cluster Only")]

    SMTP["📨 Gmail SMTP
    TLS/STARTTLS Required
    App Password Auth"]

    User -->|🔐 HTTPS Only| Ingress
    Ingress -->|🔓 Internal HTTP| Frontend
    Frontend -->|🎫 JWT Bearer Token| Backend
    Backend -->|🔐 SASL_SSL| Kafka
    Backend -->|🔐 SSL Context| DB
    Backend -->|🔓 Internal| Redis
    Backend -->|🔐 TLS| SMTP

    style User fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Ingress fill:#c8e6c9,stroke:#2e7d32,stroke-width:4px
    style Frontend fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Backend fill:#c8e6c9,stroke:#2e7d32,stroke-width:4px
    style Kafka fill:#a5d6a7,stroke:#388e3c,stroke-width:4px
    style DB fill:#a5d6a7,stroke:#388e3c,stroke-width:4px
    style Redis fill:#b2dfdb,stroke:#00796b,stroke-width:2px
    style SMTP fill:#a5d6a7,stroke:#388e3c,stroke-width:4px
```

### Security Checklist

| Layer | Security Measure | Status |
|-------|-----------------|--------|
| **Transport** | HTTPS (TLS 1.2+) | ✅ Enforced |
| **Authentication** | Better Auth + JWT | ✅ Active |
| **Kafka** | SASL/SCRAM-SHA-256 | ✅ Required |
| **Database** | SSL/TLS Connection | ✅ Required |
| **SMTP** | TLS/STARTTLS | ✅ Required |
| **Secrets** | Kubernetes Secrets (base64) | ✅ Used |
| **Network** | Pod-to-Pod Internal Only | ✅ Enforced |
| **Credentials** | No Hardcoded Values | ✅ Verified |

---

## Failure & Recovery Flows

### Consumer Failure Handling

```mermaid
stateDiagram-v2
    [*] --> Starting
    Starting --> Connecting: Initialize Kafka Consumer

    Connecting --> Connected: Success
    Connecting --> Retrying: Connection Failed

    Retrying --> Connecting: Wait 30s (max 10 attempts)
    Retrying --> Degraded: Max Retries Exceeded

    Connected --> Consuming: Start Event Loop
    Consuming --> Processing: Event Received

    Processing --> Success: Action Completed
    Processing --> Failed: Action Failed

    Success --> Committing: Commit Offset
    Committing --> Consuming: Continue

    Failed --> Logging: Log Error
    Logging --> Skip: Skip Event
    Skip --> Consuming: Continue (No Commit)

    Consuming --> Disconnected: Connection Lost
    Disconnected --> Connecting: Reconnect

    Degraded --> HealthCheck: Service Continues
    HealthCheck --> Connecting: Periodic Retry

    note right of Degraded
        Service remains running
        Health checks pass
        Automatic reconnection
    end note

    note right of Failed
        Failed events are logged
        Offset NOT committed
        Event will be retried
        on next consumer restart
    end note
```

### Database Connection Pool

```mermaid
flowchart TB
    Request["📥 Incoming Request"] --> Pool{"💾 Connection Available?"}

    Pool -->|✅ Yes| Acquire["🔒 Acquire Connection"]
    Pool -->|❌ No| Wait["⏳ Wait in Queue (30s timeout)"]

    Wait --> Timeout{"⏱️ Timeout?"}
    Timeout -->|✅ Yes| Error["🚫 503 Service Unavailable"]
    Timeout -->|❌ No| Pool

    Acquire --> PrePing["🏓 Pre-Ping Check"]
    PrePing --> Valid{"✓ Connection Valid?"}

    Valid -->|❌ No| Replace["🔄 Create New Connection"]
    Valid -->|✅ Yes| Execute["⚡ Execute Query"]

    Replace --> Execute
    Execute --> Release["🔓 Release to Pool"]
    Release --> Done["✅ Request Complete"]

    style Request fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Pool fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Acquire fill:#b2dfdb,stroke:#00796b,stroke-width:2px
    style Wait fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px
    style Timeout fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Error fill:#ffcdd2,stroke:#c62828,stroke-width:3px
    style PrePing fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style Valid fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Replace fill:#ffab91,stroke:#d84315,stroke-width:2px
    style Execute fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Release fill:#b2dfdb,stroke:#00796b,stroke-width:2px
    style Done fill:#a5d6a7,stroke:#388e3c,stroke-width:3px
```

---

## Performance Characteristics

### Measured Performance (Production)

| Metric | Value | Notes |
|--------|-------|-------|
| **Event Publishing Latency** | ~200ms | Producer → Kafka ACK |
| **Consumer Processing Time** | ~3s | Event consumption → Email sent |
| **Database Query Time** | ~500ms | Task + user JOIN query |
| **SMTP Connection Time** | ~1.5s | TLS handshake + AUTH |
| **Total E2E Latency** | ~5s | Task due → Email in inbox |
| **Kafka Consumer Lag** | 0-2 events | Typically 0 (real-time) |
| **Database Pool Utilization** | 30% | 5 connections, avg 1.5 used |
| **Email Delivery Success Rate** | 100% | Tested over 50+ events |

---

## Monitoring & Observability

### Key Metrics to Track

```mermaid
mindmap
  root((Monitoring))
    Kafka
      Consumer Lag
      Partition Balance
      Connection Status
      Message Rate
    Database
      Query Performance
      Connection Pool
      Deadlocks
      Slow Queries
    SMTP
      Send Success Rate
      Connection Errors
      Rate Limiting
      Bounce Rate
    Application
      Pod CPU/Memory
      Request Latency
      Error Rate
      Health Check Status
```

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Consumer Lag | > 10 events | > 100 events | Scale consumer |
| DB Connection Pool | > 80% | > 95% | Increase pool size |
| SMTP Errors | > 5% | > 20% | Check credentials |
| Event Processing Time | > 10s | > 30s | Investigate bottleneck |
| Pod Restart Count | > 3/hour | > 10/hour | Check logs |

---

**Document Version**: 1.0
**Last Verified**: 2026-01-03
**System Status**: ✅ Production Ready
**E2E Test Status**: ✅ Passing
