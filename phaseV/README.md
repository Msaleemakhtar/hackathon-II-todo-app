# Phase V: Event-Driven AI Task Assistant - Kubernetes Deployment

> **Production-ready Kubernetes deployment with HTTPS, OpenAI ChatKit, Kafka event streaming, SMTP email notifications, and scalable microservices architecture**

## 🎯 What is This?

Phase V is an event-driven AI-powered task management application deployed on Kubernetes. It allows users to manage their tasks through natural conversation using OpenAI's ChatKit, with automatic email reminders, recurring tasks, and fast full-text search powered by Kafka (Redpanda Cloud) and PostgreSQL.

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

## 🏗️ Event-Driven Architecture

Phase V implements a robust event-driven architecture using **Kafka (Redpanda Cloud)** for asynchronous task processing with three specialized consumer services:

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Nginx Ingress                          │
│                    (https://todo-app.local)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
               ┌───────────┴───────────┐
               │                       │
       ┌───────▼────────┐      ┌──────▼──────┐
       │   Frontend     │      │   Backend   │
       │  (Next.js)     │◄────►│  (FastAPI)  │
       │  Port: 3000    │      │  Port: 8000 │
       │  Replicas: 2   │      │  + Kafka    │
       └────────────────┘      │  Producer   │
                               └──────┬──────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
            ┌───────▼──────┐  ┌──────▼─────┐  ┌───────▼────────┐
            │  MCP Server  │  │   Redis    │  │   PostgreSQL   │
            │   (Tools)    │  │  (Cache)   │  │ (Neon Cloud)   │
            │  Port: 8001  │  │ Port: 6379 │  │ + Full-text    │
            └──────────────┘  └────────────┘  │    Search      │
                                               └────────────────┘
                                      │
                         Publishes Events to
                              Kafka Topics
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
    ┌──────▼──────┐          ┌────────▼────────┐       ┌────────▼────────┐
    │task-events  │          │task-reminders   │       │task-recurrence  │
    │  (Topic)    │          │    (Topic)      │       │    (Topic)      │
    │ 3 partitions│          │  1 partition    │       │  1 partition    │
    │ 7d retention│          │  1d retention   │       │  7d retention   │
    └──────┬──────┘          └────────┬────────┘       └────────┬────────┘
           │                          │                          │
           │                          │                          │
    ┌──────▼──────────┐      ┌────────▼──────────┐     ┌────────▼────────┐
    │ Notification    │      │ Email Delivery    │     │ Recurring Task  │
    │   Service       │      │    Service        │     │    Service      │
    │  (Consumer)     │      │   (Consumer)      │     │   (Consumer)    │
    │  Port: 8002     │      │   Port: 8003      │     │   Port: 8004    │
    │  Replicas: 1    │      │   Replicas: 1     │     │   Replicas: 1   │
    └─────────────────┘      └──────────┬────────┘     └─────────────────┘
           │                             │                      │
           │ Polls DB every 5s           │ SMTP                 │ Creates new
           │ for due tasks               │ (Gmail)              │ task instance
           │                             │                      │
           └─> Publishes                 └─> Sends              └─> Publishes
               ReminderSentEvent            Email                  TaskCreatedEvent
               to task-reminders            Notification           to task-events
```

### Event Flows

#### 1. Task Creation Flow
```
User creates task via ChatKit
        ↓
Backend MCP Tool (add_task)
        ↓
Save to PostgreSQL
        ↓
Publish TaskCreatedEvent → task-events topic
        ↓
(Future: Notification Service could consume for welcome email)
```

#### 2. Reminder Flow
```
Notification Service (Kafka Producer + Consumer)
        ↓
Polls PostgreSQL every 5 seconds
        ↓
Finds tasks due within 1 hour (reminder_sent = false)
        ↓
Publishes ReminderSentEvent → task-reminders topic
        ↓
Email Delivery Service (Kafka Consumer)
        ↓
Consumes ReminderSentEvent
        ↓
Sends email via SMTP (Gmail)
        ↓
Logs delivery status
```

#### 3. Recurring Task Flow
```
User completes recurring task via ChatKit
        ↓
Backend MCP Tool (complete_task)
        ↓
Mark task complete in PostgreSQL
        ↓
Publish TaskCompletedEvent → task-recurrence topic
        ↓
Recurring Task Service (Kafka Consumer)
        ↓
Consumes TaskCompletedEvent
        ↓
Parse iCalendar RRULE (e.g., FREQ=DAILY;COUNT=5)
        ↓
Calculate next occurrence date
        ↓
Create new task instance in PostgreSQL
        ↓
Publish TaskCreatedEvent → task-events topic
        ↓
(Cycle continues automatically)
```

### Services Overview

| Service | Type | Purpose | Port | Replicas | Critical |
|---------|------|---------|------|----------|----------|
| **Backend** | Producer + API | FastAPI + MCP tools, publishes events | 8000 | 2-5 | Yes |
| **Notification Service** | Producer + Consumer | Polls DB, publishes reminders | 8002 | 1 | No |
| **Email Delivery** | Consumer | Sends SMTP emails for reminders | 8003 | 1 | No |
| **Recurring Task** | Consumer | Regenerates recurring tasks | 8004 | 1 | No |
| **Frontend** | UI | Next.js + ChatKit interface | 3000 | 2-5 | Yes |
| **MCP Server** | Tool Executor | Executes MCP tool calls | 8001 | 1 | Yes |

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

All consumer services implement:
- ✅ **Graceful degradation**: Services start even if Kafka is temporarily unavailable
- ✅ **Automatic retry**: Connection retries every 30 seconds (up to 10 attempts)
- ✅ **Health checks**: Kubernetes liveness/readiness probes
- ✅ **Manual commit**: Consumers manually commit offsets for exactly-once processing
- ✅ **Error handling**: Failed messages are logged, service continues
- ✅ **Background consumption**: Non-blocking event consumption in separate asyncio tasks

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

```bash
# Required tools
- Minikube (local Kubernetes cluster)
- kubectl (Kubernetes CLI)
- Helm 3.13+
- Docker
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

**Step 2: Setup Redpanda Cloud (Kafka)**

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

**Step 3: Setup Gmail SMTP**

1. Enable 2-Step Verification on your Google account
2. Generate an App Password:
   - Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
3. Note your:
   - Gmail address (e.g., `your-email@gmail.com`)
   - App password

**Step 4: Create Secrets Configuration**

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

**Step 5: Build Docker Images**

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

**Step 6: Deploy to Kubernetes**

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

# Expected output:
# NAME                                  READY   STATUS    RESTARTS   AGE
# backend-xxxxxxxxxx-xxxxx              1/1     Running   0          2m
# email-delivery-xxxxxxxxxx-xxxxx       1/1     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx             1/1     Running   0          2m
# mcp-server-xxxxxxxxxx-xxxxx           1/1     Running   0          2m
# notification-service-xxxxxxxxxx-xxxxx 1/1     Running   0          2m
# recurring-service-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
# redis-0                               1/1     Running   0          2m
```

**Step 7: Access the App**

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

**Backend (FastAPI + Kafka Producer)**
```yaml
DATABASE_URL: PostgreSQL connection string
OPENAI_API_KEY: OpenAI API key
BETTER_AUTH_SECRET: JWT signing secret
MCP_SERVER_URL: http://mcp-service:8001/mcp
REDIS_HOST: redis-service
CORS_ORIGINS: JSON array of allowed origins
KAFKA_BOOTSTRAP_SERVERS: Kafka broker addresses
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

#### 1. Kafka Connection Failures

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

#### 2. Email Delivery Not Working

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

#### 3. Recurring Tasks Not Working

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

#### 4. Pods in CrashLoopBackOff

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

#### 5. ChatKit Not Loading

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

- **Kubernetes Guide**: `kubernetes/docs/KUBERNETES_GUIDE.md`
- **Runbook**: `kubernetes/docs/RUNBOOK.md`
- **Architecture**: `kubernetes/docs/architecture-diagram.md`
- **ADRs**: `history/adr/*.md`
- **Issues**: [GitHub Issues](https://github.com/your-org/your-repo/issues)

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
- [Kafka/Redpanda](https://docs.redpanda.com/) - Event streaming platform
- [aiokafka](https://aiokafka.readthedocs.io/) - Python async Kafka client
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org/docs) - React framework
- [OpenAI ChatKit](https://platform.openai.com/docs/chatkit) - AI chat interface
- [Better Auth](https://better-auth.com) - Authentication library
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [iCalendar RRULE](https://icalendar.org/rrule-tool.html) - Recurrence rule standard

---

**Built with ❤️ using Kubernetes, Kafka, Next.js, FastAPI, and OpenAI ChatKit**

**Phase V: Event-Driven Architecture Edition**
