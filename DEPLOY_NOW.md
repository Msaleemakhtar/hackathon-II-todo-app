# 🚀 Deploy Phase V to Oracle Cloud (Ashburn)

**Ready to deploy in ONE command!**

---

## ✅ Status

- ✅ **OCI CLI configured** for us-ashburn-1
- ✅ **Old Dubai files cleaned up**
- ✅ **Fresh deployment scripts ready**
- ✅ **Application migrated to Redis Pub/Sub**

---

## 🎯 ONE-COMMAND DEPLOY

```bash
./scripts/deploy-ashburn.sh
```

**That's it!** Script handles everything automatically in ~15-20 minutes.

---

## 📝 Before You Deploy

### 1. Configure Secrets (5 minutes)

Edit: `phaseV/kubernetes/helm/todo-app/values-local.yaml`

Create the file if it doesn't exist:
```bash
cp phaseV/kubernetes/helm/todo-app/values.yaml \
   phaseV/kubernetes/helm/todo-app/values-local.yaml
```

Then edit and add base64-encoded secrets:
```yaml
secrets:
  # Neon PostgreSQL URL
  databaseUrl: "cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bob3N0L2Ri..."

  # OpenAI API Key
  openaiApiKey: "c2stcHJvai14eHh4eHh4eHh4eHh4eHh4eA=="

  # Auth Secret (min 32 chars)
  betterAuthSecret: "eW91ci1zdXBlci1zZWNyZXQtMzItY2hhci1taW5pbXVt..."
```

**Encode your secrets:**
```bash
# Database URL
echo -n "postgresql://user:password@host.neon.tech/dbname?sslmode=require" | base64

# OpenAI Key
echo -n "sk-proj-your-key-here" | base64

# Auth Secret (generate random 32+ chars)
echo -n "$(openssl rand -base64 32)" | base64
```

**SMTP credentials:** Already configured in `values-minimal.yaml` ✅

---

## 🚀 Deploy Now

```bash
cd /home/salim/Desktop/hackathon-II-todo-app

# Run automated deployment
./scripts/deploy-ashburn.sh
```

### What Happens:
1. Creates OCI infrastructure (VCN, subnets)
2. Creates OKE cluster (or uses existing)
3. Configures kubectl
4. Installs Dapr runtime
5. Deploys application with Helm
6. Sets up NGINX Ingress
7. Provides Load Balancer IP

**Time:** ~15-20 minutes total

---

## 📊 Monitor Deployment

Open another terminal and watch progress:

```bash
# Watch pods starting up
watch kubectl get pods -n todo-phasev

# Watch nodes
watch kubectl get nodes
```

---

## 🌐 Access Application

After deployment completes:

### 1. Get Load Balancer IP
```bash
source ~/.oke-ashburn-env
echo $EXTERNAL_IP
```

### 2. Configure DNS
```bash
# Local testing (add to /etc/hosts)
echo "$EXTERNAL_IP todo-app.local" | sudo tee -a /etc/hosts

# Or use nip.io (no DNS needed)
# Access: https://<EXTERNAL_IP>.nip.io
```

### 3. Access Application
```
https://todo-app.local
```

---

## 🔍 Verify Deployment

```bash
# Check all pods running
kubectl get pods -n todo-phasev

# Test health endpoint
curl -k https://todo-app.local/api/health

# Check Dapr components
kubectl get components -n todo-phasev
```

---

## 📚 Documentation

- **This file:** Quick reference
- **Deployment script:** `scripts/deploy-ashburn.sh`
- **Quick start:** `docs/ASHBURN_QUICK_START.md`
- **Deployment status:** `docs/DEPLOYMENT_STATUS.md`
- **Full guide:** `phaseV/DEPLOYMENT_GUIDE_OCI_MINIMAL.md`
- **Quick commands:** `phaseV/QUICK_DEPLOY.md`

---

## 🆘 Troubleshooting

### Script Fails:
```bash
# Check OCI CLI
oci iam region list

# Check logs
cat ~/.oke-ashburn-env

# Manual deployment
See: docs/ASHBURN_QUICK_START.md
```

### Pods Not Starting:
```bash
# Check pod details
kubectl describe pod <pod-name> -n todo-phasev

# Check logs
kubectl logs <pod-name> -n todo-phasev
```

### Need Help:
- See `docs/ASHBURN_QUICK_START.md` for detailed troubleshooting
- Check `phaseV/QUICK_DEPLOY.md` for manual steps

---

## ✅ Success Checklist

After deployment:

- [ ] All pods Running (`kubectl get pods -n todo-phasev`)
- [ ] Health check works (`curl -k https://todo-app.local/api/health`)
- [ ] Frontend loads in browser
- [ ] Can create tasks
- [ ] AI chat works
- [ ] Email reminders sent

---

## 🎉 Ready?

**Configure secrets** → **Run script** → **Access app**

```bash
./scripts/deploy-ashburn.sh
```

Good luck! 🚀
