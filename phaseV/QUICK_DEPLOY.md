# Phase V - Quick Deployment Commands (OCI Free Tier)

> **Copy-paste commands for rapid deployment**

## Prerequisites Check
```bash
# Verify tools installed
kubectl version --client
helm version
dapr version

# Configure kubectl for OKE
oci ce cluster create-kubeconfig \
  --cluster-id <your-cluster-ocid> \
  --file ~/.kube/config \
  --region <your-region>

# Test connection
kubectl get nodes
```

---

## 1. Create Namespace
```bash
kubectl create namespace todo-phasev
kubectl config set-context --current --namespace=todo-phasev
```

---

## 2. Install Dapr
```bash
# Install Dapr CLI (if not installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify
dapr status -k
```

---

## 3. Create Storage Class (OCI)
```bash
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: oci-bv
provisioner: oracle.com/oci
parameters:
  type: paravirtualized
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
```

---

## 4. Configure Secrets
```bash
cd phaseV/kubernetes/helm/todo-app

# Copy and edit secrets
cp values.yaml values-local.yaml
nano values-local.yaml  # Edit with your credentials

# Required secrets (base64-encoded):
# - databaseUrl: PostgreSQL connection string
# - openaiApiKey: OpenAI API key
# - betterAuthSecret: Auth secret
# - Email credentials (if using different SMTP)
```

---

## 5. Deploy Dapr Components
```bash
cd ../../dapr-components

# Apply all components
kubectl apply -f dapr-config.yaml
kubectl apply -f pubsub-redis.yaml
kubectl apply -f statestore-postgres.yaml
kubectl apply -f secrets-kubernetes.yaml

# Verify
kubectl get components -n todo-phasev
```

---

## 6. Deploy Application
```bash
cd ../helm/todo-app

# Deploy with minimal resources
helm upgrade --install todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev \
  --create-namespace

# Watch deployment
kubectl get pods -n todo-phasev -w
```

---

## 7. Install NGINX Ingress
```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install with OCI Load Balancer
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Get external IP (wait for EXTERNAL-IP to appear)
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

---

## 8. Configure DNS
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# For local testing, add to /etc/hosts:
echo "$EXTERNAL_IP todo-app.local" | sudo tee -a /etc/hosts

# Or configure DNS A record:
# todo-app.local → $EXTERNAL_IP
```

---

## 9. Verification
```bash
# Check all pods running
kubectl get pods -n todo-phasev

# Check Dapr components
kubectl get components -n todo-phasev

# Test health endpoint
curl -k https://todo-app.local/api/health

# Expected: {"status": "healthy", ...}
```

---

## 10. Monitor Logs
```bash
# Backend logs
kubectl logs -l app=backend -n todo-phasev --tail=100 -f

# Notification service logs
kubectl logs -l app=notification-service -n todo-phasev --tail=50 -f

# Email delivery logs
kubectl logs -l app=email-delivery -n todo-phasev --tail=50 -f

# Redis logs
kubectl logs redis-0 -n todo-phasev --tail=50 -f
```

---

## Common Operations

### Scale Deployment
```bash
# Scale backend to 2 replicas
kubectl scale deployment backend -n todo-phasev --replicas=2

# Or edit values-minimal.yaml and upgrade
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

### Restart Deployment
```bash
kubectl rollout restart deployment/backend -n todo-phasev
kubectl rollout restart deployment/frontend -n todo-phasev
```

### Update Image
```bash
# Rebuild and push image
docker build -t <region>.ocir.io/<tenancy>/todo-app-backend:latest .
docker push <region>.ocir.io/<tenancy>/todo-app-backend:latest

# Update values-minimal.yaml with new tag, then:
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

### View Secrets
```bash
# Get secret (base64-encoded)
kubectl get secret todo-app-secrets -n todo-phasev -o yaml

# Decode secret
kubectl get secret todo-app-secrets -n todo-phasev -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Cleanup
```bash
# Delete application
helm uninstall todo-app -n todo-phasev

# Delete namespace
kubectl delete namespace todo-phasev

# Delete ingress
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete namespace ingress-nginx

# Uninstall Dapr
dapr uninstall --kubernetes
```

---

## Troubleshooting Commands

### Pod Not Starting
```bash
# Describe pod
kubectl describe pod <pod-name> -n todo-phasev

# Check events
kubectl get events -n todo-phasev --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n todo-phasev
kubectl logs <pod-name> -c daprd -n todo-phasev  # Dapr sidecar
```

### Redis Issues
```bash
# Connect to Redis
kubectl exec -it redis-0 -n todo-phasev -- redis-cli

# Inside Redis CLI:
127.0.0.1:6379> PING
127.0.0.1:6379> INFO
127.0.0.1:6379> KEYS *
127.0.0.1:6379> MONITOR  # Watch real-time commands
```

### Dapr Issues
```bash
# Check Dapr system pods
kubectl get pods -n dapr-system

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system

# Check component status
kubectl describe component pubsub -n todo-phasev
```

### Network Issues
```bash
# Test internal DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup redis-service.todo-phasev.svc.cluster.local

# Test Redis connectivity
kubectl run -it --rm debug --image=redis:7-alpine --restart=Never -- redis-cli -h redis-service.todo-phasev.svc.cluster.local PING

# Test backend health
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend.todo-phasev.svc.cluster.local:8000/health
```

---

## Performance Tuning

### Check Resource Usage
```bash
# Install metrics-server (if not installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View resource usage
kubectl top pods -n todo-phasev
kubectl top nodes
```

### Adjust Resources
Edit `values-minimal.yaml`:
```yaml
backend:
  resources:
    requests:
      cpu: "500m"      # Increase if CPU throttled
      memory: "512Mi"  # Increase if OOMKilled
```

Then upgrade:
```bash
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

---

## Quick Links

- **Full Deployment Guide**: [DEPLOYMENT_GUIDE_OCI_MINIMAL.md](./DEPLOYMENT_GUIDE_OCI_MINIMAL.md)
- **Migration Summary**: [MIGRATION_SUMMARY.md](./MIGRATION_SUMMARY.md)
- **Phase V README**: [README.md](./README.md)
- **Helm Values**: [kubernetes/helm/todo-app/values-minimal.yaml](./kubernetes/helm/todo-app/values-minimal.yaml)
- **Dapr Components**: [kubernetes/dapr-components/](./kubernetes/dapr-components/)

---

## Support

For issues:
1. Check logs: `kubectl logs -l app=<component> -n todo-phasev`
2. Check events: `kubectl get events -n todo-phasev`
3. Review documentation above
4. Check Dapr docs: https://docs.dapr.io
5. Check OCI docs: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm

Good luck! 🚀
