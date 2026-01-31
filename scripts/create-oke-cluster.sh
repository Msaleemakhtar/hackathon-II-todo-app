#!/bin/bash
set -e

# Source environment variables
source ~/.oke-env

echo "Creating OKE Enhanced Cluster: $CLUSTER_NAME..."
echo "Region: $REGION"
echo "Compartment: $COMPARTMENT_ID"
echo "VCN: $VCN_ID"
echo "LB Subnet: $LB_SUBNET_ID"
echo "Service Subnet: $SVC_SUBNET_ID"
echo ""

# Create cluster
RESULT=$(oci ce cluster create \
  --compartment-id "$COMPARTMENT_ID" \
  --name "$CLUSTER_NAME" \
  --vcn-id "$VCN_ID" \
  --kubernetes-version "v1.28.2" \
  --service-lb-subnet-ids "[$LB_SUBNET_ID]" \
  --endpoint-subnet-id "$SVC_SUBNET_ID" \
  --cluster-pod-network-options '[{"cniType":"FLANNEL_OVERLAY"}]' 2>&1)

# Extract cluster ID
CLUSTER_ID=$(echo "$RESULT" | grep -o 'ocid1\.cluster\.[^"]*' | head -1)

if [ -n "$CLUSTER_ID" ]; then
    echo "✅ Cluster creation started successfully!"
    echo "Cluster ID: $CLUSTER_ID"
    echo ""
    echo "export CLUSTER_ID=$CLUSTER_ID" >> ~/.oke-env

    # Wait for cluster to become active
    echo "Waiting for cluster to become ACTIVE (this takes ~7 minutes)..."
    oci ce cluster get --cluster-id "$CLUSTER_ID" --wait-for-state ACTIVE --max-wait-seconds 600

    echo ""
    echo "✅ Cluster is now ACTIVE!"
else
    echo "❌ Failed to create cluster"
    echo "Response:"
    echo "$RESULT"
    exit 1
fi
