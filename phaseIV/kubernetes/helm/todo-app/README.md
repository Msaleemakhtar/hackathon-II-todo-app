# Todo App Helm Chart

Helm chart for deploying the Phase IV Todo Chatbot application to Kubernetes.

## Description

This Helm chart deploys a complete Todo Chatbot application with:

- **Frontend**: Next.js web application with auto-scaling (2-5 replicas)
- **Backend**: FastAPI REST API with auto-scaling (2-5 replicas)
- **MCP Server**: AI agent tools server (1 replica)
- **Redis**: Cache and session storage with persistent volume
- **Nginx Ingress**: HTTP routing for external access
- **Horizontal Pod Autoscaling**: Automatic scaling based on CPU/memory metrics
- **Health Monitoring**: Liveness and readiness probes for all services

## Prerequisites

- Kubernetes v1.28+
- Helm v3.13+
- Minikube v1.32+ (for local development)
- Docker Desktop (container runtime)
- 4 CPU cores and 8GB RAM minimum

## Installation

### Quick Start

```bash
# 1. Install the chart with default values
helm install todo-app . --namespace todo-phaseiv --create-namespace

# 2. Wait for deployment
helm status todo-app -n todo-phaseiv
```

### Production Installation

```bash
# 1. Create values-local.yaml with your secrets
cp ../../values-local.yaml.example values-local.yaml

# 2. Edit values-local.yaml with base64-encoded secrets
nano values-local.yaml

# 3. Install with custom values
helm install todo-app . \
  --namespace todo-phaseiv \
  --create-namespace \
  -f values-local.yaml \
  --wait \
  --timeout 10m

# 4. Verify installation
helm test todo-app -n todo-phaseiv
```

## Configuration

### Required Secrets

The following secrets **must** be configured (base64-encoded):

| Parameter | Description | Example Encoding |
|-----------|-------------|------------------|
| `secrets.databaseUrl` | Neon PostgreSQL connection string | `echo -n 'postgresql://user:pass@host/db' \| base64` |
| `secrets.openaiApiKey` | OpenAI API key | `echo -n 'sk-...' \| base64` |
| `secrets.betterAuthSecret` | Auth shared secret | `openssl rand -base64 32` |
| `secrets.betterAuthUrl` | Application URL | `echo -n 'http://todo-app.local' \| base64` |

### Configuration Values

#### Global Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `todo-phaseiv` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |

#### Frontend Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Initial replica count | `2` |
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.port` | Frontend service port | `3000` |
| `frontend.resources.requests.cpu` | CPU request | `500m` |
| `frontend.resources.requests.memory` | Memory request | `512Mi` |
| `frontend.resources.limits.cpu` | CPU limit | `1000m` |
| `frontend.resources.limits.memory` | Memory limit | `1024Mi` |
| `frontend.autoscaling.enabled` | Enable HPA | `true` |
| `frontend.autoscaling.minReplicas` | Minimum replicas | `2` |
| `frontend.autoscaling.maxReplicas` | Maximum replicas | `5` |
| `frontend.autoscaling.targetCPUUtilizationPercentage` | CPU threshold | `70` |

#### Backend Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Initial replica count | `2` |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.port` | Backend service port | `8000` |
| `backend.resources.requests.cpu` | CPU request | `500m` |
| `backend.resources.requests.memory` | Memory request | `512Mi` |
| `backend.resources.limits.cpu` | CPU limit | `1000m` |
| `backend.resources.limits.memory` | Memory limit | `1024Mi` |
| `backend.autoscaling.enabled` | Enable HPA | `true` |
| `backend.autoscaling.minReplicas` | Minimum replicas | `2` |
| `backend.autoscaling.maxReplicas` | Maximum replicas | `5` |
| `backend.autoscaling.targetCPUUtilizationPercentage` | CPU threshold | `70` |
| `backend.autoscaling.targetMemoryUtilizationPercentage` | Memory threshold | `80` |

#### MCP Server Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mcpServer.enabled` | Enable MCP server deployment | `true` |
| `mcpServer.replicaCount` | Replica count (fixed) | `1` |
| `mcpServer.image.repository` | MCP server image | `todo-backend` |
| `mcpServer.image.tag` | MCP server image tag | `latest` |
| `mcpServer.service.port` | MCP server port | `8001` |
| `mcpServer.resources.requests.cpu` | CPU request | `250m` |
| `mcpServer.resources.requests.memory` | Memory request | `256Mi` |
| `mcpServer.resources.limits.cpu` | CPU limit | `500m` |
| `mcpServer.resources.limits.memory` | Memory limit | `512Mi` |

#### Redis Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis deployment | `true` |
| `redis.image.repository` | Redis image | `redis` |
| `redis.image.tag` | Redis image tag | `7-alpine` |
| `redis.service.port` | Redis port | `6379` |
| `redis.resources.requests.cpu` | CPU request | `250m` |
| `redis.resources.requests.memory` | Memory request | `128Mi` |
| `redis.resources.limits.cpu` | CPU limit | `500m` |
| `redis.resources.limits.memory` | Memory limit | `256Mi` |
| `redis.persistence.enabled` | Enable persistent volume | `true` |
| `redis.persistence.storageClassName` | Storage class | `standard` |
| `redis.persistence.size` | Volume size | `1Gi` |

#### Ingress Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable Ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.host` | Ingress hostname | `todo-app.local` |

#### ConfigMap Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `configMap.REDIS_HOST` | Redis hostname | `redis-service.todo-phaseiv.svc.cluster.local` |
| `configMap.REDIS_PORT` | Redis port | `6379` |
| `configMap.MCP_SERVER_URL` | MCP server URL | `http://mcp-service.todo-phaseiv.svc.cluster.local:8001` |
| `configMap.NEXT_PUBLIC_API_URL` | Public API URL | `http://todo-app.local/api` |

## Usage Examples

### Install with Custom Values

```bash
# Install with custom replica counts
helm install todo-app . \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=4 \
  -n todo-phaseiv
```

### Override Image Tags

```bash
# Use specific image versions
helm install todo-app . \
  --set frontend.image.tag=v1.2.0 \
  --set backend.image.tag=v1.2.0 \
  -n todo-phaseiv
```

### Disable HPA

```bash
# Disable autoscaling for manual control
helm install todo-app . \
  --set frontend.autoscaling.enabled=false \
  --set backend.autoscaling.enabled=false \
  -n todo-phaseiv
```

### Increase Resource Limits

```bash
# Increase resources for production
helm install todo-app . \
  --set backend.resources.limits.cpu=2000m \
  --set backend.resources.limits.memory=2048Mi \
  -n todo-phaseiv
```

### Use External Redis

```bash
# Disable built-in Redis and use external instance
helm install todo-app . \
  --set redis.enabled=false \
  --set configMap.REDIS_HOST=external-redis.example.com \
  -n todo-phaseiv
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-app . \
  -n todo-phaseiv \
  -f values-local.yaml \
  --wait

# Check upgrade status
helm rollout status deployment frontend -n todo-phaseiv
```

## Uninstalling

```bash
# Uninstall the chart
helm uninstall todo-app -n todo-phaseiv

# Optionally delete namespace
kubectl delete namespace todo-phaseiv
```

## Testing

### Helm Tests

```bash
# Run built-in Helm tests
helm test todo-app -n todo-phaseiv

# Expected output:
# NAME: todo-app
# LAST DEPLOYED: ...
# NAMESPACE: todo-phaseiv
# STATUS: deployed
# TEST SUITE:     test-frontend
# Last Started:   ...
# Last Completed: ...
# Phase:          Succeeded
```

### Manual Validation

```bash
# Check all pods are running
kubectl get pods -n todo-phaseiv

# Check services
kubectl get svc -n todo-phaseiv

# Check HPA status
kubectl get hpa -n todo-phaseiv

# Check Ingress
kubectl get ingress -n todo-phaseiv

# Test frontend endpoint
curl http://todo-app.local/

# Test backend health
curl http://todo-app.local/api/health
```

## Troubleshooting

### Chart Linting

```bash
# Validate chart templates
helm lint .

# Dry run to see generated manifests
helm install todo-app . --dry-run --debug -n todo-phaseiv
```

### Template Debugging

```bash
# Render templates locally
helm template todo-app . -n todo-phaseiv

# Render specific template
helm template todo-app . --show-only templates/backend-deployment.yaml
```

### Common Issues

#### 1. Secrets Not Configured

**Error:**
```
Error: secret "todo-app-secret" not found
```

**Solution:**
Create `values-local.yaml` with base64-encoded secrets:
```yaml
secrets:
  databaseUrl: "cG9zdGdyZXNxbDovL..." # base64 encoded
  openaiApiKey: "c2stLi4u..."        # base64 encoded
  betterAuthSecret: "..."            # base64 encoded
  betterAuthUrl: "aHR0cDovL..."      # base64 encoded
```

#### 2. Image Pull Errors

**Error:**
```
Failed to pull image "todo-frontend:latest": ErrImagePull
```

**Solution:**
Ensure images are built in Minikube's Docker environment:
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest phaseIV/frontend
docker build -t todo-backend:latest phaseIV/backend
```

#### 3. PVC Not Binding

**Error:**
```
PersistentVolumeClaim is not bound: "redis-data-redis-0"
```

**Solution:**
Check StorageClass availability:
```bash
kubectl get storageclass
# Ensure "standard" StorageClass exists

# If not, create one or use different storageClassName in values.yaml
```

## Chart Structure

```
todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── README.md               # This file
├── .helmignore            # Files to exclude from package
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── namespace.yaml      # Namespace resource
    ├── secret.yaml         # Secrets
    ├── configmap.yaml      # ConfigMap
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── frontend-hpa.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── backend-hpa.yaml
    ├── mcp-deployment.yaml
    ├── mcp-service.yaml
    ├── redis-statefulset.yaml
    ├── redis-service.yaml
    ├── ingress.yaml
    └── tests/
        ├── test-frontend.yaml
        ├── test-backend.yaml
        ├── test-mcp.yaml
        └── test-redis.yaml
```

## Version History

| Version | Description | Date |
|---------|-------------|------|
| 0.1.0 | Initial chart release | 2025-12-26 |

## Contributing

For deployment guides and operational procedures, see:

- [KUBERNETES_GUIDE.md](../../docs/KUBERNETES_GUIDE.md) - Comprehensive deployment guide
- [RUNBOOK.md](../../docs/RUNBOOK.md) - Operational procedures and troubleshooting
- [architecture-diagram.md](../../docs/architecture-diagram.md) - System architecture

## License

This Helm chart is part of the Todo App Phase IV project.
