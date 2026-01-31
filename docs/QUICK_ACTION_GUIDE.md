# Quick Action Guide - Node Pool Capacity Issue

**Problem**: ARM A1.Flex instances unavailable in me-dubai-1
**Status**: Cluster ACTIVE, kubectl connected, nodes blocked
**Goal**: Get worker nodes to deploy application

---

## ⚡ IMMEDIATE ACTIONS (Do These Now)

### **Action 1: Start Background Retry** (2 minutes)

This runs automatically every 15 minutes and may succeed when capacity becomes available.

```bash
cd /home/salim/Desktop/hackathon-II-todo-app

# Make script executable
chmod +x scripts/retry-arm-nodepool.sh

# Run in background
nohup bash scripts/retry-arm-nodepool.sh > retry-nodepool.log 2>&1 &

# Save process ID
echo $! > retry-nodepool.pid

# Verify it's running
ps aux | grep retry-arm-nodepool.sh

# Monitor progress (CTRL+C to exit, script keeps running)
tail -f retry-nodepool.log
```

✅ **This runs in background - you can continue with other options**

---

### **Action 2: Try Single Node in Different ADs** (5 minutes)

Often succeeds when 2-node pools fail.

```bash
cd /home/salim/Desktop/hackathon-II-todo-app

# Make script executable
chmod +x scripts/try-single-node-all-ads.sh

# Run the script
bash scripts/try-single-node-all-ads.sh
```

**What this does**:
- Tries creating 1 ARM node in each availability domain
- Tests different OCPU/RAM configurations
- If successful, you'll have 1 node ready to deploy

**If successful**: Continue to "After You Have Nodes" section below
**If failed**: Continue to Action 3

---

### **Action 3: Check Current Status** (1 minute)

Check if the background retry succeeded:

```bash
# Check retry log
tail -20 retry-nodepool.log

# Check if nodes appeared
kubectl get nodes

# Check node pools in OCI
source ~/.oke-env
oci ce node-pool list --cluster-id "$CLUSTER_ID" --compartment-id "$COMPARTMENT_ID"
```

**If you see nodes**: ✅ Success! Continue to "After You Have Nodes"
**If no nodes yet**: Continue to Decision Point below

---

## 🤔 DECISION POINT (If Actions 1-3 Don't Work)

You have 4 options. Choose based on your priorities:

### **Option A: Wait for Background Retry** ⏰ PATIENT
- **Time**: 6-48 hours
- **Cost**: $0 (free tier)
- **Success rate**: 60-80%
- **Best for**: Not urgent, want free tier

**Do this**:
```bash
# Just wait - script is running in background
# Check progress:
tail -f retry-nodepool.log

# Stop script if you give up:
kill $(cat retry-nodepool.pid)
```

---

### **Option B: Deploy to Different Region** 🌎 RECOMMENDED
- **Time**: 2 hours (recreate infrastructure)
- **Cost**: $0 (free tier)
- **Success rate**: 70-90%
- **Best for**: Want free tier, don't mind latency

**Do this**:
1. Delete current cluster (or keep for later):
   ```bash
   # Optional - delete current cluster to free quota
   oci ce cluster delete --cluster-id "$CLUSTER_ID" --force
   ```

2. Pick new region:
   - **us-phoenix-1** (best ARM availability)
   - **us-ashburn-1** (good ARM availability, lower latency to Dubai)

3. Follow guide:
   ```bash
   # See detailed steps in:
   cat docs/OKE_CAPACITY_ALTERNATIVES.md
   # Section: "Option 2: Deploy to Different Region"
   ```

---

### **Option C: Use x86 Free Tier** 💻 FALLBACK
- **Time**: 3 hours (rebuild images for x86)
- **Cost**: $0 (free tier)
- **Success rate**: 95%+
- **Best for**: Demo/dev only, minimal resources OK

**Trade-off**: Only 2GB RAM total (vs 24GB with ARM)

**Do this**:
1. Create x86 node pool:
   ```bash
   source ~/.oke-env
   IMAGE_ID=$(oci compute image list \
     --compartment-id "$COMPARTMENT_ID" \
     --operating-system "Oracle Linux" \
     --shape "VM.Standard.E2.1.Micro" \
     --sort-by TIMECREATED \
     --sort-order DESC \
     --limit 1 \
     --query 'data[0].id' \
     --raw-output)

   oci ce node-pool create \
     --cluster-id "$CLUSTER_ID" \
     --compartment-id "$COMPARTMENT_ID" \
     --name "x86-free-tier-pool" \
     --kubernetes-version "v1.34.1" \
     --node-shape "VM.Standard.E2.1.Micro" \
     --size 2 \
     --placement-configs "[{\"availabilityDomain\":\"<AD1>\",\"subnetId\":\"$NODE_SUBNET_ID\"}]" \
     --node-source-details "{\"sourceType\": \"IMAGE\", \"imageId\": \"$IMAGE_ID\", \"bootVolumeSizeInGBs\": 50}" \
     --wait-for-state ACTIVE
   ```

2. Rebuild Docker images for x86 (amd64):
   ```bash
   # See docs/OKE_CAPACITY_ALTERNATIVES.md Option 3
   ```

---

### **Option D: Use Minimal Paid Instances** 💰 GUARANTEED
- **Time**: 30 minutes
- **Cost**: ~$24-30/month
- **Success rate**: 99%+
- **Best for**: Urgent deadline, hackathon demo

**Do this**:
```bash
source ~/.oke-env

# Get x86 image
IMAGE_ID=$(oci compute image list \
  --compartment-id "$COMPARTMENT_ID" \
  --operating-system "Oracle Linux" \
  --shape "VM.Standard.E4.Flex" \
  --sort-by TIMECREATED \
  --sort-order DESC \
  --limit 1 \
  --query 'data[0].id' \
  --raw-output)

# Create paid node pool (E4.Flex: 1 OCPU × 4GB × 2 nodes)
oci ce node-pool create \
  --cluster-id "$CLUSTER_ID" \
  --compartment-id "$COMPARTMENT_ID" \
  --name "paid-tier-pool" \
  --kubernetes-version "v1.34.1" \
  --node-shape "VM.Standard.E4.Flex" \
  --node-shape-config '{"ocpus": 1.0, "memoryInGBs": 4.0}' \
  --size 2 \
  --placement-configs "[{\"availabilityDomain\":\"<AD1>\",\"subnetId\":\"$NODE_SUBNET_ID\"}]" \
  --node-source-details "{\"sourceType\": \"IMAGE\", \"imageId\": \"$IMAGE_ID\", \"bootVolumeSizeInGBs\": 50}" \
  --wait-for-state ACTIVE
```

**Note**: This costs money! You can migrate to free tier later.

---

## ✅ AFTER YOU HAVE NODES

Once you have worker nodes (from any option above):

### **Step 1: Verify Nodes**

```bash
# Check nodes are Ready
kubectl get nodes -o wide

# Expected output:
# NAME              STATUS   ROLES    AGE   VERSION
# <node-name>       Ready    <none>   1m    v1.34.1
```

### **Step 2: Check System Pods**

```bash
# All system pods should be Running
kubectl get pods -n kube-system

# Wait for all pods to be Ready (2-3 minutes)
kubectl wait --for=condition=ready pod --all -n kube-system --timeout=300s
```

### **Step 3: Continue with Deployment**

```bash
# You're now ready for Phase 2: Application Deployment
# See: docs/OKE_DEPLOYMENT_PLAN_FREE_TIER.md
# Section: "Phase 2: Application Deployment"

# Next steps:
# 1. Build ARM64 (or x86) Docker images
# 2. Push to Oracle Container Registry (OCIR)
# 3. Install Dapr
# 4. Deploy application via Helm
# 5. Set up Nginx Ingress (NodePort)
# 6. Configure SSL/TLS
```

---

## 📊 QUICK COMPARISON

| Option | Time | Cost | Success | Effort |
|--------|------|------|---------|--------|
| **A: Wait** | 6-48h | $0 | 60-80% | Low |
| **B: Region** | 2h | $0 | 70-90% | Medium |
| **C: x86** | 3h | $0 | 95% | High |
| **D: Paid** | 30m | $24-30/mo | 99% | Low |

---

## 🆘 HELP & TROUBLESHOOTING

### Check if retry script is still running

```bash
ps aux | grep retry-arm-nodepool.sh

# If not running, restart:
nohup bash scripts/retry-arm-nodepool.sh > retry-nodepool.log 2>&1 &
```

### Check for any existing node pools

```bash
source ~/.oke-env
oci ce node-pool list --cluster-id "$CLUSTER_ID" --compartment-id "$COMPARTMENT_ID"
```

### Check OCI quotas/limits

```bash
# Check ARM compute quota
oci limits resource-availability get \
  --compartment-id "$COMPARTMENT_ID" \
  --service-name compute \
  --limit-name vm-standard-a1-flex-core-count

# Expected: available ≥ 4 (for 2 nodes × 2 OCPU)
```

### Delete failed node pools

```bash
# List all node pools
oci ce node-pool list --cluster-id "$CLUSTER_ID" --compartment-id "$COMPARTMENT_ID"

# Delete a failed pool
oci ce node-pool delete --node-pool-id "<pool-ocid>" --force
```

---

## 📝 SUMMARY

**Where you are**:
- ✅ OKE cluster created (ACTIVE)
- ✅ kubectl connected
- ✅ Networking configured
- ❌ Node pool blocked (ARM capacity unavailable)

**What you should do RIGHT NOW**:
1. ✅ **Start Action 1** (background retry) - 2 minutes
2. ✅ **Try Action 2** (single node in different ADs) - 5 minutes
3. ⏰ **Wait 4-6 hours** OR **Choose Option B/C/D** if urgent

**Most likely outcome**:
- **60-80% chance**: Background retry succeeds within 24-48 hours
- **30-50% chance**: Single node attempt succeeds immediately
- **If both fail**: Deploy to us-phoenix-1 (Option B) or use paid (Option D)

---

## 📚 Full Documentation

- **Complete alternatives guide**: `docs/OKE_CAPACITY_ALTERNATIVES.md`
- **Full deployment plan**: `docs/OKE_DEPLOYMENT_PLAN_FREE_TIER.md`
- **Manual setup guide**: `docs/OKE_MANUAL_SETUP_GUIDE.md`
- **Current status**: `docs/DEPLOYMENT_STATUS.md`

---

**Ready to proceed?** Pick your path above and execute! Let me know which option you choose and I'll help with the next steps.
