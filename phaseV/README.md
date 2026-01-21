# Phase V: Event-Driven AI Task Assistant - Kubernetes Deployment

> **Production-ready Kubernetes deployment with HTTPS, OpenAI ChatKit, Dapr-powered event streaming, SMTP email notifications, and scalable microservices architecture**

## 🎯 What is This?

Phase V is an event-driven AI-powered task management application deployed on Kubernetes. It allows users to manage their tasks through natural conversation using OpenAI's ChatKit, with automatic email reminders, recurring tasks, and fast full-text search powered by **Dapr** (Distributed Application Runtime) with Kafka (Redpanda Cloud) and PostgreSQL.

**Key Features:**
- 🤖 AI-powered task management via natural language
- 🔐 Secure authentication with Better Auth + JWT
- 🌐 HTTPS with self-signed certificates
- ⚡ Auto-scaling based on CPU/memory usage
- 🗄️ PostgreSQL database (Neon serverless) with full-text search
- 💾 Redis for session caching
- 🔧 MCP (Model Context Protocol) tool integration
- 📊 Horizontal Pod Autoscaling (HPA)
- ⏰ **Automatic task reminders** (event-driven notifications)
- 📧 **Email delivery via SMTP** (Gmail integration)
- 🔄 **Recurring task automation** (iCalendar RRULE support)
- 🔍 **Fast full-text search** (PostgreSQL tsvector + GIN index)
- 📡 **Kafka event streaming** (Redpanda Cloud integration)
- 🔗 **Dapr sidecar integration** (pub/sub, service invocation, state management)

## 🏗️ Event-Driven Architecture

Phase V implements a robust event-driven architecture using **Dapr** (Distributed Application Runtime) with **Kafka (Redpanda Cloud)** as the message broker for asynchronous task processing. Dapr sidecars are injected into all backend services (Backend, MCP Server) enabling:

- **Pub/Sub messaging** via `localhost:3500` (Dapr HTTP API)
- **Service-to-service invocation** with automatic retries and circuit breaking
- **Abstracted broker integration** (switch Kafka to Redis/RabbitMQ without code changes)
- **Observability** with distributed tracing and metrics

### Complete System Architecture Flow

```mermaid
graph TB
    subgraph "User Layer"
        User[👤 User]
    end

    subgraph "Frontend Layer"
        UI[🌐 Next.js Frontend<br/>ChatKit Interface<br/>Port: 3000<br/>Replicas: 2-5]
    end

    subgraph "API Layer with Dapr Sidecars"
        subgraph "Backend Pod (2/2 containers)"
            Backend[⚡ FastAPI Backend<br/>Port: 8000<br/>Replicas: 2-5]
            DaprBackend[🔗 Dapr Sidecar<br/>app-id: backend<br/>Port: 3500]
        end
        subgraph "MCP Server Pod (2/2 containers)"
            MCP[🔧 MCP Server<br/>Tool Executor<br/>Port: 8001<br/>Replicas: 1]
            DaprMCP[🔗 Dapr Sidecar<br/>app-id: mcp-server<br/>Port: 3500]
        end
    end

    subgraph "Data Layer"
        DB[(🗄️ PostgreSQL<br/>Neon Cloud<br/>Full-text Search)]
        Redis[(💾 Redis<br/>Session Cache<br/>Port: 6379)]
    end

    subgraph "Event Streaming Layer - Dapr Pub/Sub"
        DaprPubSub[🔗 Dapr Pub/Sub Component<br/>pubsub-kafka<br/>SASL_SSL/SCRAM-SHA-256]

        subgraph "Kafka Topics (Redpanda Cloud)"
            T1[📋 task-events<br/>3 partitions<br/>7d retention]
            T2[⏰ task-reminders<br/>1 partition<br/>1d retention]
            T3[🔄 task-recurrence<br/>1 partition<br/>7d retention]
        end
    end

    subgraph "Consumer Services Layer"
        NotificationSvc[🔔 Notification Service<br/>Producer + Consumer<br/>Port: 8002<br/>Polls DB every 5s]
        EmailSvc[📧 Email Delivery Service<br/>Consumer Only<br/>Port: 8003<br/>SMTP Client]
        RecurringSvc[🔁 Recurring Task Service<br/>Consumer Only<br/>Port: 8004<br/>RRULE Parser]
    end

    subgraph "External Services"
        SMTP[📨 Gmail SMTP<br/>smtp.gmail.com:587<br/>TLS/STARTTLS]
        UserEmail[📬 User Email Inbox]
    end

    %% User interactions
    User -->|HTTPS| UI
    UI <-->|REST API| Backend

    %% Backend to Dapr sidecar
    Backend -->|localhost:3500| DaprBackend
    MCP -->|localhost:3500| DaprMCP
    Backend --> MCP
    Backend <--> DB
    Backend <--> Redis

    %% Dapr pub/sub flow
    DaprBackend -->|Publish via Dapr| DaprPubSub
    DaprMCP -->|Publish via Dapr| DaprPubSub
    DaprPubSub -->|TaskCreatedEvent<br/>TaskUpdatedEvent<br/>TaskDeletedEvent| T1
    DaprPubSub -->|TaskCompletedEvent| T3
    NotificationSvc -->|ReminderSentEvent| T2

    %% Notification Service flow
    NotificationSvc -.->|Poll every 5s<br/>Find due tasks| DB
    T2 -->|Consume| EmailSvc

    %% Email Service flow
    EmailSvc -->|Query task + user| DB
    EmailSvc -->|Send email| SMTP
    SMTP -->|Deliver| UserEmail

    %% Recurring Task Service flow
    T3 -->|Consume| RecurringSvc
    RecurringSvc -->|Parse RRULE<br/>Create new task| DB
    RecurringSvc -->|Publish TaskCreatedEvent| DaprPubSub

    %% Styling
    classDef userClass fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef frontendClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef backendClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef daprClass fill:#00d4aa,stroke:#00a080,stroke-width:2px,color:#000
    classDef dataClass fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef kafkaClass fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef consumerClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef externalClass fill:#eceff1,stroke:#263238,stroke-width:2px

    class User userClass
    class UI frontendClass
    class Backend,MCP backendClass
    class DaprBackend,DaprMCP,DaprPubSub daprClass
    class DB,Redis dataClass
    class T1,T2,T3 kafkaClass
    class NotificationSvc,EmailSvc,RecurringSvc consumerClass
    class SMTP,UserEmail externalClass
```

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Nginx Ingress                          │
│                    (https://todo-app.local)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
               ┌───────────┴───────────┐
               │                       │
       ┌───────▼────────┐      ┌───────▼───────────────────────┐
       │   Frontend     │      │      Backend Pod (2/2)        │
       │  (Next.js)     │◄────►│ ┌─────────────┬─────────────┐ │
       │  Port: 3000    │      │ │  FastAPI    │ Dapr Sidecar│ │
       │  Replicas: 2   │      │ │  Port: 8000 │ Port: 3500  │ │
       └────────────────┘      │ └─────────────┴─────────────┘ │
                               └───────────────┬───────────────┘
                                               │
                    ┌──────────────────────────┼─────────────────┐
                    │                          │                 │
      ┌─────────────▼─────────────┐    ┌──────▼─────┐  ┌───────▼────────┐
      │    MCP Server Pod (2/2)   │    │   Redis    │  │   PostgreSQL   │
      │ ┌───────────┬───────────┐ │    │  (Cache)   │  │ (Neon Cloud)   │
      │ │MCP Server │Dapr Sidecar│ │    │ Port: 6379 │  │ + Full-text    │
      │ │Port: 8001 │Port: 3500 │ │    └────────────┘  │    Search      │
      │ └───────────┴───────────┘ │                    └────────────────┘
      └─────────────┬─────────────┘
                    │
                    │  Publishes via Dapr Pub/Sub
                    │  POST localhost:3500/v1.0/publish/pubsub-kafka/<topic>
                    ▼
    ┌───────────────────────────────────────────────────────────────┐
    │                  Dapr Pub/Sub Component                       │
    │              (pubsub-kafka → Redpanda Cloud)                  │
    │              SASL_SSL / SCRAM-SHA-256                         │
    └───────────────────────────┬───────────────────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           │                    │                    │
    ┌──────▼──────┐      ┌──────▼────────┐   ┌──────▼────────┐
    │task-events  │      │task-reminders │   │task-recurrence│
    │  (Topic)    │      │   (Topic)     │   │   (Topic)     │
    │ 3 partitions│      │ 1 partition   │   │ 1 partition   │
    │ 7d retention│      │ 1d retention  │   │ 7d retention  │
    └──────┬──────┘      └──────┬────────┘   └──────┬────────┘
           │                    │                    │
    ┌──────▼──────────┐  ┌──────▼──────────┐  ┌─────▼─────────┐
    │ Notification    │  │ Email Delivery  │  │ Recurring Task│
    │   Service       │  │    Service      │  │    Service    │
    │  (Consumer)     │  │   (Consumer)    │  │   (Consumer)  │
    │  Port: 8002     │  │   Port: 8003    │  │   Port: 8004  │
    └─────────────────┘  └────────┬────────┘  └───────────────┘
           │                      │                   │
           │ Polls DB every 5s    │ SMTP              │ Creates new
           │ for due tasks        │ (Gmail)           │ task instance
           │                      │                   │
           └─> Publishes          └─> Sends           └─> Publishes
               ReminderSentEvent      Email               TaskCreatedEvent
               to task-reminders      Notification        to task-events
```

### Event Flows

#### 1. Task Creation Flow (via Dapr)

```mermaid
sequenceDiagram
    participant User
    participant ChatKit as ChatKit UI
    participant Backend as FastAPI Backend
    participant Dapr as Dapr Sidecar<br/>(localhost:3500)
    participant DB as PostgreSQL
    participant PubSub as Dapr Pub/Sub<br/>(pubsub-kafka)
    participant Topic as task-events Topic

    User->>ChatKit: "Create task: Buy groceries"
    ChatKit->>Backend: POST /mcp/tools/add_task
    Backend->>DB: INSERT INTO tasks_phaseiii
    DB-->>Backend: task_id=123
    Backend->>Dapr: POST /v1.0/publish/pubsub-kafka/task-events
    Dapr->>PubSub: Publish TaskCreatedEvent
    PubSub->>Topic: {task_id:123, title:"Buy groceries", ...}
    Dapr-->>Backend: HTTP 204 (Success)
    Backend-->>ChatKit: Success response
    ChatKit-->>User: "✅ Task created!"

    Note over Topic: Event stored for 7 days<br/>Available for future consumers
```

#### 2. Email Reminder Flow (End-to-End)

```mermaid
sequenceDiagram
    participant DB as PostgreSQL
    participant NotifSvc as Notification Service
    participant Producer as Kafka Producer
    participant Topic as task-reminders Topic
    participant EmailSvc as Email Delivery Service
    participant SMTP as Gmail SMTP
    participant User as User Email Inbox

    loop Every 5 seconds
        NotifSvc->>DB: SELECT due tasks
        Note over DB: WHERE due_date - NOW() < 1 hour
        Note over DB: AND reminder_sent = false
    end

    DB-->>NotifSvc: Task ID=188 due in 30 min
    NotifSvc->>Producer: ReminderSentEvent{task_id:188}
    Producer->>Topic: Publish event (partition 0)
    NotifSvc->>DB: UPDATE reminder_sent=true

    Topic->>EmailSvc: Consume ReminderSentEvent
    EmailSvc->>DB: SELECT task and user email
    Note over DB: JOIN users ON task.user_id
    DB-->>EmailSvc: Email and task details
    Note over EmailSvc: email: "user@gmail.com"
    Note over EmailSvc: title: "Buy groceries"

    EmailSvc->>SMTP: SMTP STARTTLS connection
    SMTP-->>EmailSvc: 220 Ready
    EmailSvc->>SMTP: Send email (TLS encrypted)
    SMTP-->>EmailSvc: 250 OK
    EmailSvc->>EmailSvc: Log success + commit offset

    SMTP->>User: 📧 Email delivered

    Note over EmailSvc,SMTP: ✅ Verified working<br/>E2E test successful<br/>2026-01-03
```

#### 3. Recurring Task Flow

```mermaid
sequenceDiagram
    participant User
    participant Backend as FastAPI Backend
    participant DB as PostgreSQL
    participant Producer as Kafka Producer
    participant Topic as task-recurrence Topic
    participant RecurringSvc as Recurring Task Service

    User->>Backend: "Complete task: Daily standup"
    Backend->>DB: UPDATE tasks SET completed=true
    Note over DB: WHERE id=42
    DB-->>Backend: Task with recurrence
    Note over DB: recurrence_rule: FREQ=DAILY;COUNT=5

    Backend->>Producer: TaskCompletedEvent
    Note over Producer: task_id: 42
    Note over Producer: recurrence_rule: FREQ=DAILY;COUNT=5
    Producer->>Topic: Publish event

    Topic->>RecurringSvc: Consume TaskCompletedEvent
    RecurringSvc->>RecurringSvc: Parse RRULE with dateutil
    RecurringSvc->>RecurringSvc: Calculate next occurrence
    Note over RecurringSvc: tomorrow same time

    RecurringSvc->>DB: INSERT new task instance
    Note over DB: due_date = tomorrow
    DB-->>RecurringSvc: new_task_id=43

    RecurringSvc->>Producer: TaskCreatedEvent{task_id:43}
    Producer->>Topic: Publish to task-events

    Note over RecurringSvc: Cycle repeats until<br/>COUNT limit reached
```

#### 4. Complete System Flow (All Events)

```mermaid
flowchart TB
    Start([👤 User Interaction]) --> Action{Action Type}

    Action -->|Create Task| Create[Backend: add_task MCP]
    Action -->|Update Task| Update[Backend: update_task MCP]
    Action -->|Complete Task| Complete[Backend: complete_task MCP]
    Action -->|Delete Task| Delete[Backend: delete_task MCP]

    Create --> SaveDB[(💾 Save to PostgreSQL)]
    Update --> SaveDB
    Complete --> SaveDB
    Delete --> SaveDB

    SaveDB --> PubEvents{Publish Events}

    PubEvents -->|TaskCreatedEvent| TE[📋 task-events topic]
    PubEvents -->|TaskUpdatedEvent| TE
    PubEvents -->|TaskDeletedEvent| TE
    PubEvents -->|TaskCompletedEvent<br/>if has recurrence_rule| TR[🔄 task-recurrence topic]

    %% Notification Service Loop
    DBPoll[🔔 Notification Service<br/>Polls DB every 5s] -.->|Find due tasks| SaveDB
    DBPoll -->|Publish| TReminder[⏰ task-reminders topic]

    %% Consumers
    TReminder --> EmailConsumer[📧 Email Delivery Service]
    TR --> RecurringConsumer[🔁 Recurring Task Service]

    EmailConsumer --> QueryDB[(Query task + user)]
    QueryDB --> SMTP[📨 Send via Gmail SMTP]
    SMTP --> UserInbox([📬 User Email])

    RecurringConsumer --> ParseRRULE[Parse RRULE]
    ParseRRULE --> CreateNext[Create next task instance]
    CreateNext --> SaveDB

    style Start fill:#e1f5ff,stroke:#01579b
    style SaveDB fill:#e8f5e9,stroke:#1b5e20
    style TE fill:#fff9c4,stroke:#f57f17
    style TR fill:#fff9c4,stroke:#f57f17
    style TReminder fill:#fff9c4,stroke:#f57f17
    style EmailConsumer fill:#fce4ec,stroke:#880e4f
    style RecurringConsumer fill:#fce4ec,stroke:#880e4f
    style UserInbox fill:#eceff1,stroke:#263238
```

### Services Overview

| Service | Type | Purpose | Port | Replicas | Dapr Sidecar | Critical |
|---------|------|---------|------|----------|--------------|----------|
| **Backend** | Producer + API | FastAPI + MCP tools, publishes events via Dapr | 8000 | 2-5 | **Yes** (app-id: backend) | Yes |
| **MCP Server** | Tool Executor | Executes MCP tool calls, publishes events via Dapr | 8001 | 1 | **Yes** (app-id: mcp-server) | Yes |
| **Frontend** | UI | Next.js + ChatKit interface | 3000 | 2-5 | No | Yes |
| **Notification Service** | Producer + Consumer | Polls DB, publishes reminders | 8002 | 1 | No | No |
| **Email Delivery** | Consumer | Sends SMTP emails for reminders | 8003 | 1 | No | No |
| **Recurring Task** | Consumer | Regenerates recurring tasks | 8004 | 1 | No | No |

### Kafka Topics Configuration

| Topic | Purpose | Partitions | Retention | Producers | Consumers |
|-------|---------|------------|-----------|-----------|-----------|
| **task-events** | Task lifecycle events (CRUD) | 3 | 7 days | Backend | (Future analytics) |
| **task-reminders** | Reminder notifications audit trail | 1 | 1 day | Notification Service | Email Delivery |
| **task-recurrence** | Recurring task regeneration | 1 | 7 days | Backend | Recurring Task Service |

### Event Schemas

All events use **Pydantic v2** for validation with JSON serialization:

```python
# Base Event (all events inherit)
class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    schema_version: str = "1.0"

# Task Events
class TaskCreatedEvent(BaseEvent):
    task_id: int
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[datetime]
    recurrence_rule: Optional[str]
    category_id: Optional[int]
    tag_ids: List[int]

class TaskCompletedEvent(BaseEvent):
    task_id: int
    recurrence_rule: Optional[str]

class TaskUpdatedEvent(BaseEvent):
    task_id: int
    updated_fields: Dict[str, Any]

class TaskDeletedEvent(BaseEvent):
    task_id: int

# Reminder Event
class ReminderSentEvent(BaseEvent):
    task_id: int
    task_title: str
    due_date: datetime
    notification_type: str  # "email", "sms", etc.
```

### Resilient Service Design

All services implement:
- ✅ **Dapr abstraction**: Backend/MCP services use Dapr sidecar for pub/sub (broker-agnostic)
- ✅ **Graceful degradation**: Services start even if Kafka is temporarily unavailable
- ✅ **Automatic retry**: Connection retries every 30 seconds (up to 10 attempts)
- ✅ **Health checks**: Kubernetes liveness/readiness probes (including Dapr sidecar health)
- ✅ **Manual commit**: Consumers manually commit offsets for exactly-once processing
- ✅ **Error handling**: Failed messages are logged, service continues
- ✅ **Background consumption**: Non-blocking event consumption in separate asyncio tasks

### Dapr Sidecar Configuration

Services with Dapr sidecars use these Kubernetes annotations:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"      # backend or mcp-server
  dapr.io/app-port: "<service-port>"    # 8000 or 8001
  dapr.io/log-level: "debug"
  dapr.io/sidecar-cpu-limit: "200m"
  dapr.io/sidecar-memory-limit: "256Mi"
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-memory-request: "128Mi"
```

**Dapr Components Deployed:**
- `pubsub-kafka`: Kafka pub/sub component connected to Redpanda Cloud
- Sidecar listens on `localhost:3500` for pub/sub HTTP API

### ✅ E2E Verification & Testing

The complete event-driven pipeline has been **verified working end-to-end**:

**Dapr Integration Verified (2026-01-21):**
```bash
# Dapr Sidecar Test Results
✅ MCP Server Pod: 2/2 containers READY (mcp-server + daprd)
✅ Backend Pod: 2/2 containers READY (backend + daprd)
✅ Dapr Sidecar: SASL authentication succeeded with Redpanda Cloud
✅ Pub/Sub Test: HTTP 204 response from localhost:3500/v1.0/publish/pubsub-kafka/task-events

# Dapr Sidecar Verification Commands
kubectl get pods -n todo-phasev -l app=mcp-server    # Shows 2/2 READY
kubectl logs -n todo-phasev -l app=mcp-server -c daprd --tail=20  # Shows "dapr initialized"
```

**Email Flow Verified (2026-01-03):**
```bash
# Test Results Summary
✅ Kafka Producer: Connected to Redpanda Cloud (SASL_SSL/SCRAM-SHA-256)
✅ Event Publishing: ReminderSentEvent published to task-reminders (offset 44)
✅ Consumer Processing: Email delivery service consumed event
✅ Database Query: Retrieved task 188 + user email (saleemakhtar864@gmail.com)
✅ SMTP Connection: TLS connection established to smtp.gmail.com:587
✅ Email Delivery: Email sent successfully and delivered to inbox

# Test Logs
2026-01-03 04:24:09 - Received ReminderSentEvent for task 188
2026-01-03 04:24:12 - Email sent successfully to saleemakhtar864@gmail.com
2026-01-03 04:24:12 - ✅ Email reminder sent for task 188 ('✅ VERIFIED Email Test - SUCCESS')
```

#### Critical Fixes Applied (January 2026)

During E2E testing, the following issues were identified and resolved:

1. **Kafka Authentication (SASL_SSL)**
   - **Issue**: Incorrect password in Kubernetes secret
   - **Fix**: Updated `todo-app-secrets` with correct Redpanda Cloud credentials
   - **Verification**: Connection established, events flowing

2. **SMTP TLS Configuration**
   - **Issue**: `SMTPException: Connection already using TLS` (manual `starttls()` call)
   - **Fix**: Changed to `start_tls=True` parameter in `aiosmtplib.SMTP` initialization
   - **Location**: `app/services/email_delivery_service.py:136-151`

3. **SMTP Credentials**
   - **Issue**: Empty username/password in `email-delivery-secret`
   - **Fix**: Populated with Gmail app password from `redpanda.md`
   - **Credentials**: saleemakhtar864@gmail.com / Gmail app password

4. **Database SSL Connection (Neon PostgreSQL)**
   - **Issue**: `asyncpg.exceptions.InvalidPasswordError` with asyncpg SSL configuration
   - **Root Cause**: asyncpg doesn't accept `sslmode` as URL parameter (psycopg2 only)
   - **Fix**: Strip `?sslmode=require` from URL, provide SSL context via `connect_args`
   - **Implementation**:
     ```python
     import ssl as ssl_module
     ssl_context = ssl_module.create_default_context()
     ssl_context.check_hostname = False
     ssl_context.verify_mode = ssl_module.CERT_NONE

     engine = create_async_engine(
         db_url,  # URL without sslmode parameter
         connect_args={"ssl": ssl_context}
     )
     ```

5. **Database URL Mismatch**
   - **Issue**: Email service using old database (`phaseiii_db@ep-nameless-hill`)
   - **Fix**: Updated to active database (`neondb@ep-green-shape-advm09wo-pooler`)
   - **Result**: All queries working, no auth errors

#### Testing Scripts

Two test scripts are available in `phaseV/backend/`:

1. **`publish_reminder_event.py`** - Manual event publisher
   - Fetches real task from database
   - Publishes ReminderSentEvent to Kafka
   - Monitors email delivery logs
   - **Usage**: `kubectl exec -n todo-phasev deployment/backend -- python publish_reminder_event.py`

2. **`test_e2e_email_reminder.py`** - End-to-end automated test
   - Creates test event with dummy data
   - Verifies consumer processing
   - Checks email delivery logs
   - **Usage**: `python test_e2e_email_reminder.py`

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

```bash
# Required tools
- Minikube (local Kubernetes cluster)
- kubectl (Kubernetes CLI)
- Helm 3.13+
- Docker
- Dapr CLI + Dapr runtime (v1.12+)
- Redpanda Cloud account (or local Kafka cluster)
- Gmail account (for SMTP email delivery)

# Optional but recommended
- kubectl-ai (AI-powered kubectl assistant)
```

### Installation

**Step 1: Start Minikube**

```bash
# Start with adequate resources for event-driven services
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable nginx ingress
minikube addons enable ingress

# Enable metrics server (for HPA)
minikube addons enable metrics-server

# Verify
minikube status
kubectl get nodes
```

**Step 2: Install Dapr**

```bash
# Install Dapr CLI (if not already installed)
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
#   dapr-operator          dapr-system  True     Running  1         1.12.x   ...
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.12.x   ...
#   dapr-placement-server  dapr-system  True     Running  1         1.12.x   ...
#   dapr-sentry            dapr-system  True     Running  1         1.12.x   ...
```

**Step 4: Setup Redpanda Cloud (Kafka)**

1. Create a free account at [https://redpanda.com/try-redpanda](https://redpanda.com/try-redpanda)
2. Create a new cluster (select region closest to you)
3. Create topics:
   - `task-events` (3 partitions, 7 days retention)
   - `task-reminders` (1 partition, 1 day retention)
   - `task-recurrence` (1 partition, 7 days retention)
4. Create a user with SASL/SCRAM-SHA-256 authentication
5. Set ACLs: Allow ALL operations on ALL topics for your user
6. Note your:
   - Bootstrap servers (e.g., `xxx.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092`)
   - SASL username
   - SASL password

**Step 5: Setup Gmail SMTP**

1. Enable 2-Step Verification on your Google account
2. Generate an App Password:
   - Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
3. Note your:
   - Gmail address (e.g., `your-email@gmail.com`)
   - App password

**Step 6: Create Secrets Configuration**

```bash
# Copy example file
cp kubernetes/helm/todo-app/values-local.yaml.example kubernetes/helm/todo-app/values-local.yaml

# Edit with your actual values
nano kubernetes/helm/todo-app/values-local.yaml
```

Add these values:

```yaml
secrets:
  # Database
  DATABASE_URL: "postgresql://user:password@host/database?sslmode=require"

  # OpenAI
  OPENAI_API_KEY: "sk-..."

  # Auth
  BETTER_AUTH_SECRET: "your-secret-key-min-32-chars"

  # Kafka (Redpanda Cloud)
  KAFKA_BOOTSTRAP_SERVERS: "xxx.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092"
  KAFKA_SASL_USERNAME: "your-username"
  KAFKA_SASL_PASSWORD: "your-password"

  # SMTP (Gmail)
  SMTP_USERNAME: "your-email@gmail.com"
  SMTP_PASSWORD: "your-app-password"
  SMTP_FROM_EMAIL: "your-email@gmail.com"
  SMTP_FROM_NAME: "Todo App"
```

**Step 7: Build Docker Images**

```bash
# Set Minikube Docker environment
eval $(minikube docker-env)

# Build frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://todo-app.local/api \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=https://todo-app.local \
  --build-arg NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your_domain_key_here \
  -t todo-frontend:latest \
  frontend

# Build backend (includes all services)
docker build -t todo-backend:latest backend

# Build email delivery service
docker build -f backend/Dockerfile.email-delivery -t todo-email-delivery:latest backend

# Verify images
docker images | grep todo
```

**Step 8: Deploy to Kubernetes**

```bash
# Deploy with Helm
helm install todo-app kubernetes/helm/todo-app \
  -n todo-phasev \
  --create-namespace \
  -f kubernetes/helm/todo-app/values-local.yaml \
  -f kubernetes/helm/todo-app/values-tls.yaml \
  --wait --timeout=5m

# Verify all pods are running
kubectl get pods -n todo-phasev

# Expected output (note: 2/2 for pods with Dapr sidecar):
# NAME                                  READY   STATUS    RESTARTS   AGE
# backend-xxxxxxxxxx-xxxxx              2/2     Running   0          2m  ← Dapr sidecar
# email-delivery-xxxxxxxxxx-xxxxx       1/1     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx             1/1     Running   0          2m
# mcp-server-xxxxxxxxxx-xxxxx           2/2     Running   0          2m  ← Dapr sidecar
# notification-service-xxxxxxxxxx-xxxxx 1/1     Running   0          2m
# recurring-service-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
# redis-0                               1/1     Running   0          2m
```

**Step 9: Access the App**

```bash
# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Trust the self-signed certificate
# Chrome/Edge: Visit https://todo-app.local/chat and type "thisisunsafe"
# Firefox: Click "Advanced" → "Accept the Risk and Continue"
```

🎉 **App is now running at: https://todo-app.local/chat**

---

## 🔧 Configuration

### Environment Variables

**Backend (FastAPI + Dapr Pub/Sub)**
```yaml
DATABASE_URL: PostgreSQL connection string
OPENAI_API_KEY: OpenAI API key
BETTER_AUTH_SECRET: JWT signing secret
MCP_SERVER_URL: http://mcp-service:8001/mcp
REDIS_HOST: redis-service
CORS_ORIGINS: JSON array of allowed origins
USE_DAPR: "true"  # Enable Dapr pub/sub (publishes to localhost:3500)
KAFKA_BOOTSTRAP_SERVERS: Kafka broker addresses (for direct Kafka fallback)
KAFKA_SASL_USERNAME: SASL username
KAFKA_SASL_PASSWORD: SASL password
KAFKA_SECURITY_PROTOCOL: SASL_SSL
KAFKA_SASL_MECHANISM: SCRAM-SHA-256
```

**MCP Server (Tool Executor + Dapr Pub/Sub)**
```yaml
DATABASE_URL: PostgreSQL connection string
OPENAI_API_KEY: OpenAI API key
REDIS_HOST: redis-service
MCP_PORT: 8001
USE_DAPR: "true"  # Enable Dapr pub/sub (publishes to localhost:3500)
KAFKA_BOOTSTRAP_SERVERS: Kafka broker addresses (for direct Kafka fallback)
KAFKA_SASL_USERNAME: SASL username
KAFKA_SASL_PASSWORD: SASL password
KAFKA_SECURITY_PROTOCOL: SASL_SSL
KAFKA_SASL_MECHANISM: SCRAM-SHA-256
```

**Email Delivery Service**
```yaml
DATABASE_URL: (same as backend)
KAFKA_BOOTSTRAP_SERVERS: (same as backend)
KAFKA_SASL_USERNAME: (same as backend)
KAFKA_SASL_PASSWORD: (same as backend)
KAFKA_SECURITY_PROTOCOL: SASL_SSL
KAFKA_SASL_MECHANISM: SCRAM-SHA-256
SMTP_HOST: smtp.gmail.com
SMTP_PORT: 587
SMTP_USERNAME: your-email@gmail.com
SMTP_PASSWORD: gmail-app-password
SMTP_FROM_EMAIL: your-email@gmail.com
SMTP_FROM_NAME: "Todo App Reminders"
```

**Notification Service**
```yaml
DATABASE_URL: (same as backend)
KAFKA_BOOTSTRAP_SERVERS: (same as backend)
KAFKA_SASL_USERNAME: (same as backend)
KAFKA_SASL_PASSWORD: (same as backend)
# Polls database every 5 seconds for tasks due within 1 hour
```

**Recurring Task Service**
```yaml
DATABASE_URL: (same as backend)
KAFKA_BOOTSTRAP_SERVERS: (same as backend)
KAFKA_SASL_USERNAME: (same as backend)
KAFKA_SASL_PASSWORD: (same as backend)
# Consumes task-recurrence topic for TaskCompletedEvent
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Dapr Sidecar Issues

**Symptom**: Pod shows 1/1 instead of 2/2 (missing Dapr sidecar)

```bash
# Check pod status
kubectl get pods -n todo-phasev -l app=backend
kubectl get pods -n todo-phasev -l app=mcp-server

# Expected: 2/2 READY (app + daprd)
# If showing 1/1, sidecar is not injected
```

**Causes & Solutions**:

1. **Dapr not installed**
   ```bash
   # Check Dapr status
   dapr status -k

   # If not installed, run:
   dapr init -k
   ```

2. **Missing annotations**
   ```bash
   # Verify deployment has Dapr annotations
   kubectl get deployment backend -n todo-phasev -o yaml | grep -A10 "annotations:"

   # Should see:
   # dapr.io/enabled: "true"
   # dapr.io/app-id: "backend"
   ```

3. **Sidecar injection disabled**
   ```bash
   # Check if namespace has sidecar injector label
   kubectl get namespace todo-phasev --show-labels

   # If missing, Helm values may have dapr.enabled: false
   # Verify values.yaml: dapr.enabled should be true
   ```

**Test Dapr Pub/Sub**:
```bash
# Exec into pod and test pub/sub endpoint
kubectl exec -n todo-phasev deployment/mcp-server -c mcp-server -- \
  curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","task_id":999}'

# Expected: 204 (No Content = success)
```

#### 2. Kafka Connection Failures

**Symptom**: Services show "Connection closed during SASL handshake"

```bash
# Check logs
kubectl logs -n todo-phasev -l app=email-delivery --tail=100
kubectl logs -n todo-phasev -l app=notification-service --tail=100

# Look for errors like:
# KafkaConnectionError: Connection at xxx.redpanda.com:9092 closed
```

**Causes & Solutions**:

1. **Redpanda Cloud connection limits**
   - Redpanda Cloud free tier has connection limits
   - Solution: Contact Redpanda support or upgrade plan

2. **Incorrect credentials**
   ```bash
   # Verify secrets
   kubectl get secret -n todo-phasev todo-app-secrets -o jsonpath='{.data.KAFKA_SASL_USERNAME}' | base64 -d
   kubectl get secret -n todo-phasev todo-app-secrets -o jsonpath='{.data.KAFKA_SASL_PASSWORD}' | base64 -d
   ```

3. **ACL permissions missing**
   - Go to Redpanda Console → Security → ACLs
   - Ensure your user has ALL permissions on ALL topics

4. **Network connectivity**
   ```bash
   # Test TLS connection from cluster
   kubectl run test-kafka --image=alpine --restart=Never -n todo-phasev --rm -it -- \
     sh -c "apk add openssl && openssl s_client -connect xxx.redpanda.com:9092"
   ```

**Resilient Behavior**:
- All consumer services have built-in retry logic (10 attempts, 30-second intervals)
- Services start in "degraded mode" and automatically connect when Kafka becomes available
- Health checks pass even when Kafka is temporarily unavailable

#### 3. Email Delivery Not Working

**Check Service Status**:
```bash
# Check if pod is running
kubectl get pods -n todo-phasev -l app=email-delivery

# Check logs
kubectl logs -n todo-phasev -l app=email-delivery --tail=100

# Look for:
# ✅ "Kafka consumer started"
# ✅ "Email sent successfully"
# ❌ SMTPAuthenticationError
# ❌ KafkaConnectionError
```

**Common Issues**:

1. **Gmail App Password not configured**
   - Generate new App Password at [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Update secret:
     ```bash
     kubectl edit secret email-delivery-secret -n todo-phasev
     # Base64 encode your app password: echo -n "your-app-password" | base64
     ```

2. **"Less secure app access" blocked** (OLD Gmail accounts)
   - This is deprecated - use App Passwords instead

3. **SMTP connection timeout**
   - Verify port 587 is accessible from cluster

4. **No events in topic**
   ```bash
   # Check Redpanda Console → Topics → task-reminders
   # Should see ReminderSentEvent messages
   ```

#### 4. Recurring Tasks Not Working

**Check Service**:
```bash
# Check recurring-service logs
kubectl logs -n todo-phasev -l app=recurring-task --tail=100

# Look for:
# ✅ "Kafka consumer started for task-recurrence topic"
# ✅ "Processing TaskCompletedEvent: task_id=X"
# ✅ "Created new recurring task instance"
```

**Test Flow**:
1. Create recurring task with RRULE: `FREQ=DAILY;COUNT=5`
2. Complete the task via ChatKit
3. Check logs - should create new instance
4. Verify new task appears in database

**Common Issues**:
- Invalid RRULE syntax (must be valid iCalendar format)
- Consumer not connected to Kafka (connection retry in progress)

#### 5. Pods in CrashLoopBackOff

```bash
# Identify crashing pod
kubectl get pods -n todo-phasev

# Check events
kubectl describe pod <pod-name> -n todo-phasev

# Common causes:
# - Missing secrets (OPENAI_API_KEY, DATABASE_URL)
# - Database connection failure
# - Kafka connection failure (for consumer services)
```

#### 6. ChatKit Not Loading

1. **Check HTTPS**: Must access via `https://todo-app.local` (not `http://`)
2. **Trust Certificate**: Type `thisisunsafe` in Chrome
3. **Check Backend Logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=backend | grep -i chatkit
   ```
4. **Verify Frontend Can Reach Backend**:
   ```bash
   kubectl exec -n todo-phasev deploy/frontend -- wget -qO- http://backend-service:8000/health
   ```

---

## 📊 Monitoring & Observability

### Health Checks

All services expose `/health` endpoints:

```bash
# Check backend health
kubectl port-forward -n todo-phasev svc/backend-service 8000:8000
curl http://localhost:8000/health

# Check email-delivery health
kubectl port-forward -n todo-phasev svc/email-delivery-service 8003:8003
curl http://localhost:8003/health
```

### Kafka Consumer Lag

Check consumer lag in Redpanda Console:
1. Go to **Consumers** tab
2. Look for consumer groups:
   - `email-delivery-consumer-group`
   - `recurring-task-service-group`
3. Check **Lag** column (should be 0 or low)

### Resource Usage

```bash
# CPU/Memory by pod
kubectl top pods -n todo-phasev

# Specific service
kubectl top pod -n todo-phasev -l app=email-delivery

# Node resources
kubectl top nodes
```

### Logs Aggregation

```bash
# Stream all logs
kubectl logs -n todo-phasev --all-containers=true -f --max-log-requests=10

# Filter by service
kubectl logs -n todo-phasev -l app=backend -f

# Search for errors
kubectl logs -n todo-phasev --all-containers=true | grep -i error
```

---

## 🔄 Deployment & Updates

### Update Services

```bash
# Rebuild backend image
eval $(minikube docker-env)
docker build -t todo-backend:latest backend

# Restart deployment to pick up new image
kubectl rollout restart deployment/backend -n todo-phasev

# Verify rollout
kubectl rollout status deployment/backend -n todo-phasev
```

### Update Configuration

```bash
# Edit secrets
kubectl edit secret todo-app-secrets -n todo-phasev

# Restart affected services
kubectl rollout restart deployment -n todo-phasev
```

### Scale Services

```bash
# Scale email delivery (if high volume)
kubectl scale deployment/email-delivery --replicas=3 -n todo-phasev

# Auto-scaling (HPA)
kubectl autoscale deployment/email-delivery \
  --min=1 --max=5 \
  --cpu-percent=70 \
  -n todo-phasev
```

---

## 🧪 Testing Event-Driven Features

### Test Reminder Flow

1. **Create task with future due date**:
   ```
   User: "Create a task 'Test Reminder' due in 30 minutes"
   ```

2. **Wait for notification service to pick it up** (polls every 5 seconds)

3. **Check notification-service logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=notification-service -f
   # Should see: "Published ReminderSentEvent to task-reminders"
   ```

4. **Check email-delivery logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=email-delivery -f
   # Should see: "Email sent successfully for task: Test Reminder"
   ```

5. **Check your email** for reminder notification

### Test Recurring Task

1. **Create recurring task**:
   ```
   User: "Create a daily task 'Standup' for 5 days"
   ```
   Backend creates task with: `recurrence_rule=FREQ=DAILY;COUNT=5`

2. **Complete the task**:
   ```
   User: "Complete task 'Standup'"
   ```

3. **Check recurring-service logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=recurring-task -f
   # Should see: "Created new recurring task instance for: Standup"
   ```

4. **Verify new task created**:
   ```
   User: "List my tasks"
   # Should show new "Standup" task with incremented due date
   ```

---

## 📚 Architecture Decision Records (ADRs)

- [ADR-0020: Event-Driven Architecture Stack](../history/adr/0020-event-driven-architecture-stack-kafka-aiokafka-redpanda-cloud.md)
- [ADR-0021: Recurring Task Implementation](../history/adr/0021-recurring-task-implementation-icalendar-rrule-with-python-dateutil.md)
- [ADR-0022: Full-Text Search Strategy](../history/adr/0022-full-text-search-strategy-postgresql-tsvector-with-gin-index.md)
- [ADR-0023: Event Consumer Service Deployment](../history/adr/0023-event-consumer-service-deployment-architecture-kubernetes-single-replica-strategy.md)

---

## 🔐 Security Considerations

1. **Kafka Security**:
   - ✅ SASL/SCRAM-SHA-256 authentication
   - ✅ TLS/SSL encryption (SASL_SSL)
   - ✅ ACL-based authorization

2. **SMTP Security**:
   - ✅ TLS (STARTTLS on port 587)
   - ✅ App passwords (not account passwords)
   - ⚠️ Store credentials in Kubernetes secrets

3. **Secrets Management**:
   - Never commit `values-local.yaml` to git
   - Use Kubernetes secrets (base64 encoded)
   - Consider Sealed Secrets or external secret managers for production

4. **Network Policies**:
   - Implement network policies to restrict pod-to-pod communication
   - Example: Only backend should access PostgreSQL

---

## 🚦 Production Checklist

Before deploying to production:

- [ ] Use real TLS certificates (Let's Encrypt)
- [ ] Configure Kafka retention policies for compliance
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation (ELK/Loki)
- [ ] Implement network policies
- [ ] Set resource limits on all pods
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up alerting for Kafka consumer lag
- [ ] Test disaster recovery procedures
- [ ] Document runbooks for on-call team
- [ ] Load test with expected traffic
- [ ] Configure rate limiting on SMTP to avoid quotas

---

## 🆘 Support & Documentation

- **📊 Architecture Flow Diagrams**: [`ARCHITECTURE_FLOW.md`](./ARCHITECTURE_FLOW.md) - Comprehensive visual documentation with Mermaid diagrams
- **Kubernetes Guide**: `kubernetes/docs/KUBERNETES_GUIDE.md`
- **Runbook**: `kubernetes/docs/RUNBOOK.md`
- **Architecture**: `kubernetes/docs/architecture-diagram.md`
- **ADRs**: `history/adr/*.md`
- **Issues**: [GitHub Issues](https://github.com/your-org/your-repo/issues)

### Quick Links to Diagrams

- [Complete System Architecture Flow](./ARCHITECTURE_FLOW.md#complete-system-architecture)
- [Email Reminder Flow (E2E Verified)](./ARCHITECTURE_FLOW.md#email-reminder-flow-verified-e2e)
- [Recurring Task Flow](./ARCHITECTURE_FLOW.md#recurring-task-flow)
- [Security Architecture](./ARCHITECTURE_FLOW.md#security-architecture)
- [Failure & Recovery Flows](./ARCHITECTURE_FLOW.md#failure--recovery-flows)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test locally with Minikube
5. Update documentation
6. Submit a pull request

---

## 📜 License

MIT License - see LICENSE file for details

---

## 🎓 Learn More

### Technologies Used
- [Kubernetes](https://kubernetes.io/docs/) - Container orchestration
- [Helm](https://helm.sh/docs/) - Kubernetes package manager
- [Dapr](https://docs.dapr.io/) - Distributed Application Runtime for microservices
- [Kafka/Redpanda](https://docs.redpanda.com/) - Event streaming platform
- [aiokafka](https://aiokafka.readthedocs.io/) - Python async Kafka client
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org/docs) - React framework
- [OpenAI ChatKit](https://platform.openai.com/docs/chatkit) - AI chat interface
- [Better Auth](https://better-auth.com) - Authentication library
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [iCalendar RRULE](https://icalendar.org/rrule-tool.html) - Recurrence rule standard

---

**Built with ❤️ using Kubernetes, Dapr, Kafka, Next.js, FastAPI, and OpenAI ChatKit**

**Phase V: Event-Driven Architecture with Dapr Integration**
