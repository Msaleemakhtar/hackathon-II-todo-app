# Phoenix Migration Checklist

**Date**: 2026-01-23
**Target Region**: us-phoenix-1
**Estimated Time**: 20-30 minutes total

---

## Pre-Migration

- [ ] Confirm OCI CLI is installed: `oci --version`
- [ ] Verify OCI authentication: `oci iam region list`
- [ ] Have OCI Auth Token ready for OCIR (or create new one)
- [ ] Backup current environment: Already done → `~/.oke-env.dubai.backup`

---

## Migration Execution

### Step 1: Run Migration Script (20 minutes)

```bash
cd /home/salim/Desktop/hackathon-II-todo-app
bash scripts/migrate-to-phoenix.sh
```

**What it does**:
- [x] Creates VCN in us-phoenix-1
- [x] Creates subnets (LB, Node, Service)
- [x] Configures security rules
- [x] Creates OKE cluster
- [x] Creates ARM node pool (2 nodes)
- [x] Configures kubectl
- [x] Updates ~/.oke-env

**Expected duration**: ~15-20 minutes

**Success criteria**:
```
✅ MIGRATION COMPLETE!
Cluster ID: ocid1.cluster.oc1.phx...
Nodes: 2 × ARM A1.Flex
```

---

### Step 2: Verify Cluster (2 minutes)

```bash
source ~/.oke-env
kubectl get nodes -o wide
```

**Expected output**:
```
NAME     STATUS   ROLES   AGE   VERSION   INTERNAL-IP   EXTERNAL-IP
node-1   Ready    node    5m    v1.28.2   10.0.2.X      XXX.XXX.XXX.XXX
node-2   Ready    node    5m    v1.28.2   10.0.2.Y      YYY.YYY.YYY.YYY
```

- [ ] Both nodes show STATUS = Ready
- [ ] Both nodes are ARM64 architecture

---

### Step 3: Configure Storage (1 minute)

```bash
kubectl apply -f phaseV/kubernetes/storage-class.yaml
kubectl get storageclass
```

- [ ] Storage class `oci-bv` shows as (default)

---

### Step 4: Install Dapr (3 minutes)

```bash
dapr init --kubernetes --wait --namespace dapr-system
kubectl get pods -n dapr-system
```

**Expected**: 4 Dapr pods running (operator, sidecar-injector, sentry, placement)

- [ ] All Dapr pods are Running

---

### Step 5: Build ARM64 Images (10-15 minutes)

```bash
# Set up OCIR
export TENANCY_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
export OCIR_REGION="phx"
export OCIR_REGISTRY="${OCIR_REGION}.ocir.io"
export IMAGE_PREFIX="${OCIR_REGISTRY}/${TENANCY_NAMESPACE}/todo-phasev"

# Login to OCIR
docker login ${OCIR_REGISTRY}
# Username: ${TENANCY_NAMESPACE}/<your-oci-username>
# Password: <your-auth-token>

# Build backend
cd phaseV/backend
docker buildx build --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/backend:latest \
  -t ${IMAGE_PREFIX}/backend:v1.0.0 \
  --push .

# Build frontend
cd ../frontend
docker buildx build --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/frontend:latest \
  -t ${IMAGE_PREFIX}/frontend:v1.0.0 \
  --push .
```

- [ ] Backend image pushed successfully
- [ ] Frontend image pushed successfully
- [ ] Images are ARM64 architecture: `docker manifest inspect ${IMAGE_PREFIX}/backend:latest | grep arm64`

---

### Step 6: Create Namespace and Secrets (2 minutes)

```bash
# Create namespace
kubectl create namespace todo-phasev

# Create OCIR pull secret
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCIR_REGISTRY} \
  --docker-username="${TENANCY_NAMESPACE}/<your-oci-username>" \
  --docker-password="<your-auth-token>" \
  --docker-email="<your-email>" \
  --namespace=todo-phasev

# Create app secrets
kubectl create secret generic app-secrets \
  --from-env-file=phaseV/kubernetes/secrets/.env.production \
  --namespace=todo-phasev
```

- [ ] Namespace created
- [ ] OCIR secret created
- [ ] App secrets created

---

### Step 7: Deploy Application (5 minutes)

```bash
# Deploy with Helm (ask me to prepare values-phoenix.yaml first)
helm install todo-phasev ./phaseV/kubernetes/helm/todo-app \
  --namespace todo-phasev \
  --values phaseV/kubernetes/helm/todo-app/values-phoenix.yaml

# Watch deployment
kubectl get pods -n todo-phasev -w
```

- [ ] All pods are Running
- [ ] No CrashLoopBackOff errors

---

### Step 8: Set Up Ingress (3 minutes)

```bash
# Install Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/baremetal/deploy.yaml

# Get access URL
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
echo "App URL: https://${NODE_IP}.nip.io:30443"
```

- [ ] Nginx Ingress installed
- [ ] Application accessible via NodePort

---

## Post-Migration Verification

### Functional Tests

- [ ] Application loads in browser
- [ ] Can create a task
- [ ] Can view tasks
- [ ] Can update a task
- [ ] Can delete a task
- [ ] Real-time updates work (WebSocket)

### Resource Verification

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n todo-phasev

# Check Dapr sidecars
kubectl get pods -n todo-phasev -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

- [ ] Nodes have available CPU/memory
- [ ] Pods have Dapr sidecars
- [ ] No pods in pending state

---

## Rollback Plan (If Needed)

If migration fails, you can quickly rollback to Dubai:

```bash
# Restore Dubai environment
cp ~/.oke-env.dubai.backup ~/.oke-env
source ~/.oke-env

# Reconfigure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id "$CLUSTER_ID" \
  --file ~/.kube/config \
  --region me-dubai-1

kubectl get nodes
```

**Note**: Dubai cluster has no nodes, so you'd still be blocked.

---

## Success Criteria Summary

| Criteria | Target | Status |
|----------|--------|--------|
| Cluster Status | ACTIVE | [ ] |
| Node Count | 2 | [ ] |
| Node Status | Ready | [ ] |
| Node Architecture | ARM64 | [ ] |
| Total CPU | 4 OCPU | [ ] |
| Total RAM | 24 GB | [ ] |
| Dapr Installed | Yes | [ ] |
| Images Built | ARM64 | [ ] |
| App Deployed | Running | [ ] |
| App Accessible | Yes | [ ] |
| Monthly Cost | $0 | [ ] |

---

## Troubleshooting

### If node pool creation fails:
```bash
# Try single node first
# Edit migrate-to-phoenix.sh line 143: --size 1
```

### If kubectl doesn't work:
```bash
source ~/.oke-env
export KUBECONFIG=~/.kube/config
kubectl config current-context
```

### If images fail to push:
```bash
# Verify OCIR login
docker login ${OCIR_REGISTRY}

# Check image size
docker images | grep todo-phasev
```

### If pods are pending:
```bash
kubectl describe pod <pod-name> -n todo-phasev
# Look for resource constraints or image pull errors
```

---

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| Migration script | 20 min | 20 min |
| Verify cluster | 2 min | 22 min |
| Storage setup | 1 min | 23 min |
| Dapr install | 3 min | 26 min |
| Build images | 15 min | 41 min |
| Create secrets | 2 min | 43 min |
| Deploy app | 5 min | 48 min |
| Setup ingress | 3 min | 51 min |
| Testing | 5 min | 56 min |
| **Total** | **~1 hour** | ✅ |

---

## Final Validation

Before considering migration complete:

1. [ ] Application is accessible via public URL
2. [ ] All CRUD operations work
3. [ ] Real-time features work
4. [ ] No error logs in pods: `kubectl logs -n todo-phasev <pod-name>`
5. [ ] Dapr components are healthy: `kubectl get components -n todo-phasev`
6. [ ] Database connectivity works (Neon PostgreSQL)
7. [ ] Environment documented in ~/.oke-env

---

## What's Next

After successful migration:

1. Update documentation with Phoenix URLs
2. Test latency from different regions
3. Monitor resource usage
4. Consider cleanup of Dubai resources (optional)
5. Set up monitoring/alerting (optional for hackathon)

---

**Ready?** Start with:

```bash
cd /home/salim/Desktop/hackathon-II-todo-app
bash scripts/migrate-to-phoenix.sh
```

Expected completion: **20 minutes** ⏱️
Expected cost: **$0/month** 💰
Expected success rate: **70-90%** ✅
