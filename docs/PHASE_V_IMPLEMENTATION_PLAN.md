# Phase V Implementation Plan: Advanced Cloud Deployment
~/.claude/plans/ancient-soaring-whisper.md
**Directory Structure**: `/phaseV/` (copied from Phase IV, independent implementation)
**Approach**: Sequential implementation (Part A → B → C)
**Feature Scope**: All advanced features together (due dates, priorities, tags, search, filter, sort, recurring tasks)
**Kafka**: Redpanda Cloud (serverless, free tier)
**Cloud Provider**: Oracle Cloud (OKE - always free tier)

## Phase V Directory Structure

```
phaseV/
├── frontend/                    # Copied from Phase IV → enhance with new features
├── backend/                     # Copied from Phase IV → add advanced features + Kafka + Dapr
├── kubernetes/                  # Copied from Phase IV → update for Dapr + cloud
│   ├── helm/
│   ├── dapr-components/        # NEW: Dapr component configs
│   ├── scripts/
│   └── docs/
├── specs/                       # NEW: Phase V-specific specs
└── README.md
```

**Note**: All file paths in this plan reference `/phaseV/` directory.

---

## Overview

Phase V transforms the todo application into a production-grade, event-driven, distributed system with advanced features, deployed on cloud infrastructure. This plan follows the hackathon requirements while building on the solid Phase IV Kubernetes foundation.

### Key Objectives
1. ✅ Implement advanced task management features (due dates, priorities, tags, search, recurring tasks)
2. ✅ Add event-driven architecture with Kafka (Redpanda Cloud)
3. ✅ Integrate Dapr for distributed application runtime
4. ✅ Deploy to Oracle Cloud Kubernetes (OKE)
5. ✅ Implement CI/CD pipeline with GitHub Actions
6. ✅ Add production monitoring and logging

---

## Part A: Advanced Features Implementation

**Goal**: Enhance task management with intermediate and advanced features, add event-driven architecture with Kafka.

### A1: Database Schema Evolution

**Files to Create/Modify**:
- `/phaseV/backend/alembic/versions/YYYYMMDD_HHMMSS_add_advanced_task_fields.py`
- `/phaseV/backend/app/models/task.py`
- `/phaseV/backend/app/models/category.py` (new)
- `/phaseV/backend/app/models/tag.py` (new)
- `/phaseV/backend/app/models/task_tag.py` (new junction table)

**Schema Changes to `tasks_phaseiii` table**:
```python
# New fields to add:
priority: str = Field(default="medium")  # Enum: low, medium, high, urgent
due_date: Optional[datetime] = Field(default=None)
category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
recurrence_rule: Optional[str] = Field(default=None)  # iCal RRULE format
reminder_sent: bool = Field(default=False)
```

**New Tables**:
```python
# categories table
id: int (PK, autoincrement)
user_id: str (indexed, not null)
name: str (max 50 chars, not null)
color: str (hex format, nullable)
created_at: datetime

# tags table
id: int (PK, autoincrement)
user_id: str (indexed, not null)
name: str (max 30 chars, not null)
color: str (hex format, nullable)
created_at: datetime

# task_tags junction table
task_id: int (FK → tasks_phaseiii.id, PK)
tag_id: int (FK → tags.id, PK)
```

**Indexes to Add**:
- `idx_tasks_phaseiii_priority` on (user_id, priority)
- `idx_tasks_phaseiii_due_date` on (user_id, due_date)
- `idx_tasks_phaseiii_category` on (category_id)
- `idx_categories_user` on (user_id)
- `idx_tags_user` on (user_id)

**Full-Text Search Setup**:
```sql
-- Add tsvector column for full-text search
ALTER TABLE tasks_phaseiii ADD COLUMN search_vector tsvector;
CREATE INDEX idx_tasks_search ON tasks_phaseiii USING GIN(search_vector);
```

**Implementation Steps**:
1. Create SQLModel models for categories, tags, task_tags junction
2. Update Task model with new fields
3. Generate Alembic migration with `alembic revision --autogenerate -m "add advanced task fields"`
4. Add PostgreSQL full-text search trigger function
5. Test migration on development database
6. Document rollback strategy

---

### A2: Enhanced MCP Tools

**Files to Modify**:
- `/phaseV/backend/app/mcp/tools.py`

**Updated Tool Signatures**:

```python
# Enhanced add_task
add_task(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",  # NEW: low, medium, high, urgent
    due_date: str = None,       # NEW: ISO 8601 datetime
    category_id: int = None,    # NEW: optional category
    tag_ids: List[int] = None,  # NEW: list of tag IDs
    recurrence_rule: str = None # NEW: iCal RRULE
)

# Enhanced list_tasks
list_tasks(
    user_id: str,
    status: str = "all",
    priority: str = None,       # NEW: filter by priority
    category_id: int = None,    # NEW: filter by category
    tag_id: int = None,         # NEW: filter by tag
    due_before: str = None,     # NEW: tasks due before date
    due_after: str = None,      # NEW: tasks due after date
    sort_by: str = "created_at" # NEW: created_at, due_date, priority, title
)

# Enhanced update_task
update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,       # NEW
    due_date: str = None,       # NEW
    category_id: int = None,    # NEW
    tag_ids: List[int] = None,  # NEW
    recurrence_rule: str = None # NEW
)
```

**New MCP Tools**:

```python
# Search tasks with full-text search
search_tasks(
    user_id: str,
    query: str,
    status: str = "all",
    limit: int = 20
) -> List[Task]

# Manage categories
add_category(user_id: str, name: str, color: str = None) -> Category
list_categories(user_id: str) -> List[Category]
delete_category(user_id: str, category_id: int) -> Dict

# Manage tags
add_tag(user_id: str, name: str, color: str = None) -> Tag
list_tags(user_id: str) -> List[Tag]
delete_tag(user_id: str, tag_id: int) -> Dict

# Tag operations
add_tag_to_task(user_id: str, task_id: int, tag_id: int) -> Dict
remove_tag_from_task(user_id: str, task_id: int, tag_id: int) -> Dict

# Due date management
set_reminder(user_id: str, task_id: int, remind_before_minutes: int) -> Dict
get_overdue_tasks(user_id: str) -> List[Task]
get_upcoming_tasks(user_id: str, days: int = 7) -> List[Task]
```

**Implementation Steps**:
1. Update existing tools with new parameters (maintain backward compatibility)
2. Implement new tools with proper validation
3. Add error handling for invalid priorities, dates, RRULE patterns
4. Write unit tests for each tool (pytest)
5. Update MCP tool descriptions for better AI prompting
6. Test with ChatKit to ensure natural language understanding

---

### A3: Event-Driven Architecture with Kafka

**Files to Create**:
- `/phaseV/backend/app/kafka/producer.py` (new)
- `/phaseV/backend/app/kafka/events.py` (new - event schemas)
- `/phaseV/backend/app/services/notification_service.py` (new consumer)
- `/phaseV/backend/app/services/recurring_task_service.py` (new consumer)
- `/phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml` (new)
- `/phaseV/kubernetes/helm/todo-app/templates/recurring-deployment.yaml` (new)

**Kafka Topics**:
```yaml
1. task-events
   - Producers: All MCP tools (when tasks created/updated/deleted/completed)
   - Consumers: Notification Service, Recurring Task Service, Audit Service (future)
   - Schema: { event_type, task_id, task_data, user_id, timestamp }

2. reminders
   - Producers: Backend (when due_date set on task)
   - Consumers: Notification Service
   - Schema: { task_id, title, due_at, remind_at, user_id }

3. task-updates
   - Producers: All MCP tools
   - Consumers: WebSocket Service (future for real-time UI updates)
   - Schema: { task_id, change_type, user_id, timestamp }
```

**Redpanda Cloud Setup**:
1. Sign up at redpanda.com/cloud
2. Create Serverless cluster (free tier)
3. Create topics: `task-events`, `reminders`, `task-updates`
4. Copy bootstrap server URL and credentials
5. Store credentials in Kubernetes Secrets

**Event Producer Integration**:
```python
# In each MCP tool
async def add_task(...):
    # Create task in database
    task = await create_task_in_db(...)

    # Publish event to Kafka
    await kafka_producer.send(
        topic="task-events",
        value={
            "event_type": "created",
            "task_id": task.id,
            "task_data": task.dict(),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # If due_date set, publish reminder event
    if task.due_date:
        await publish_reminder_event(task)

    return task
```

**Notification Service (Consumer)**:
```python
# Consumes from 'reminders' topic
# Sends browser push notifications
# Marks reminder_sent=True in database
# Runs as separate Kubernetes deployment
```

**Recurring Task Service (Consumer)**:
```python
# Consumes from 'task-events' topic
# Listens for 'completed' events on tasks with recurrence_rule
# Parses RRULE, calculates next occurrence
# Automatically creates new task instance
# Runs as separate Kubernetes deployment
```

**Implementation Steps**:
1. Setup Redpanda Cloud cluster and topics
2. Implement Kafka producer with aiokafka library
3. Define event schemas in `/app/kafka/events.py`
4. Integrate event publishing in all MCP tools
5. Implement Notification Service as consumer
6. Implement Recurring Task Service as consumer
7. Create Kubernetes deployments for new services
8. Add Kafka connection configuration to Helm chart
9. Test event flow end-to-end

---

### A4: Search & Filter Implementation

**Files to Create/Modify**:
- `/phaseV/backend/app/services/search_service.py` (new)
- `/phaseV/backend/app/mcp/tools.py` (add search_tasks tool)

**PostgreSQL Full-Text Search**:
```python
# Trigger function to update search_vector
CREATE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_search_update
    BEFORE INSERT OR UPDATE ON tasks_phaseiii
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

**Search Service Implementation**:
```python
async def search_tasks(
    user_id: str,
    query: str,
    status: str = "all",
    limit: int = 20
) -> List[Task]:
    """
    Full-text search with ranking.
    Returns tasks ordered by relevance.
    """
    search_query = """
        SELECT *, ts_rank(search_vector, query) as rank
        FROM tasks_phaseiii, plainto_tsquery('english', :query) query
        WHERE user_id = :user_id
            AND search_vector @@ query
            AND (:status = 'all' OR
                 (:status = 'pending' AND completed = false) OR
                 (:status = 'completed' AND completed = true))
        ORDER BY rank DESC
        LIMIT :limit
    """
    # Execute with SQLModel
```

**Advanced Filtering**:
```python
async def list_tasks_advanced(
    user_id: str,
    filters: Dict[str, Any]
) -> List[Task]:
    """
    Multi-criteria filtering:
    - status: all, pending, completed
    - priority: low, medium, high, urgent
    - category_id: int
    - tag_id: int
    - due_before: datetime
    - due_after: datetime
    - overdue: bool
    - sort_by: created_at, due_date, priority, title
    - sort_order: asc, desc
    """
    # Build dynamic query with filters
```

**Implementation Steps**:
1. Add PostgreSQL FTS extension and trigger
2. Implement search_service with FTS queries
3. Add search_tasks MCP tool
4. Update list_tasks tool with advanced filters
5. Add sorting capabilities (multiple fields)
6. Test with various search queries
7. Optimize with proper indexes
8. Update ChatKit prompts for search commands

---

### A5: Recurring Tasks Implementation

**Files to Create**:
- `/phaseV/backend/app/services/recurring_task_service.py`
- `/phaseV/backend/app/utils/rrule_parser.py`

**RRULE Parser**:
```python
from dateutil.rrule import rrulestr

def parse_rrule(rrule_string: str, start_date: datetime) -> datetime:
    """
    Parse iCal RRULE and calculate next occurrence.
    Examples:
    - FREQ=DAILY → every day
    - FREQ=WEEKLY;BYDDAY=MO,WE,FR → every Monday, Wednesday, Friday
    - FREQ=MONTHLY;BYMONTHDAY=1 → first day of every month
    """
    rule = rrulestr(rrule_string, dtstart=start_date)
    next_occurrence = rule.after(datetime.now())
    return next_occurrence
```

**Recurring Task Service**:
```python
async def handle_task_completed(event: Dict):
    """
    Kafka consumer for 'completed' events on recurring tasks.
    """
    task_id = event["task_id"]
    task = await get_task_by_id(task_id)

    if not task.recurrence_rule:
        return  # Not a recurring task

    # Calculate next occurrence
    next_due_date = parse_rrule(
        task.recurrence_rule,
        task.due_date
    )

    # Create new task instance
    new_task = await create_task({
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": next_due_date,
        "category_id": task.category_id,
        "recurrence_rule": task.recurrence_rule,
        "tags": task.tags
    })

    logger.info(f"Created recurring task {new_task.id} from {task_id}")
```

**Implementation Steps**:
1. Install python-dateutil for RRULE parsing
2. Implement RRULE parser with validation
3. Implement Recurring Task Service as Kafka consumer
4. Add RRULE examples to MCP tool descriptions
5. Test with various recurrence patterns
6. Deploy as separate Kubernetes deployment
7. Add monitoring for recurring task generation

---

### A6: Frontend ChatKit Enhancements

**Files to Modify**:
- `/phaseV/frontend/src/app/chat/page.tsx`

**Enhanced ChatKit Prompts**:
```typescript
const suggestedPrompts = [
  "Add a high priority task to finish the project report by Friday",
  "Show me all urgent tasks due this week",
  "Create a recurring task to review emails every Monday",
  "Search for tasks related to 'budget'"
]
```

**ChatKit System Prompt Update**:
```
You are a task management assistant with advanced capabilities:
- Set task priorities (low, medium, high, urgent)
- Schedule tasks with due dates
- Create recurring tasks using natural language
- Search tasks by keyword
- Filter by priority, category, tags, due dates
- Send reminders for upcoming tasks

When users mention dates like "tomorrow", "next week", "Friday", calculate the actual date.
When users say "recurring" or "every day/week", create appropriate recurrence rules.
```

**Implementation Steps**:
1. Update ChatKit starter prompts
2. Enhance agent system prompt
3. Add UI indicators for priorities (color coding)
4. Display due dates with visual cues
5. Show tag badges in chat responses
6. Test natural language date parsing

---

## Part B: Dapr Integration (Minikube)

**Goal**: Add Dapr for distributed application runtime, abstracting infrastructure dependencies.

### B1: Dapr Installation & Setup

**Prerequisites**:
- Minikube running with Phase IV deployment
- kubectl configured
- Helm 3.13+ installed

**Installation Steps**:
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr installation
kubectl get pods -n dapr-system
# Should see: dapr-dashboard, dapr-operator, dapr-placement, dapr-sentry, dapr-sidecar-injector

# Check Dapr version
dapr version
```

**Files to Create**:
- `/phaseV/kubernetes/dapr-components/` (new directory)
- `/phaseV/kubernetes/dapr-components/pubsub-kafka.yaml`
- `/phaseV/kubernetes/dapr-components/statestore-postgres.yaml`
- `/phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml`
- `/phaseV/kubernetes/dapr-components/jobs-scheduler.yaml`

---

### B2: Dapr Components Configuration

**Pub/Sub Component (Kafka via Redpanda)**:
```yaml
# /phaseV/kubernetes/dapr-components/pubsub-kafka.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-phasev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "YOUR-REDPANDA-URL:9092"
    - name: authType
      value: "sasl"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: consumerGroup
      value: "todo-service"
```

**State Management Component (PostgreSQL)**:
```yaml
# /phaseV/kubernetes/dapr-components/statestore-postgres.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-phasev
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-app-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
```

**Secrets Store Component**:
```yaml
# /phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-phasev
spec:
  type: secretstores.kubernetes
  version: v1
```

**Implementation Steps**:
1. Install Dapr on Minikube cluster
2. Create Dapr component YAML files
3. Apply components to todo-phasev namespace
4. Create Kubernetes secrets for Kafka credentials
5. Verify components are loaded: `dapr components -k -n todo-phasev`

---

### B3: Service Updates for Dapr

**Files to Modify**:
- `/phaseV/backend/app/main.py`
- `/phaseV/backend/app/kafka/producer.py` → replace with Dapr Pub/Sub
- `/phaseV/backend/app/services/notification_service.py` → use Dapr
- `/phaseV/kubernetes/helm/todo-app/templates/backend-deployment.yaml`
- `/phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml`

**Replace Kafka Client with Dapr Pub/Sub**:
```python
# OLD: Direct Kafka
from aiokafka import AIOKafkaProducer
producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")
await producer.send("task-events", value=event)

# NEW: Dapr Pub/Sub
import httpx
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event
)
```

**Add Dapr Annotations to Deployments**:
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
        - name: backend
          # ... existing config
```

**Dapr Jobs API for Reminders**:
```python
# Instead of cron polling, use Dapr Jobs
async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    """Schedule exact-time reminder using Dapr Jobs API."""
    await httpx.post(
        f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
        json={
            "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder"
            }
        }
    )

# Callback endpoint
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this at scheduled time."""
    job_data = await request.json()
    if job_data["data"]["type"] == "reminder":
        await publish_event("reminders", "reminder.due", job_data["data"])
    return {"status": "SUCCESS"}
```

**Implementation Steps**:
1. Update backend to use Dapr HTTP API instead of direct Kafka
2. Add Dapr annotations to all service deployments
3. Implement Dapr Jobs API for reminders
4. Update Helm chart with Dapr configuration
5. Test Pub/Sub flow through Dapr sidecar
6. Verify state management working
7. Test Jobs API triggering at scheduled times
8. Monitor Dapr sidecar logs for debugging

---

### B4: Helm Chart Updates for Dapr

**Files to Modify**:
- `/phaseV/kubernetes/helm/todo-app/values.yaml`

**Add Dapr Configuration**:
```yaml
# values.yaml
dapr:
  enabled: true
  appId: "todo-app"
  logLevel: "info"
  components:
    pubsub:
      enabled: true
      brokers: "{{ .Values.kafka.brokers }}"
    statestore:
      enabled: true
      connectionString: "{{ .Values.database.url }}"

kafka:
  brokers: "YOUR-REDPANDA-URL:9092"
  username: ""  # Set in values-local.yaml
  password: ""  # Set in values-local.yaml
```

**Implementation Steps**:
1. Add Dapr configuration to values.yaml
2. Conditionally enable Dapr annotations based on values
3. Create Helm templates for Dapr components
4. Update deployment scripts to apply Dapr components
5. Test Helm upgrade with Dapr enabled
6. Document Dapr setup in KUBERNETES_GUIDE.md

---

## Part C: Cloud Deployment (Oracle Cloud)

**Goal**: Deploy production-ready application to Oracle Cloud Kubernetes (OKE) with CI/CD, monitoring, and production hardening.

### C1: Oracle Cloud Infrastructure Setup

**Oracle Cloud Free Tier**:
- Sign up at https://www.oracle.com/cloud/free/
- Always Free tier includes: 4 OCPUs, 24GB RAM, 200GB storage
- No credit card charge after trial
- Best for learning without time pressure

**Create OKE Cluster**:
```bash
# Using OCI CLI
oci ce cluster create \
  --compartment-id <compartment-ocid> \
  --name todo-app-oke \
  --kubernetes-version v1.28.2 \
  --vcn-id <vcn-ocid> \
  --node-pool-name default-pool \
  --node-shape VM.Standard.A1.Flex \
  --node-shape-config '{"ocpus":4,"memoryInGBs":24}' \
  --node-count 2

# Configure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region us-ashburn-1

# Verify connection
kubectl get nodes
```

**Files to Create**:
- `/phaseV/kubernetes/terraform/` (optional - Infrastructure as Code)
- `/phaseV/kubernetes/terraform/main.tf`
- `/phaseV/kubernetes/terraform/variables.tf`
- `/phaseV/kubernetes/terraform/outputs.tf`

**Implementation Steps**:
1. Create Oracle Cloud account (free tier)
2. Setup VCN (Virtual Cloud Network) and subnets
3. Create OKE cluster with 2 nodes (4 OCPU, 24GB each)
4. Configure kubectl to connect to OKE
5. Setup OCI CLI for automation
6. (Optional) Write Terraform for reproducible infrastructure
7. Document setup in `phaseV/kubernetes/docs/ORACLE_CLOUD_SETUP.md`

---

### C2: Production Helm Configuration

**Files to Create**:
- `/phaseV/kubernetes/helm/todo-app/values-production.yaml`

**Production Values**:
```yaml
# values-production.yaml
environment: production

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com

frontend:
  replicas: 3
  image:
    repository: your-registry.ocir.io/tenancy/todo-frontend
    tag: "1.0.0"
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

backend:
  replicas: 3
  image:
    repository: your-registry.ocir.io/tenancy/todo-backend
    tag: "1.0.0"
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

redis:
  persistence:
    enabled: true
    size: 10Gi
    storageClass: oci-bv

database:
  external: true
  url: "postgresql://user:pass@neon.tech:5432/todo_prod"

kafka:
  brokers: "your-redpanda-url:9092"
  tls: true

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
```

**TLS Certificates Setup**:
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt issuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

**Implementation Steps**:
1. Create production values file
2. Setup Oracle Container Registry (OCIR) for Docker images
3. Install cert-manager for TLS certificates
4. Configure Let's Encrypt ClusterIssuer
5. Update DNS records to point to OKE load balancer
6. Deploy with production values
7. Verify HTTPS working with valid certificates

---

### C3: CI/CD Pipeline (GitHub Actions)

**Files to Create**:
- `.github/workflows/ci-phase-v.yml`
- `.github/workflows/deploy-production.yml`

**CI Workflow** (`ci-phase-v.yml`):
```yaml
name: Phase V CI

on:
  pull_request:
    paths:
      - 'phaseV/**'
  push:
    branches:
      - main

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          cd phaseV/backend
          pip install uv
          uv pip install ruff
          ruff check .
          ruff format --check .

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: |
          cd phaseV/backend
          uv pip install -r requirements.txt
          uv run pytest --cov=app --cov-report=term

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: |
          cd phaseV/frontend
          bun install
          bun run lint

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: |
          cd phaseV/frontend
          bun install
          bun test

  build-images:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    needs: [test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: your-registry.ocir.io
          username: ${{ secrets.OCIR_USERNAME }}
          password: ${{ secrets.OCIR_PASSWORD }}
      - uses: docker/build-push-action@v5
        with:
          context: ./phaseV/frontend
          push: true
          tags: |
            your-registry.ocir.io/tenancy/todo-frontend:latest
            your-registry.ocir.io/tenancy/todo-frontend:${{ github.sha }}
      - uses: docker/build-push-action@v5
        with:
          context: ./phaseV/backend
          push: true
          tags: |
            your-registry.ocir.io/tenancy/todo-backend:latest
            your-registry.ocir.io/tenancy/todo-backend:${{ github.sha }}

  helm-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/setup-helm@v3
      - run: |
          helm lint phaseV/kubernetes/helm/todo-app
          helm template phaseV/kubernetes/helm/todo-app --dry-run
```

**Deployment Workflow** (`deploy-production.yml`):
```yaml
name: Deploy to Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > ~/.kube/config

      - uses: azure/setup-helm@v3

      - name: Deploy to OKE
        run: |
          helm upgrade todo-app phaseV/kubernetes/helm/todo-app \
            -n todo-phasev \
            --create-namespace \
            -f phaseV/kubernetes/helm/todo-app/values-production.yaml \
            --set frontend.image.tag=${{ github.event.release.tag_name }} \
            --set backend.image.tag=${{ github.event.release.tag_name }} \
            --wait \
            --timeout 10m

      - name: Run smoke tests
        run: |
          kubectl run smoke-test \
            --rm -i --restart=Never \
            --image=curlimages/curl \
            -- curl -f https://todo.example.com/health || exit 1

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "❌ Production deployment failed for ${{ github.event.release.tag_name }}"
            }
```

**Implementation Steps**:
1. Create GitHub Actions workflow files
2. Setup GitHub secrets (OCIR credentials, KUBECONFIG)
3. Configure GitHub Environments (production with approval)
4. Test CI pipeline on PR
5. Create release tag to trigger deployment
6. Setup Slack/Discord webhooks for notifications
7. Document CI/CD workflow in README

---

### C4: Monitoring & Observability Stack

**Files to Create**:
- `/phaseV/kubernetes/helm/todo-app/templates/prometheus-servicemonitor.yaml`
- `/phaseV/kubernetes/helm/todo-app/templates/grafana-dashboard.yaml`
- `/phaseV/kubernetes/monitoring/` (new directory)

**Install Prometheus + Grafana**:
```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin123

# Expose Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Access at http://localhost:3000 (admin/admin123)
```

**Backend Metrics Instrumentation**:
```python
# /phaseV/backend/app/main.py
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

task_operations_total = Counter(
    'task_operations_total',
    'Total task operations',
    ['operation', 'user_id']
)

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**ServiceMonitor for Prometheus**:
```yaml
# prometheus-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
  namespace: todo-phasev
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

**Grafana Dashboard JSON**:
```json
{
  "dashboard": {
    "title": "Todo App Metrics",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "Task Operations",
        "targets": [{
          "expr": "sum(rate(task_operations_total[5m])) by (operation)"
        }]
      },
      {
        "title": "Pod CPU Usage",
        "targets": [{
          "expr": "sum(rate(container_cpu_usage_seconds_total{namespace='todo-phasev'}[5m])) by (pod)"
        }]
      }
    ]
  }
}
```

**Logging with Loki** (Optional):
```bash
# Install Loki
helm install loki grafana/loki-stack \
  -n monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true

# Configure Grafana datasource for Loki
```

**Implementation Steps**:
1. Install Prometheus Operator via Helm
2. Add Prometheus metrics to backend (prometheus-client)
3. Create ServiceMonitor for app services
4. Design Grafana dashboards (HTTP, tasks, pods, HPA)
5. (Optional) Install Loki for log aggregation
6. Setup alerting rules in Prometheus
7. Configure Alertmanager for notifications
8. Document monitoring stack in RUNBOOK.md

---

### C5: Production Hardening

**Security Enhancements**:

**1. Network Policies**:
```yaml
# /phaseV/kubernetes/helm/todo-app/templates/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: todo-phasev
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:  # External database
        - podSelector: {}
      ports:
        - protocol: TCP
          port: 5432
```

**2. RBAC Policies**:
```yaml
# Service account for backend
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: todo-phasev

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: backend-role
  namespace: todo-phasev
rules:
  - apiGroups: [""]
    resources: ["secrets", "configmaps"]
    verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: backend-rolebinding
  namespace: todo-phasev
subjects:
  - kind: ServiceAccount
    name: backend-sa
roleRef:
  kind: Role
  name: backend-role
  apiGroup: rbac.authorization.k8s.io
```

**3. Pod Security Standards**:
```yaml
# Update deployment with security context
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: backend
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop:
            - ALL
        readOnlyRootFilesystem: true
```

**4. Resource Quotas**:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-phasev-quota
  namespace: todo-phasev
spec:
  hard:
    requests.cpu: "8"
    requests.memory: "16Gi"
    limits.cpu: "16"
    limits.memory: "32Gi"
    pods: "50"
```

**5. Backup Strategy**:
```bash
# Velero for Kubernetes backups
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace \
  --set configuration.backupStorageLocation.bucket=todo-backups \
  --set configuration.backupStorageLocation.config.region=us-ashburn-1

# Schedule daily backups
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces todo-phasev
```

**Implementation Steps**:
1. Create network policies (deny-all default, allow specific)
2. Setup RBAC with least-privilege service accounts
3. Apply Pod Security Standards (restricted profile)
4. Set resource quotas and limit ranges
5. Configure pod anti-affinity for HA
6. Setup Velero for backup/restore
7. Implement secrets encryption at rest
8. Regular vulnerability scanning (Trivy)
9. Document security hardening in `SECURITY.md`

---

## Implementation Timeline

### Week 1: Part A Foundation (Advanced Features)
- Day 1-2: Database schema evolution + migrations
- Day 3-4: Enhanced MCP tools implementation
- Day 5-7: Search & filter functionality + testing

### Week 2: Part A Event-Driven (Kafka)
- Day 8-9: Redpanda Cloud setup + Kafka integration
- Day 10-11: Notification Service implementation
- Day 12-13: Recurring Task Service implementation
- Day 14: Frontend ChatKit enhancements + E2E testing

### Week 3: Part B (Dapr Integration)
- Day 15-16: Dapr installation + component configuration
- Day 17-18: Service updates for Dapr Pub/Sub
- Day 19-20: Dapr Jobs API for reminders
- Day 21: Testing Dapr flow + Helm chart updates

### Week 4: Part C Setup (Cloud Infrastructure)
- Day 22-23: Oracle Cloud setup + OKE cluster creation
- Day 24-25: Production Helm configuration + TLS
- Day 26-27: CI/CD pipeline (GitHub Actions)
- Day 28: Initial production deployment + smoke tests

### Week 5: Part C Production (Monitoring & Hardening)
- Day 29-30: Prometheus + Grafana setup + dashboards
- Day 31-32: Logging (Loki) + alerting rules
- Day 33-34: Security hardening (RBAC, network policies)
- Day 35: Final testing, documentation, demo video

---

## Testing Strategy

### Unit Tests
- All MCP tools (add, list, complete, delete, update, search)
- RRULE parser
- Search service
- Filter/sort logic
- Event publishers
- **Target**: 80%+ backend coverage

### Integration Tests
- End-to-end chat flow with new features
- Kafka event publishing and consumption
- Database queries with advanced filters
- Dapr Pub/Sub integration
- **Target**: Cover all critical user journeys

### Load Tests
- HPA scaling with increased load
- Kafka throughput (events per second)
- Search performance with large datasets
- Concurrent task operations
- **Target**: 100 concurrent users, <2s p95 response time

### Resilience Tests
- Pod failures (delete pods, verify recovery)
- Database connection failures
- Kafka broker failures
- Dapr sidecar failures
- **Target**: Zero data loss, automatic recovery

### E2E Tests (Critical Flows)
1. User creates high-priority task with due date → receives reminder
2. User creates recurring task → task auto-regenerates on completion
3. User searches for tasks → relevant results returned
4. User filters by priority + due date → correct tasks shown
5. Events published to Kafka → consumers process correctly

---

## Documentation Requirements

### New Documentation Files
1. **`/specs/sphaseV/001-advanced-features/spec.md`**
   - Comprehensive specification for all Part A features
   - User stories, acceptance criteria, edge cases

2. **`/specs/sphaseV/002-dapr-integration/spec.md`**
   - Dapr architecture and component specifications
   - Migration from direct Kafka to Dapr Pub/Sub

3. **`/specs/sphaseV/003-cloud-deployment/spec.md`**
   - Production deployment requirements
   - CI/CD pipeline specifications
   - Security and monitoring standards

4. **`/phaseV/kubernetes/docs/ORACLE_CLOUD_SETUP.md`**
   - Step-by-step OKE cluster creation
   - OCI CLI configuration
   - Cost optimization tips

5. **`/phaseV/kubernetes/docs/DAPR_GUIDE.md`**
   - Dapr installation and configuration
   - Component usage examples
   - Troubleshooting common issues

6. **`/phaseV/kubernetes/docs/MONITORING_GUIDE.md`**
   - Prometheus/Grafana setup
   - Dashboard configuration
   - Alerting rules

7. **`/phaseV/DEPLOYMENT_RUNBOOK.md`**
   - Production deployment checklist
   - Rollback procedures
   - Incident response playbook

8. **Update `/phaseV/README.md`**
   - Add Phase V features overview
   - Cloud deployment instructions
   - Architecture diagrams with Kafka + Dapr

---

## Success Criteria

### Part A: Advanced Features
- ✅ All intermediate features working (priorities, tags, search, filter, sort)
- ✅ All advanced features working (due dates, reminders, recurring tasks)
- ✅ Kafka event flow functional (task events published and consumed)
- ✅ Notification Service sends reminders for due tasks
- ✅ Recurring Task Service auto-generates tasks
- ✅ PostgreSQL FTS search returns relevant results
- ✅ Multi-criteria filtering works correctly
- ✅ All 10+ MCP tools functional in ChatKit
- ✅ Backend test coverage ≥ 80%

### Part B: Dapr Integration
- ✅ Dapr installed and running on Minikube
- ✅ All 4 Dapr components configured (Pub/Sub, State, Secrets, Jobs)
- ✅ Services using Dapr Pub/Sub instead of direct Kafka
- ✅ Dapr Jobs API triggering reminders at scheduled times
- ✅ Helm chart updated with Dapr annotations
- ✅ No direct infrastructure dependencies in application code
- ✅ Dapr sidecar logs show successful operation

### Part C: Cloud Deployment
- ✅ OKE cluster running in Oracle Cloud (2 nodes, 4 OCPU each)
- ✅ Application deployed to production with HTTPS
- ✅ Let's Encrypt TLS certificates working
- ✅ CI/CD pipeline building and deploying on release tags
- ✅ Prometheus collecting metrics from all services
- ✅ Grafana dashboards showing application health
- ✅ Network policies enforcing pod-to-pod communication rules
- ✅ RBAC policies limiting service account permissions
- ✅ Backup strategy in place (Velero daily backups)
- ✅ Production environment stable for 7+ days

---

## Critical Files Summary

### Files to Create (52 new files)
**Backend (22 files)**:
- `app/models/category.py`, `app/models/tag.py`, `app/models/task_tag.py`
- `app/services/search_service.py`, `app/services/notification_service.py`, `app/services/recurring_task_service.py`
- `app/kafka/producer.py`, `app/kafka/events.py`
- `app/utils/rrule_parser.py`
- `alembic/versions/YYYYMMDD_add_advanced_task_fields.py`
- Multiple new MCP tools

**Kubernetes (15 files)**:
- `helm/todo-app/templates/notification-deployment.yaml`
- `helm/todo-app/templates/recurring-deployment.yaml`
- `helm/todo-app/templates/networkpolicy.yaml`
- `helm/todo-app/templates/prometheus-servicemonitor.yaml`
- `helm/todo-app/values-production.yaml`
- `dapr-components/pubsub-kafka.yaml`
- `dapr-components/statestore-postgres.yaml`
- `dapr-components/secrets-kubernetes.yaml`
- `dapr-components/jobs-scheduler.yaml`
- `docs/ORACLE_CLOUD_SETUP.md`
- `docs/DAPR_GUIDE.md`
- `docs/MONITORING_GUIDE.md`

**CI/CD (2 files)**:
- `.github/workflows/ci-phase-v.yml`
- `.github/workflows/deploy-production.yml`

**Specifications (3 files)**:
- `specs/sphaseV/001-advanced-features/spec.md`
- `specs/sphaseV/002-dapr-integration/spec.md`
- `specs/sphaseV/003-cloud-deployment/spec.md`

**Terraform (Optional, 3 files)**:
- `kubernetes/terraform/main.tf`
- `kubernetes/terraform/variables.tf`
- `kubernetes/terraform/outputs.tf`

### Files to Modify (12 files)
**Backend (5 files)**:
- `app/models/task.py` (add new fields)
- `app/mcp/tools.py` (enhance existing tools, add new tools)
- `app/main.py` (add Prometheus metrics)
- `app/chatkit/task_server.py` (update system prompt)

**Frontend (1 file)**:
- `src/app/chat/page.tsx` (update suggested prompts)

**Kubernetes (5 files)**:
- `helm/todo-app/values.yaml` (add Dapr, monitoring config)
- `helm/todo-app/templates/backend-deployment.yaml` (add Dapr annotations, security context)
- `helm/todo-app/templates/frontend-deployment.yaml` (add Dapr annotations)
- `helm/todo-app/templates/mcp-deployment.yaml` (add Dapr annotations)
- `helm/todo-app/Chart.yaml` (bump version)

**Documentation (1 file)**:
- `README.md` (add Phase V overview)

---

## Risk Mitigation

### High-Risk Areas
1. **Kafka Integration Complexity**
   - **Risk**: Event ordering issues, duplicate processing
   - **Mitigation**: Use idempotent consumers, exactly-once semantics, proper consumer group configuration

2. **Dapr Learning Curve**
   - **Risk**: Team unfamiliar with Dapr concepts
   - **Mitigation**: Start with simple Pub/Sub, add components incrementally, extensive testing

3. **Cloud Cost Overruns**
   - **Risk**: Oracle Cloud free tier exceeded
   - **Mitigation**: Use Oracle always-free tier (4 OCPU limit), monitor usage dashboards, set billing alerts

4. **Production Stability**
   - **Risk**: New features cause outages
   - **Mitigation**: Canary deployments, extensive testing, rollback procedures, feature flags

5. **Database Schema Migrations**
   - **Risk**: Migration failures on production database
   - **Mitigation**: Test on staging first, backup before migration, reversible migrations

### Rollback Plan
1. **Part A Issues**: Revert database migration, deploy previous Helm chart version
2. **Part B Issues**: Disable Dapr annotations, fallback to direct Kafka
3. **Part C Issues**: Use `helm rollback` to previous release, DNS cutover to Minikube

---

## Next Steps After Plan Approval

1. **Constitutional Update**: Amend constitution to v3.0.0 with Phase V principles
2. **Create Specifications**: Write comprehensive specs in `/specs/sphaseV/`
3. **Setup Redpanda Cloud**: Create account and Kafka cluster
4. **Database Migration**: Implement schema changes first
5. **Iterative Development**: Implement features in order, test continuously
6. **Documentation**: Update docs as features are completed
7. **Cloud Setup**: Create Oracle Cloud account early (provisioning takes time)
8. **CI/CD Pipeline**: Setup GitHub Actions before first production deployment

---

## Conclusion

This plan provides a complete roadmap for Phase V implementation, transforming the todo application into a production-grade, event-driven, cloud-native system. By following the sequential approach (A → B → C) and building on the solid Phase IV foundation, we'll deliver all hackathon requirements while maintaining code quality, security, and operational excellence.

The key success factors are:
- **Spec-Driven Development**: Write comprehensive specs before implementation
- **Incremental Testing**: Test each component thoroughly before moving to the next
- **Cloud-Native Patterns**: Leverage Kubernetes, Dapr, and managed services
- **Production Mindset**: Security, monitoring, and reliability from day one

Let's build an impressive Phase V submission! 🚀
