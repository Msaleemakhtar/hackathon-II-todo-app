# Ashburn Deployment - Quick Start Guide

**Region:** us-ashburn-1
**Account:** New OCI Free Tier
**Date:** 2026-02-01

---

## ⚡ ONE-COMMAND DEPLOY

```bash
cd /home/salim/Desktop/hackathon-II-todo-app
./scripts/deploy-ashburn.sh
```

**That's it!** The script handles everything automatically.

---

## 📝 What the Script Does

1. **Gathers OCI Info** - Gets tenancy, compartment IDs
2. **Creates VCN** - If not exists (10.0.0.0/16)
3. **Creates OKE Cluster** - Or uses existing
4. **Configures kubectl** - Connects to cluster
5. **Verifies Nodes** - Ensures workers are ready
6. **Installs Dapr** - Runtime for event-driven architecture
7. **Creates Namespace** - `todo-phasev`
8. **Creates Storage Class** - OCI Block Volumes
9. **Deploys Dapr Components** - Redis Pub/Sub, PostgreSQL State Store
10. **Deploys Application** - Via Helm (frontend, backend, services)
11. **Installs NGINX Ingress** - With Load Balancer
12. **Gets External IP** - For DNS configuration

---

## ⏱️ Timeline

- **Total Time:** ~15-20 minutes
- **OKE Cluster Creation:** 7-10 minutes (if new)
- **Node Provisioning:** 3-5 minutes
- **Application Deployment:** 2-3 minutes

---

## ✅ Prerequisites

### Required:
- [x] OCI CLI configured (`~/.oci/config` exists)
- [x] OCI account in us-ashburn-1 region
- [x] kubectl installed
- [x] Helm installed
- [x] Dapr CLI installed

### Check Prerequisites:
```bash
# Verify OCI CLI
oci iam region list --query 'data[].name' --output table

# Verify kubectl
kubectl version --client

# Verify Helm
helm version

# Verify Dapr CLI
dapr version
```

### Install Missing Tools:
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

---

## 🔐 Configure Secrets (BEFORE DEPLOY)

Edit: `phaseV/kubernetes/helm/todo-app/values-local.yaml`

```yaml
secrets:
  databaseUrl: "<BASE64_ENCODED_POSTGRESQL_URL>"
  openaiApiKey: "<BASE64_ENCODED_OPENAI_KEY>"
  betterAuthSecret: "<BASE64_ENCODED_AUTH_SECRET>"
```

### Encode Secrets:
```bash
# Database URL (Neon PostgreSQL)
echo -n "postgresql://user:password@host.neon.tech/dbname?sslmode=require" | base64

# OpenAI API Key
echo -n "sk-proj-xxxxxxxxxxxxxxxxxxxx" | base64

# Better Auth Secret (min 32 chars)
echo -n "your-super-secret-32-char-minimum-string" | base64
```

**SMTP Credentials:** Already configured in `values-minimal.yaml` ✅

---

## 🚀 Run Deployment

```bash
cd /home/salim/Desktop/hackathon-II-todo-app

# Make executable (if not already)
chmod +x scripts/deploy-ashburn.sh

# Run deployment
./scripts/deploy-ashburn.sh
```

### Follow Prompts:
1. **Cluster Creation:** Choose automatic or manual
2. **Secrets Check:** Confirm secrets are configured
3. **Wait:** Script runs automatically

---

## 📊 Monitor Progress

### During Deployment:
```bash
# Watch pods (in another terminal)
watch kubectl get pods -n todo-phasev

# Watch nodes
watch kubectl get nodes
```

### After Deployment:
```bash
# Check all pods
kubectl get pods -n todo-phasev

# Check Dapr components
kubectl get components -n todo-phasev

# Check services
kubectl get svc -n todo-phasev

# Check ingress
kubectl get ingress -n todo-phasev
```

---

## 🌐 Access Application

### Get Load Balancer IP:
```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Or check environment file
source ~/.oke-ashburn-env
echo $EXTERNAL_IP
```

### Configure DNS:
```bash
# Option 1: Add to /etc/hosts (local testing)
echo "$EXTERNAL_IP todo-app.local" | sudo tee -a /etc/hosts

# Option 2: Configure real DNS (production)
# Create A record: todo-app.yourdomain.com → $EXTERNAL_IP
```

### Test Application:
```bash
# Health check
curl -k https://todo-app.local/api/health

# Expected: {"status":"healthy", ...}
```

### Access in Browser:
```
https://todo-app.local
```

---

## 🔍 Troubleshooting

### Pods Not Starting:
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-phasev

# Check logs
kubectl logs <pod-name> -n todo-phasev

# Check Dapr sidecar
kubectl logs <pod-name> -c daprd -n todo-phasev
```

### No Nodes:
```bash
# Check node pools
source ~/.oke-ashburn-env
oci ce node-pool list --cluster-id "$CLUSTER_ID" --compartment-id "$COMPARTMENT_ID"

# Create node pool manually (if needed)
# See: phaseV/QUICK_DEPLOY.md
```

### Dapr Issues:
```bash
# Check Dapr system
kubectl get pods -n dapr-system

# Reinitialize Dapr
dapr uninstall --kubernetes
dapr init --kubernetes --wait
```

### Secrets Not Working:
```bash
# Check secrets exist
kubectl get secrets -n todo-phasev

# Decode secret (to verify)
kubectl get secret todo-app-secrets -n todo-phasev -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Update secrets
cd phaseV/kubernetes/helm/todo-app
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

---

## 📈 Scale Application

### Manual Scaling:
```bash
# Scale backend
kubectl scale deployment backend -n todo-phasev --replicas=2

# Scale frontend
kubectl scale deployment frontend -n todo-phasev --replicas=2
```

### Update Resources:
Edit `values-minimal.yaml` and upgrade:
```bash
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

---

## 🧹 Cleanup (If Needed)

### Remove Application:
```bash
helm uninstall todo-app -n todo-phasev
kubectl delete namespace todo-phasev
```

### Remove Ingress:
```bash
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete namespace ingress-nginx
```

### Delete Cluster:
```bash
source ~/.oke-ashburn-env
oci ce cluster delete --cluster-id "$CLUSTER_ID" --force
```

### Delete VCN:
```bash
oci network vcn delete --vcn-id "$VCN_ID" --force
```

---

## 📚 Additional Resources

- **Full Guide:** `phaseV/DEPLOYMENT_GUIDE_OCI_MINIMAL.md`
- **Quick Commands:** `phaseV/QUICK_DEPLOY.md`
- **Architecture:** `phaseV/README.md`
- **Helm Values:** `phaseV/kubernetes/helm/todo-app/values-minimal.yaml`

---

## ✅ Success Checklist

After deployment completes:

- [ ] All pods are Running (`kubectl get pods -n todo-phasev`)
- [ ] Dapr components are loaded (`kubectl get components -n todo-phasev`)
- [ ] Health endpoint responds (`curl -k https://todo-app.local/api/health`)
- [ ] Frontend loads in browser (`https://todo-app.local`)
- [ ] Can create tasks via UI
- [ ] Email reminders work
- [ ] AI chat responds

---

## 🎉 You're Done!

Application is now running on Oracle Cloud (us-ashburn-1) Free Tier!

**Next Steps:**
1. Configure production domain
2. Set up monitoring (Prometheus + Grafana)
3. Configure automated backups
4. Set up CI/CD pipeline

Enjoy your deployed application! 🚀
