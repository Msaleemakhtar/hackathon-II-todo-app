# Kubernetes Deployment Guide for Naive Developers

> **Complete step-by-step guide to deploy the AI Task Assistant on Kubernetes**
>
> No prior Kubernetes knowledge required! This guide explains everything.

---

## 📚 Table of Contents

1. [What is Kubernetes?](#what-is-kubernetes)
2. [Architecture Flow](#architecture-flow)
3. [Prerequisites](#prerequisites)
4. [Installation Steps](#installation-steps)
5. [Understanding the Deployment](#understanding-the-deployment)
6. [Configuration](#configuration)
7. [Deployment](#deployment)
8. [Verification](#verification)
9. [Using kubectl-ai](#using-kubectl-ai)
10. [Troubleshooting](#troubleshooting)
11. [Cleanup](#cleanup)

---

## 🤔 What is Kubernetes?

**Kubernetes (K8s)** is like a smart manager for your applications that run in containers (Docker).

**Think of it like this:**
- **Docker** = Individual shipping containers
- **Kubernetes** = The entire port with cranes, trucks, and logistics that manage those containers

**What Kubernetes does for us:**
- **Auto-healing**: Restarts crashed containers
- **Scaling**: Adds more containers when traffic increases  
- **Load balancing**: Distributes traffic across containers
- **Rolling updates**: Updates apps without downtime
- **Secret management**: Stores passwords securely

**Minikube** = Kubernetes running on your local computer for development

---

## 🏗️ Architecture Flow

### How Requests Flow Through the System

This section explains how a user request travels from your browser all the way to the database and back. Understanding this flow helps you debug issues and understand how each component works.

#### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                  │
│                     (Browser/Client)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS Request
                             │ (https://todo-app.local/*)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX INGRESS CONTROLLER                      │
│                   (Load Balancer + Router)                       │
│                                                                   │
│  • Terminates TLS (HTTPS → HTTP)                                │
│  • Routes based on path:                                         │
│    - /chat, /login, / → Frontend Service                        │
│    - /api/* → Backend Service (except /api/auth)                │
│  • Adds headers (X-Forwarded-*, etc.)                           │
└──────────────┬────────────────────────────┬─────────────────────┘
               │                            │
               │ /chat, /, /login          │ /api/*
               ▼                            ▼
┌──────────────────────────┐    ┌──────────────────────────────────┐
│   FRONTEND SERVICE       │    │     BACKEND SERVICE              │
│   (ClusterIP: 3000)      │    │     (ClusterIP: 8000)            │
│                          │    │                                  │
│   Load balances to:      │    │   Load balances to:              │
│   ├─ frontend-pod-1      │    │   ├─ backend-pod-1               │
│   └─ frontend-pod-2      │    │   └─ backend-pod-2               │
└──────────┬───────────────┘    └────────────┬─────────────────────┘
           │                                 │
           │ Serves HTML/JS/CSS              │ REST API + ChatKit
           ▼                                 ▼
┌──────────────────────────┐    ┌──────────────────────────────────┐
│   FRONTEND POD           │    │     BACKEND POD                  │
│   (Next.js 16)           │    │     (FastAPI + Python)           │
│                          │    │                                  │
│   • Server-side render   │    │   • ChatKit SDK adapter          │
│   • ChatKit UI component │    │   • JWT authentication           │
│   • Auth client (Better) │    │   • Rate limiting                │
│   • Static assets        │    │   • MCP tool orchestration       │
└──────────────────────────┘    └────┬──────┬──────┬───────────────┘
                                     │      │      │
                    ┌────────────────┘      │      └──────────────┐
                    │                       │                     │
                    │ Chat messages         │ Session cache       │ Task operations
                    │ (POST /chatkit)       │ (GET/SET)          │ (MCP tools)
                    ▼                       ▼                     ▼
      ┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
      │  MCP SERVICE         │  │  REDIS SERVICE   │  │  NEON POSTGRESQL     │
      │  (ClusterIP: 8001)   │  │  (ClusterIP:     │  │  (External Cloud)    │
      │                      │  │   6379)          │  │                      │
      │  Routes to:          │  │                  │  │  • User auth data    │
      │  └─ mcp-server-pod   │  │  Routes to:      │  │  • Task data         │
      └──────────┬───────────┘  │  └─ redis-0      │  │  • Conversation      │
                 │              │    (StatefulSet) │  │    history           │
                 │              └──────────────────┘  │  • Session data      │
                 │                                    └──────────────────────┘
                 │ Executes tools
                 │ (add_task, list_tasks, etc.)
                 ▼
      ┌──────────────────────┐
      │   MCP SERVER POD     │
      │   (FastMCP)          │
      │                      │
      │   • Task tools       │
      │   • Database access  │────────────────────────────┐
      │   • Tool validation  │                            │
      └──────────────────────┘                            │
                                                          │ Direct DB access
                                                          │ (for task CRUD)
                                                          ▼
                                              ┌──────────────────────┐
                                              │  NEON POSTGRESQL     │
                                              │  (External Cloud)    │
                                              │                      │
                                              │  Tables:             │
                                              │  • users             │
                                              │  • tasks             │
                                              │  • sessions          │
                                              │  • threads           │
                                              │  • messages          │
                                              └──────────────────────┘
```

#### Detailed Request Flow Examples

##### 1. User Opens Chat Page (`https://todo-app.local/chat`)

**Step-by-step flow:**

```
1. Browser → HTTPS Request
   GET https://todo-app.local/chat

2. DNS Resolution
   /etc/hosts → todo-app.local → <minikube-ip>

3. Ingress Controller (Nginx)
   ├─ Receives request on port 443 (HTTPS)
   ├─ Terminates TLS using todo-app-tls secret
   ├─ Matches path "/" to frontend service (path: /(.*))
   └─ Forwards to: http://frontend-service:3000/chat

4. Frontend Service (ClusterIP)
   ├─ Load balances to one of: frontend-pod-1 or frontend-pod-2
   └─ Forwards to: http://<pod-ip>:3000/chat

5. Frontend Pod (Next.js)
   ├─ Server-side renders page
   ├─ Includes ChatKit SDK script from OpenAI CDN
   ├─ Fetches user session from Better Auth
   └─ Returns: HTML + JavaScript

6. Browser Receives Response
   ├─ Renders HTML
   ├─ Loads ChatKit web component
   └─ ChatKit initializes with config (domain key, API URL)
```

**What you see:** Chat interface loads with "Welcome!" greeting and prompt suggestions.

##### 2. User Sends Chat Message ("Show me my tasks")

**Step-by-step flow:**

```
1. ChatKit UI → POST Request
   POST https://todo-app.local/api/chatkit
   Headers:
     Authorization: Bearer <jwt-token>
     Content-Type: application/json
   Body:
     {
       "type": "chat.create_message",
       "params": {
         "thread_id": "thread_abc123",
         "content": "Show me my tasks"
       }
     }

2. Ingress Controller
   ├─ Receives on port 443 (HTTPS)
   ├─ Terminates TLS
   ├─ Matches path "/api/chatkit" to backend service
   │  (path: /api/(?!auth)(.*))
   └─ Forwards to: http://backend-service:8000/chatkit

3. Backend Service
   ├─ Load balances to: backend-pod-1 or backend-pod-2
   └─ Forwards to: http://<pod-ip>:8000/chatkit

4. Backend Pod (FastAPI)
   ├─ Rate limiting check (10 req/min)
   ├─ JWT authentication (extract user_id)
   ├─ Input sanitization
   └─ Forwards to: ChatKit SDK adapter

5. ChatKit SDK Adapter (app/chatkit/server.py)
   ├─ Creates user context: {"user_id": "user_123"}
   ├─ Calls: task_server.process(body, context)
   └─ Agent determines intent: "List user's tasks"

6. Agent Decides to Use MCP Tool
   ├─ Identifies: list_tasks tool needed
   ├─ Calls MCP server: http://mcp-service:8001/mcp
   └─ Sends: list_tasks(user_id="user_123", status="all")

7. MCP Service
   └─ Routes to: mcp-server-pod

8. MCP Server Pod (FastMCP)
   ├─ Receives tool call: list_tasks
   ├─ Validates user_id matches context
   ├─ Queries database:
   │  SELECT * FROM tasks
   │  WHERE user_id = 'user_123'
   │  ORDER BY created_at DESC
   └─ Returns: [{"id": 1, "title": "Buy groceries", ...}, ...]

9. MCP → Database (Neon PostgreSQL)
   ├─ Connects via: DATABASE_URL secret
   ├─ Executes SQL query
   └─ Returns: Task rows

10. Response Flows Back
    MCP Server → Backend → ChatKit SDK → OpenAI API

11. OpenAI Generates Response
    ├─ Receives tool results
    ├─ Generates natural language response
    └─ Returns: "You have 3 tasks: 1. Buy groceries..."

12. Backend Streams Response
    ├─ Wraps in Server-Sent Events (SSE)
    ├─ Streams to client chunk by chunk
    └─ HTTP/1.1 200 OK
       Content-Type: text/event-stream

13. ChatKit UI Receives Stream
    ├─ Displays message progressively
    └─ Stores in thread history
```

**What you see:** AI assistant responds with your task list in conversational format.

##### 3. Session Caching Flow (Redis)

**When caching occurs:**

```
1. User Login
   ├─ Better Auth creates session
   ├─ Backend stores in Redis:
   │  SET session:abc123 {"user_id": "user_123", "exp": 1234567890}
   │  EXPIRE session:abc123 3600  # 1 hour TTL
   └─ Returns JWT token to frontend

2. Subsequent Requests
   ├─ Frontend sends: Authorization: Bearer <jwt>
   ├─ Backend checks Redis cache:
   │  GET session:abc123
   └─ Cache hit → Skip database lookup (faster!)

3. Cache Miss (session expired or not cached)
   ├─ Backend queries PostgreSQL
   ├─ Validates session
   └─ Stores in Redis for next request
```

**Redis Service Flow:**

```
Backend Pod → Redis Service (redis-service:6379)
              └─ Routes to: redis-0 (StatefulSet)
                  └─ Persistent storage: PVC (redis-data-redis-0)
```

#### Component Communication Summary

| From | To | Protocol | Purpose | Example |
|------|-----|----------|---------|---------|
| **Browser** | **Ingress** | HTTPS (443) | User requests | `GET /chat` |
| **Ingress** | **Frontend** | HTTP (3000) | Page requests | `GET /chat` |
| **Ingress** | **Backend** | HTTP (8000) | API requests | `POST /api/chatkit` |
| **Frontend** | **Backend** | HTTP (8000) | API calls | `POST /api/chatkit` |
| **Backend** | **MCP Server** | HTTP (8001) | Tool execution | `POST /mcp` (list_tasks) |
| **Backend** | **Redis** | Redis protocol (6379) | Cache operations | `GET session:abc123` |
| **Backend** | **PostgreSQL** | PostgreSQL (5432) | Auth & data | `SELECT * FROM users` |
| **MCP Server** | **PostgreSQL** | PostgreSQL (5432) | Task operations | `SELECT * FROM tasks` |

#### Service Types Explained

**ClusterIP (Internal Services):**
- `frontend-service:3000` - Only accessible within cluster
- `backend-service:8000` - Only accessible within cluster
- `mcp-service:8001` - Only accessible within cluster
- `redis-service:6379` - Only accessible within cluster

**Ingress (External Access):**
- `todo-app.local` - Accessible from your browser
- Routes external traffic to internal ClusterIP services

**External Service:**
- Neon PostgreSQL - Cloud-hosted, accessed via internet

#### Path-Based Routing (Ingress)

```
https://todo-app.local/chat
└─ Matches: path: /(.*)
   └─ Routes to: frontend-service:3000

https://todo-app.local/api/health
└─ Matches: path: /api/(?!auth)(.*)
   └─ Routes to: backend-service:8000
   └─ Rewrites to: /health (strips /api prefix)

https://todo-app.local/api/chatkit
└─ Matches: path: /api/(?!auth)(.*)
   └─ Routes to: backend-service:8000
   └─ Rewrites to: /chatkit
```

**Why `/api/(?!auth)` pattern?**
- Matches: `/api/*` EXCEPT `/api/auth/*`
- Better Auth handles its own `/api/auth` routes in frontend
- Backend handles all other `/api/*` routes

#### TLS/HTTPS Flow

```
1. Browser Initiates TLS Handshake
   ├─ ClientHello → Ingress Controller
   └─ Supports TLS 1.2, TLS 1.3

2. Ingress Controller Responds
   ├─ ServerHello
   ├─ Presents certificate from: todo-app-tls secret
   └─ Certificate: CN=todo-app.local (self-signed)

3. Browser Validates Certificate
   ├─ Self-signed → Shows warning
   ├─ User accepts risk (dev environment)
   └─ Establishes encrypted connection

4. Encrypted Communication
   ├─ All traffic encrypted in transit
   └─ Ingress decrypts → forwards plain HTTP internally
```

**Why HTTPS is required:**
- ChatKit SDK requires secure context for `crypto.randomUUID()`
- Protects JWT tokens in transit
- Prevents man-in-the-middle attacks

#### Auto-Scaling Flow (HPA)

```
1. Metrics Server Collects Data
   ├─ Polls kubelet every 15 seconds
   └─ Gets CPU/Memory usage per pod

2. HPA Reads Metrics
   ├─ Every 15 seconds
   ├─ Calculates: current_usage / target_usage
   └─ Example: 85% CPU / 70% target = 1.21 ratio

3. HPA Decides to Scale
   ├─ Ratio > 1.1 → Scale up
   ├─ Ratio < 0.9 → Scale down
   └─ Respects: minReplicas (2) and maxReplicas (5)

4. HPA Updates Deployment
   ├─ kubectl scale deployment/backend --replicas=3
   └─ Deployment creates new pod

5. New Pod Joins Service
   ├─ Pod becomes Ready
   ├─ Added to backend-service endpoints
   └─ Ingress starts routing traffic to it
```

#### Health Check Flow

```
1. Kubelet Executes Probes (every 10s)

2. Liveness Probe (Is pod alive?)
   ├─ HTTP GET: http://<pod-ip>:8000/health
   ├─ Success (200 OK) → Pod is alive
   └─ Failure (3 consecutive) → Restart pod

3. Readiness Probe (Ready for traffic?)
   ├─ HTTP GET: http://<pod-ip>:8000/health
   ├─ Success → Add to service endpoints
   └─ Failure → Remove from service (stop traffic)

4. Startup Probe (First-time startup)
   ├─ HTTP GET: http://<pod-ip>:8000/health
   ├─ Success → Enable liveness/readiness probes
   └─ Failure (30 attempts) → Pod failed to start
```

#### Data Persistence

**Ephemeral (Lost on pod restart):**
- Frontend pod filesystem
- Backend pod filesystem
- MCP Server pod filesystem

**Persistent (Survives pod restart):**
- Redis data (PersistentVolumeClaim: `redis-data-redis-0`)
  - Mounted at: `/data` in redis-0 pod
  - Stores: `dump.rdb` (Redis snapshot)
- PostgreSQL (Neon Cloud - always persistent)

**Example: Redis pod restart:**
```
1. kubectl delete pod redis-0
2. StatefulSet recreates redis-0
3. New pod mounts SAME PVC: redis-data-redis-0
4. Redis loads data from /data/dump.rdb
5. Data restored! ✅
```

---

## ✅ Prerequisites

### Required Software

#### 1. Docker
**What it is**: Packages your application into containers
**Why we need it**: Kubernetes runs containerized applications

\`\`\`bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker \$USER
newgrp docker

# Verify
docker --version
# Expected: Docker version 24.0.0 or higher
\`\`\`

#### 2. Minikube
**What it is**: Local Kubernetes cluster
**Why we need it**: Run Kubernetes on your laptop

\`\`\`bash
# Install Minikube (Linux)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
minikube version
# Expected: minikube version: v1.32.0 or higher
\`\`\`

#### 3. kubectl
**What it is**: Command-line tool to control Kubernetes
**Why we need it**: Interact with your cluster

\`\`\`bash
# Install kubectl (Linux)
curl -LO "https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
# Expected: Client Version: v1.28.0 or higher
\`\`\`

#### 4. Helm
**What it is**: Package manager for Kubernetes (like npm for Node.js)
**Why we need it**: Simplifies complex deployments

\`\`\`bash
# Install Helm (Linux)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
# Expected: version.BuildInfo{Version:"v3.13.0" or higher}
\`\`\`

#### 5. kubectl-ai (Optional but Recommended)
**What it is**: AI-powered kubectl assistant
**Why we need it**: Makes Kubernetes commands easier with natural language

\`\`\`bash
# Install kubectl-ai
brew install kubectl-ai  # macOS
# Or download from: https://github.com/sozercan/kubectl-ai

# Configure with OpenAI API key
export OPENAI_API_KEY=your-api-key-here

# Test it
kubectl-ai "show me all namespaces"
\`\`\`

---

## 🚀 Quick Start

### Step 1: Start Minikube

\`\`\`bash
# Start Minikube with adequate resources
minikube start \\
  --cpus=4 \\
  --memory=8192 \\
  --driver=docker

# Enable ingress addon
minikube addons enable ingress

# Verify
minikube status
\`\`\`

**With kubectl-ai:**
\`\`\`bash
kubectl-ai "is my minikube cluster healthy"
\`\`\`

### Step 2: Add Hostname

\`\`\`bash
# Add to /etc/hosts
echo "\$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts
\`\`\`

### Step 3: Prepare Secrets

\`\`\`bash
cd phaseIV/kubernetes/helm/todo-app

# Create values-local.yaml with your secrets
cp values-local.yaml.example values-local.yaml
nano values-local.yaml

# Add your:
# - DATABASE_URL (Neon PostgreSQL - base64 encoded)
# - OPENAI_API_KEY (base64 encoded)
# - BETTER_AUTH_SECRET (base64 encoded)
# - CHATKIT_DOMAIN_KEY (plain text in configMap)
\`\`\`

**How to base64 encode:**
\`\`\`bash
echo -n "your-secret-value" | base64
\`\`\`

### Step 4: Build Docker Images

\`\`\`bash
# Set Minikube Docker environment
eval \$(minikube docker-env)

cd phaseIV

# Build frontend
docker build \\
  --build-arg NEXT_PUBLIC_API_URL=https://todo-app.local/api \\
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=https://todo-app.local \\
  --build-arg NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your_domain_key \\
  -t todo-frontend:latest \\
  frontend

# Build backend
docker build -t todo-backend:latest backend
\`\`\`

### Step 5: Create TLS Certificates

\`\`\`bash
cd kubernetes/helm/todo-app
mkdir -p certs

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
  -keyout certs/tls.key \\
  -out certs/tls.crt \\
  -subj "/CN=todo-app.local/O=TodoApp" \\
  -addext "subjectAltName=DNS:todo-app.local,DNS:*.todo-app.local"

# Create Kubernetes secret
kubectl create secret tls todo-app-tls \\
  --cert=certs/tls.crt \\
  --key=certs/tls.key \\
  -n todo-phaseiv \\
  --dry-run=client -o yaml | kubectl apply -f -
\`\`\`

### Step 6: Deploy with Helm

\`\`\`bash
cd ../..

helm install todo-app todo-app \\
  -n todo-phaseiv \\
  --create-namespace \\
  -f todo-app/values-local.yaml \\
  -f todo-app/values-tls.yaml \\
  --wait \\
  --timeout 10m
\`\`\`

**With kubectl-ai:**
\`\`\`bash
kubectl-ai "install helm chart in todo-phaseiv namespace"
\`\`\`

### Step 7: Verify Deployment

\`\`\`bash
# Check all pods are running
kubectl get pods -n todo-phaseiv

# Expected: All pods showing 1/1 READY and Running status
\`\`\`

**With kubectl-ai:**
\`\`\`bash
kubectl-ai "are all my pods healthy in todo-phaseiv"
\`\`\`

### Step 8: Access the App

1. **Trust the certificate**:
   - **Chrome/Edge**: Visit https://todo-app.local/chat, click anywhere, type `thisisunsafe`
   - **Firefox**: Click "Advanced" → "Accept the Risk"

2. **Test the app**: Go to https://todo-app.local/chat

---

## 🤖 Using kubectl-ai (Natural Language Commands)

### Basic Commands

\`\`\`bash
# View cluster status
kubectl-ai "show me all pods in todo-phaseiv"
kubectl-ai "are all my pods healthy"
kubectl-ai "which pods are using the most memory"

# Logs
kubectl-ai "show me the last 50 lines of backend logs"
kubectl-ai "find errors in frontend pods"

# Troubleshooting
kubectl-ai "why is my frontend pod not starting"
kubectl-ai "debug ingress routing issues"

# Resource usage
kubectl-ai "show CPU usage for all pods"
kubectl-ai "is my cluster running out of resources"

# Scaling
kubectl-ai "scale frontend to 3 replicas"
kubectl-ai "show autoscaling status"

# Updates
kubectl-ai "restart all deployments in todo-phaseiv"
kubectl-ai "rollback frontend deployment"
\`\`\`

---

## 🐛 Troubleshooting

### Issue: Pods in CrashLoopBackOff

\`\`\`bash
# Check logs
kubectl logs <pod-name> -n todo-phaseiv

# With kubectl-ai
kubectl-ai "why is backend pod crash looping"

# Common fixes:
# 1. Check secrets
kubectl get secret todo-app-secrets -n todo-phaseiv

# 2. Verify DATABASE_URL
kubectl exec -n todo-phaseiv deploy/backend -- env | grep DATABASE_URL

# 3. Restart
kubectl rollout restart deployment/backend -n todo-phaseiv
\`\`\`

### Issue: Ingress Not Working

\`\`\`bash
# Check /etc/hosts
cat /etc/hosts | grep todo-app.local

# Check ingress controller
kubectl get pods -n ingress-nginx

# With kubectl-ai
kubectl-ai "debug why ingress is not routing traffic"

# Fix:
echo "\$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts
minikube addons enable ingress
\`\`\`

### Issue: ChatKit Not Loading

\`\`\`bash
# Must access via HTTPS!
# URL: https://todo-app.local/chat (not http://)

# Check TLS secret
kubectl get secret todo-app-tls -n todo-phaseiv

# With kubectl-ai
kubectl-ai "is TLS configured correctly for ingress"

# Fix: Trust certificate
# Chrome: Type 'thisisunsafe'
# Firefox: Accept risk
\`\`\`

### Issue: 500 Internal Server Error

\`\`\`bash
# Check backend logs
kubectl logs -n todo-phaseiv -l app=backend --tail=100

# Check MCP server
kubectl get pods -n todo-phaseiv -l app=mcp-server

# With kubectl-ai
kubectl-ai "show errors in backend and mcp-server pods"

# Test MCP connectivity
kubectl exec -n todo-phaseiv deploy/backend -- \\
  curl -s http://mcp-service:8001/mcp
\`\`\`

---

## 🧹 Cleanup

\`\`\`bash
# Uninstall application
helm uninstall todo-app -n todo-phaseiv

# Delete namespace
kubectl delete namespace todo-phaseiv

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete

# Remove from /etc/hosts
sudo sed -i '/todo-app.local/d' /etc/hosts
\`\`\`

**With kubectl-ai:**
\`\`\`bash
kubectl-ai "completely remove todo-app from cluster"
\`\`\`

---

## 📚 Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [OpenAI ChatKit](https://platform.openai.com/docs/chatkit)

---

**Built with ❤️ for developers learning Kubernetes**
