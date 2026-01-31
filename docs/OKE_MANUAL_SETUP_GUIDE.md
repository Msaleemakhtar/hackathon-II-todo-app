# OKE Manual Setup Guide - Free Tier Deployment

## Current Status

✅ **Completed Infrastructure:**
- VCN: `todo-phasev-vcn` (10.0.0.0/16) - ocid1.vcn.oc1.me-dubai-1.amaaaaaapdqqk3iah6ifxyopxa4d46awt2thvzdcjtcyof6prkl2ijpymcla
- LB Subnet: ocid1.subnet.oc1.me-dubai-1.aaaaaaaaeinvjrkt3g4h4xvrsjvqx5sakpgr6uwhsfyleuyci2e2dhn325nq
- Node Subnet: ocid1.subnet.oc1.me-dubai-1.aaaaaaaar6cxaecl3q23z4urysnmjasw5lcfhj7kv3mzf7g7eh2h272afhtq
- Service Subnet: ocid1.subnet.oc1.me-dubai-1.aaaaaaaajweob47w5ffvekanizcovwgbrppj65o4fr623gjuakaqvsoous4a
- Internet Gateway configured
- Security Lists configured for HTTP, HTTPS, NodePorts (30080, 30443)
- Production secrets: `phaseV/kubernetes/secrets/.env.production`

⏳ **Next Step:** Create OKE Cluster manually via OCI Console

---

## Step 1: Create OKE Cluster via OCI Console (5-10 minutes)

### Instructions:

1. **Log in to OCI Console**
   - Go to: https://cloud.oracle.com
   - Sign in with your OCI credentials
   - Region: **me-dubai-1** (Dubai)

2. **Navigate to OKE Service**
   - Click ☰ (hamburger menu)
   - Select **Developer Services** → **Kubernetes Clusters (OKE)**
   - Or direct link: https://cloud.oracle.com/containers/clusters

3. **Start Cluster Creation**
   - Click **Create Cluster** button
   - Choose **Quick Create** (recommended for faster setup)
   - Click **Submit**

4. **Configure Cluster Settings**

   **Basic Information:**
   - **Name:** `todo-phasev-oke`
   - **Compartment:** Select your root compartment
   - **Kubernetes Version:** `v1.28` or latest available
   - **Kubernetes API Endpoint:** Public Endpoint
   - **Kubernetes Worker Nodes:** Public Workers

   **Network Configuration:**
   - **VCN:** Select **todo-phasev-vcn** (already created)
   - **Kubernetes Service LB Subnets:** Select the LB subnet (10.0.1.0/24)
   - **Kubernetes API Endpoint Subnet:** Select the Service subnet (10.0.3.0/24)

   **Node Pool Configuration:**
   - **Name:** `laude
   `
   - **Node Count:** `2`
   - **Shape:** `VM.Standard.A1.Flex` (ARM Ampere - **Always Free Eligible**)
     - If you don't see A1.Flex, click "Change Shape" and filter by "Always Free Eligible"
   - **OCPUs:** `2` per node
   - **Memory:** `12 GB` per node
   - **Boot Volume:** `50 GB`
   - **Node Subnet:** Select the Node subnet (10.0.2.0/24)
   - **Placement:** Distribute across availability domains (automatic)

   **Pod Configuration:**
   - **Pod Communication:** Flannel Overlay (default)

5. **Review and Create**
   - Review all settings
   - Click **Create Cluster**
   - Wait 5-7 minutes for cluster creation to complete

6. **Get Cluster OCID**
   - Once cluster is **ACTIVE**, click on the cluster name
   - Copy the **Cluster OCID** (starts with `ocid1.cluster.oc1...`)
   - **SAVE THIS - YOU'LL NEED IT IN STEP 2**

---

## Step 2: Configure kubectl Access

Once your cluster is **ACTIVE**, run this command to save the cluster ID and configure kubectl:

```bash
# Replace <YOUR_CLUSTER_OCID> with the actual OCID from Step 1
export CLUSTER_ID="<YOUR_CLUSTER_OCID>"
echo "export CLUSTER_ID=$CLUSTER_ID" >> ~/.oke-env

# Run the kubectl configuration script
chmod +x /home/salim/Desktop/hackathon-II-todo-app/scripts/configure-kubectl.sh
bash /home/salim/Desktop/hackathon-II-todo-app/scripts/configure-kubectl.sh
```

**Verify kubectl access:**
```bash
kubectl cluster-info
kubectl get nodes
```

You should see 2 ARM nodes in **Ready** state (may take 2-3 minutes after cluster creation).

---

## Step 3: Configure Storage Class

```bash
# Create OCI Block Volume storage class
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: oci-bv
provisioner: oracle.com/oci
parameters:
  type: paravirtualized
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Retain
EOF

# Set as default
kubectl patch storageclass oci-bv -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Verify
kubectl get storageclass
```

---

## Step 4: Build and Push ARM64 Docker Images

Your OKE cluster uses ARM Ampere A1 nodes, so you need ARM64-compatible images.

### Option A: Build with Docker Buildx (Local)

```bash
# Get OCIR details
export TENANCY_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
export OCIR_REGION="me"  # me-dubai-1 = me
export OCIR_REGISTRY="${OCIR_REGION}.ocir.io"
export IMAGE_PREFIX="${OCIR_REGISTRY}/${TENANCY_NAMESPACE}/todo-phasev"

# Login to OCIR (use your OCI auth token as password)
docker login ${OCIR_REGISTRY} -u ${TENANCY_NAMESPACE}/<your-oci-username>

# Set up buildx for ARM64
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build and push backend (ARM64)
cd /home/salim/Desktop/hackathon-II-todo-app/phaseV/backend
docker buildx build \
  --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/backend:latest \
  -t ${IMAGE_PREFIX}/backend:v1.0.0 \
  --push \
  .

# Build and push frontend (ARM64)
cd ../frontend
docker buildx build \
  --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/frontend:latest \
  -t ${IMAGE_PREFIX}/frontend:v1.0.0 \
  --push \
  .

# Verify ARM64 support
docker manifest inspect ${IMAGE_PREFIX}/backend:latest | grep -A 5 "arm64"
```

### Option B: Build with GitHub Actions (Automated)

I can set up a GitHub Actions workflow to build ARM64 images automatically. Let me know if you prefer this approach.

---

## Step 5: Deploy Application

Once images are built and pushed, continue with application deployment:

```bash
# Install Dapr
dapr init --kubernetes --wait --namespace dapr-system

# Create namespace
kubectl create namespace todo-phasev

# Create OCIR pull secret
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCIR_REGISTRY} \
  --docker-username="${TENANCY_NAMESPACE}/<your-oci-username>" \
  --docker-password="<your-auth-token>" \
  --docker-email="<your-email>" \
  --namespace=todo-phasev

# Create application secrets
kubectl create secret generic app-secrets \
  --from-env-file=/home/salim/Desktop/hackathon-II-todo-app/phaseV/kubernetes/secrets/.env.production \
  --namespace=todo-phasev

# Deploy via Helm (I'll prepare the values file)
```

---

## What's Next

After you complete Steps 1-2:

1. ✅ Cluster will be ready with 2 ARM nodes
2. ✅ kubectl configured for OKE access
3. → Continue with Docker image building (Step 4)
4. → Deploy application with Dapr (Step 5)
5. → Set up Nginx Ingress with NodePort (FREE - no Load Balancer)
6. → Access app via `https://<NODE_IP>.nip.io:30443`

---

## Free Tier Checklist

- ✅ 2 × A1.Flex nodes (2 OCPU, 12GB each) = 4 OCPU, 24GB total (100% free tier)
- ✅ VCN and subnets (free tier)
- ✅ Block Volumes < 200GB (free tier)
- ✅ OCIR 500GB storage (free tier)
- ✅ NodePort ingress (no Load Balancer = $0)
- ✅ 10TB/month egress (free tier)

**Monthly Cost: $0** ✅

---

## Troubleshooting

### Issue: Can't find VM.Standard.A1.Flex shape

**Solution:**
1. In shape selection, click **Change Shape**
2. Filter by **Always Free Eligible**
3. Select **VM.Standard.A1.Flex**
4. If not available in me-dubai-1, try another region (us-ashburn-1, us-phoenix-1, etc.)

### Issue: "Out of capacity for shape VM.Standard.A1.Flex"

**Solution:**
- ARM A1 instances are in high demand
- Try different availability domains
- Try a different region
- Wait and retry in a few hours
- Alternative: Use x86 shapes (E2.1.Micro × 2 is also free tier, but less powerful)

### Issue: Node status "NotReady"

**Solution:**
- Nodes take 2-3 minutes after cluster creation to become Ready
- Check: `kubectl describe node <node-name>`
- Verify: `kubectl get pods -n kube-system`

---

## When You're Ready

After creating the cluster in OCI Console, come back here with the **Cluster OCID** and I'll guide you through the remaining deployment steps!

**Questions? Issues?** Let me know and I'll help troubleshoot!
