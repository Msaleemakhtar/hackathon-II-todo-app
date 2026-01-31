#!/bin/bash
set -e

# Source environment variables
source ~/.oke-env

echo "Configuring kubectl for OKE cluster..."
echo "Cluster ID: $CLUSTER_ID"
echo "Region: $REGION"
echo ""

# Create kubeconfig
mkdir -p ~/.kube
oci ce cluster create-kubeconfig \
  --cluster-id "$CLUSTER_ID" \
  --file ~/.kube/config-oke \
  --region "$REGION" \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Backup existing config if it exists
if [ -f ~/.kube/config ]; then
    cp ~/.kube/config ~/.kube/config.backup
    echo "Backed up existing kubeconfig to ~/.kube/config.backup"
fi

# Merge kubeconfigs
export KUBECONFIG=~/.kube/config:~/.kube/config-oke
kubectl config view --flatten > ~/.kube/config-merged
mv ~/.kube/config-merged ~/.kube/config

# Set context
CONTEXT=$(kubectl config get-contexts -o name | grep "$CLUSTER_ID" | head -1)
kubectl config use-context "$CONTEXT"

echo ""
echo "✅ kubectl configured successfully!"
echo "Current context: $CONTEXT"
echo ""
kubectl cluster-info
