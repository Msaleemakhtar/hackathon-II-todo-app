# Phase IV: AI Task Assistant - Kubernetes Deployment

> **Production-ready Kubernetes deployment with HTTPS, OpenAI ChatKit, and scalable microservices architecture**

## 🎯 What is This?

Phase IV is a complete AI-powered task management application deployed on Kubernetes. It allows users to manage their tasks through natural conversation using OpenAI's ChatKit.

**Key Features:**
- 🤖 AI-powered task management via natural language
- 🔐 Secure authentication with Better Auth + JWT
- 🌐 HTTPS with self-signed certificates
- ⚡ Auto-scaling based on CPU/memory usage
- 🗄️ PostgreSQL database (Neon serverless)
- 💾 Redis for session caching
- 🔧 MCP (Model Context Protocol) tool integration
- 📊 Horizontal Pod Autoscaling (HPA)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

```bash
# Required tools
- Minikube (local Kubernetes)
- kubectl (Kubernetes CLI)
- Helm 3.13+
- Docker

# Optional but recommended
- kubectl-ai (AI-powered kubectl assistant)
```

### Installation

**Step 1: Start Minikube**

```bash
# Start with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable nginx ingress
minikube addons enable ingress

# Verify
minikube status
```

**Step 2: Setup Secrets**

```bash
# Create values-local.yaml with your secrets
cp kubernetes/helm/todo-app/values-local.yaml.example kubernetes/helm/todo-app/values-local.yaml

# Edit with your values:
# - DATABASE_URL (Neon PostgreSQL)
# - OPENAI_API_KEY
# - BETTER_AUTH_SECRET
nano kubernetes/helm/todo-app/values-local.yaml
```

**Step 3: Build Docker Images**

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

# Build backend
docker build -t todo-backend:latest backend
```

**Step 4: Deploy to Kubernetes**

```bash
# Deploy with Helm
helm install todo-app kubernetes/helm/todo-app \
  -n todo-phaseiv \
  --create-namespace \
  -f kubernetes/helm/todo-app/values-local.yaml \
  -f kubernetes/helm/todo-app/values-tls.yaml \
  --wait

# Verify deployment
kubectl get pods -n todo-phaseiv
```

**Step 5: Access the App**

```bash
# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Trust the certificate (Chrome/Edge)
# 1. Visit https://todo-app.local/chat
# 2. Click anywhere and type: thisisunsafe

# Or for Firefox:
# Click "Advanced" → "Accept the Risk and Continue"
```

🎉 **App is now running at: https://todo-app.local/chat**

---

## 📚 Documentation

- **[Kubernetes Guide](kubernetes/docs/KUBERNETES_GUIDE.md)** - Complete deployment guide for naive developers
- **[Runbook](kubernetes/docs/RUNBOOK.md)** - Operational procedures and troubleshooting
- **[Architecture Diagram](kubernetes/docs/architecture-diagram.md)** - System architecture overview

---

## 🛠️ Using kubectl-ai (Natural Language Commands)

If you have kubectl-ai installed, you can use natural language:

```bash
# Check pod status
kubectl-ai "show me all pods in todo-phaseiv namespace"

# Check pod logs
kubectl-ai "show logs from frontend pods"

# Restart deployment
kubectl-ai "restart the backend deployment in todo-phaseiv"

# Check resource usage
kubectl-ai "show CPU and memory usage for all pods"

# Debug issues
kubectl-ai "why is my frontend pod not starting"

# Scale deployment
kubectl-ai "scale frontend to 3 replicas"
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx Ingress                         │
│              (https://todo-app.local)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│    Frontend    │    │     Backend     │
│   (Next.js)    │    │    (FastAPI)    │
│   Port: 3000   │    │   Port: 8000    │
│   Replicas: 2  │    │   Replicas: 2   │
└────────┬───────┘    └────────┬────────┘
         │                     │
         └─────────┬───────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
   ┌─────▼──────┐    ┌──────▼─────┐
   │ MCP Server │    │   Redis    │
   │  (Tools)   │    │  (Cache)   │
   │ Port: 8001 │    │ Port: 6379 │
   └────────────┘    └────────────┘
         │
         │
   ┌─────▼──────────┐
   │   PostgreSQL   │
   │  (Neon Cloud)  │
   └────────────────┘
```

---

## 📦 Components

| Component | Purpose | Replicas | Scaling |
|-----------|---------|----------|---------|
| **Frontend** | Next.js UI with ChatKit | 2-5 | HPA (CPU 70%) |
| **Backend** | FastAPI + ChatKit adapter | 2-5 | HPA (CPU 70%, Mem 80%) |
| **MCP Server** | Tool execution engine | 1 | Fixed |
| **Redis** | Session cache (StatefulSet) | 1 | Fixed |
| **Ingress** | HTTPS routing | - | - |

---

## 🔧 Common Operations

### View Application Status

```bash
# All resources
kubectl get all -n todo-phaseiv

# With kubectl-ai
kubectl-ai "give me a summary of the todo-app deployment"
```

### Check Logs

```bash
# Frontend logs
kubectl logs -n todo-phaseiv -l app=frontend --tail=100

# Backend logs
kubectl logs -n todo-phaseiv -l app=backend --tail=100

# With kubectl-ai
kubectl-ai "show me the last 50 lines of backend logs"
```

### Restart Services

```bash
# Restart frontend
kubectl rollout restart deployment/frontend -n todo-phaseiv

# Restart all
kubectl rollout restart deployment -n todo-phaseiv

# With kubectl-ai
kubectl-ai "restart all deployments in todo-phaseiv"
```

### Update Configuration

```bash
# Edit secrets
kubectl edit secret todo-app-secrets -n todo-phaseiv

# Update Helm release
helm upgrade todo-app kubernetes/helm/todo-app \
  -n todo-phaseiv \
  -f kubernetes/helm/todo-app/values-local.yaml \
  -f kubernetes/helm/todo-app/values-tls.yaml

# With kubectl-ai
kubectl-ai "update the configmap for todo-app"
```

---

## 🐛 Troubleshooting

### Pods not starting?

```bash
# Check pod status
kubectl get pods -n todo-phaseiv

# Describe pod for details
kubectl describe pod <pod-name> -n todo-phaseiv

# With kubectl-ai
kubectl-ai "why isn't my frontend pod running"
```

### ChatKit not loading?

1. **Check HTTPS**: Must access via `https://todo-app.local` (not `http://`)
2. **Trust Certificate**: Type `thisisunsafe` in Chrome or accept in Firefox
3. **Check Backend Logs**:
   ```bash
   kubectl logs -n todo-phaseiv -l app=backend | grep -i chatkit
   ```
4. **Verify Secrets**:
   ```bash
   kubectl get secret todo-app-secrets -n todo-phaseiv -o yaml
   ```

### 500 Internal Server Error?

```bash
# Check backend logs for errors
kubectl logs -n todo-phaseiv -l app=backend --tail=100

# Check database connectivity
kubectl exec -n todo-phaseiv deploy/backend -- env | grep DATABASE_URL

# With kubectl-ai
kubectl-ai "show me errors in backend pods"
```

### MCP Server issues?

```bash
# Check MCP server logs
kubectl logs -n todo-phaseiv -l app=mcp-server --tail=50

# Check connectivity from backend
kubectl exec -n todo-phaseiv deploy/backend -- \
  curl -s http://mcp-service:8001/mcp

# With kubectl-ai
kubectl-ai "check if mcp-server is responding"
```

---

## 📊 Monitoring

### Resource Usage

```bash
# CPU/Memory by pod
kubectl top pods -n todo-phaseiv

# Node resources
kubectl top nodes

# With kubectl-ai
kubectl-ai "show resource usage for todo-app pods"
```

### HPA Status

```bash
# Check autoscaler status
kubectl get hpa -n todo-phaseiv

# Detailed HPA info
kubectl describe hpa frontend-hpa -n todo-phaseiv

# With kubectl-ai
kubectl-ai "is the frontend autoscaling working"
```

---

## 🔄 CI/CD Integration

```yaml
# GitHub Actions example
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Images
        run: |
          docker build -t todo-frontend:${{ github.sha }} frontend
          docker build -t todo-backend:${{ github.sha }} backend

      - name: Deploy with Helm
        run: |
          helm upgrade todo-app kubernetes/helm/todo-app \
            -n todo-phaseiv \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.tag=${{ github.sha }} \
            --wait
```

---

## 🔐 Security Notes

1. **Secrets Management**: Never commit `values-local.yaml` to git
2. **TLS Certificates**: Self-signed for dev, use Let's Encrypt for production
3. **Network Policies**: Implement network segmentation in production
4. **RBAC**: Use service accounts with minimal permissions
5. **Image Scanning**: Scan Docker images for vulnerabilities

---

## 📈 Scaling Guidelines

### Manual Scaling

```bash
# Scale frontend to 3 replicas
kubectl scale deployment/frontend --replicas=3 -n todo-phaseiv

# With kubectl-ai
kubectl-ai "scale frontend to 3 replicas"
```

### Auto-scaling Configuration

Edit HPA limits in `values.yaml`:

```yaml
frontend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10  # Increase for production
    targetCPUUtilizationPercentage: 70
```

---

## 🚦 Health Checks

All services have liveness and readiness probes:

```bash
# Check probe status
kubectl get pods -n todo-phaseiv -o wide

# View probe configuration
kubectl describe pod <pod-name> -n todo-phaseiv | grep -A 10 Liveness

# With kubectl-ai
kubectl-ai "show health check status for all pods"
```

---

## 📝 Environment Variables

**Frontend:**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Auth service URL
- `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`: ChatKit domain key

**Backend:**
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `BETTER_AUTH_SECRET`: JWT signing secret
- `MCP_SERVER_URL`: MCP server endpoint
- `REDIS_HOST`: Redis hostname
- `CORS_ORIGINS`: Allowed CORS origins

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with Minikube
5. Submit a pull request

---

## 📜 License

MIT License - see LICENSE file for details

---

## 🆘 Support

- **Documentation**: See `kubernetes/docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 🎓 Learn More

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [OpenAI ChatKit](https://platform.openai.com/docs/chatkit)
- [Better Auth](https://better-auth.com)
- [Next.js](https://nextjs.org/docs)
- [FastAPI](https://fastapi.tiangolo.com)

---

**Built with ❤️ using Kubernetes, Next.js, FastAPI, and OpenAI ChatKit**
