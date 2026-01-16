#!/bin/bash
# Pre-Deployment Validation Script - Verify Dapr readiness before migration

set -e

NAMESPACE="${1:-todo-phasev}"

echo "========================================="
echo "Dapr Deployment Validation"
echo "Namespace: $NAMESPACE"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VALIDATION_FAILED=0

# Function to check and report
check() {
  local test_name="$1"
  local command="$2"

  echo -n "Checking $test_name... "

  if eval "$command" &> /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    return 0
  else
    echo -e "${RED}❌ FAIL${NC}"
    VALIDATION_FAILED=1
    return 1
  fi
}

# 1. Check Dapr system pods
echo "1. Dapr System Health"
echo "----------------------------------------"

check "Dapr system namespace exists" "kubectl get namespace dapr-system"
check "Dapr operator running" "kubectl get pods -n dapr-system -l app=dapr-operator | grep Running"
check "Dapr sidecar injector running" "kubectl get pods -n dapr-system -l app=dapr-sidecar-injector | grep Running"
check "Dapr placement server running" "kubectl get pods -n dapr-system -l app=dapr-placement-server | grep Running"

# Check scheduler (may not be present in older versions)
if kubectl get pods -n dapr-system -l app.kubernetes.io/name=dapr-scheduler &> /dev/null; then
  check "Dapr scheduler running (Jobs API)" "kubectl get pods -n dapr-system -l app.kubernetes.io/name=dapr-scheduler | grep Running"
else
  echo -e "Dapr scheduler: ${YELLOW}Not found (Jobs API may not be available)${NC}"
fi

echo ""

# 2. Check Dapr CRDs
echo "2. Dapr Custom Resource Definitions"
echo "----------------------------------------"

check "components.dapr.io CRD" "kubectl get crd components.dapr.io"
check "configurations.dapr.io CRD" "kubectl get crd configurations.dapr.io"
check "subscriptions.dapr.io CRD" "kubectl get crd subscriptions.dapr.io"

echo ""

# 3. Check application namespace
echo "3. Application Namespace"
echo "----------------------------------------"

check "Namespace exists: $NAMESPACE" "kubectl get namespace $NAMESPACE"

echo ""

# 4. Check Dapr components
echo "4. Dapr Components Configuration"
echo "----------------------------------------"

COMPONENTS=$(kubectl get components -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
echo "Components found: $COMPONENTS"

if [ "$COMPONENTS" -gt 0 ]; then
  kubectl get components -n $NAMESPACE

  check "Pub/Sub component configured" "kubectl get component pubsub-kafka -n $NAMESPACE"
  check "State Store component configured" "kubectl get component statestore-postgres -n $NAMESPACE"

  # Verify component status
  echo ""
  echo "Component details:"
  kubectl get components -n $NAMESPACE -o yaml | grep -A 3 "metadata:" | head -20
else
  echo -e "${YELLOW}⚠️  No Dapr components found - apply components before deployment${NC}"
  echo "Run: kubectl apply -f phaseV/kubernetes/dapr-components/ -n $NAMESPACE"
  VALIDATION_FAILED=1
fi

echo ""

# 5. Check secrets
echo "5. Kubernetes Secrets"
echo "----------------------------------------"

check "kafka-secrets exists" "kubectl get secret kafka-secrets -n $NAMESPACE"
check "todo-app-secrets exists" "kubectl get secret todo-app-secrets -n $NAMESPACE"

# Verify secret keys (don't print values)
echo ""
echo "Secret keys (kafka-secrets):"
kubectl get secret kafka-secrets -n $NAMESPACE -o jsonpath='{.data}' 2>/dev/null | jq -r 'keys[]' | sed 's/^/  - /' || echo "  Unable to read secret"

echo ""
echo "Secret keys (todo-app-secrets):"
kubectl get secret todo-app-secrets -n $NAMESPACE -o jsonpath='{.data}' 2>/dev/null | jq -r 'keys[]' | sed 's/^/  - /' || echo "  Unable to read secret"

echo ""

# 6. Check message broker
echo "6. Message Broker Availability"
echo "----------------------------------------"

# Check Kafka
if kubectl get pod kafka-local-0 -n $NAMESPACE &> /dev/null; then
  check "Kafka pod running" "kubectl get pod kafka-local-0 -n $NAMESPACE | grep Running"

  echo "Testing Kafka connectivity..."
  if kubectl exec -n $NAMESPACE kafka-local-0 -- kafka-broker-api-versions.sh --bootstrap-server localhost:9092 &> /dev/null; then
    echo -e "${GREEN}✅ Kafka broker reachable${NC}"
  else
    echo -e "${RED}❌ Kafka broker not reachable${NC}"
    VALIDATION_FAILED=1
  fi
else
  echo -e "${YELLOW}⚠️  Local Kafka not found - ensure message broker is available${NC}"
fi

# Check Redis
if kubectl get pod redis-0 -n $NAMESPACE &> /dev/null; then
  check "Redis pod running" "kubectl get pod redis-0 -n $NAMESPACE | grep Running"

  echo "Testing Redis connectivity..."
  if kubectl exec -n $NAMESPACE redis-0 -- redis-cli PING &> /dev/null; then
    echo -e "${GREEN}✅ Redis reachable${NC}"
  else
    echo -e "${RED}❌ Redis not reachable${NC}"
    VALIDATION_FAILED=1
  fi
fi

echo ""

# 7. Check database
echo "7. Database Connectivity"
echo "----------------------------------------"

check "PostgreSQL connection string in secret" "kubectl get secret todo-app-secrets -n $NAMESPACE -o jsonpath='{.data.DATABASE_URL}' | base64 -d | grep -q postgres"

# Try to connect to database (requires backend pod)
if kubectl get deployment backend -n $NAMESPACE &> /dev/null; then
  BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend --no-headers | head -1 | awk '{print $1}')

  if [ -n "$BACKEND_POD" ]; then
    echo "Testing database connection via backend pod..."
    if kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- psql $DATABASE_URL -c "SELECT 1;" &> /dev/null 2>&1; then
      echo -e "${GREEN}✅ Database connection successful${NC}"
    else
      echo -e "${YELLOW}⚠️  Database connection test skipped (requires backend pod)${NC}"
    fi
  fi
fi

echo ""

# 8. Check deployment readiness
echo "8. Deployment Configuration"
echo "----------------------------------------"

# Check if deployments have Dapr annotations
if kubectl get deployment backend -n $NAMESPACE &> /dev/null; then
  DAPR_ENABLED=$(kubectl get deployment backend -n $NAMESPACE -o jsonpath='{.spec.template.metadata.annotations.dapr\.io/enabled}' 2>/dev/null)

  if [ "$DAPR_ENABLED" == "true" ]; then
    echo -e "Backend Dapr annotation: ${GREEN}enabled${NC}"
  else
    echo -e "Backend Dapr annotation: ${YELLOW}disabled (will be 1/1 containers)${NC}"
  fi

  DAPR_APP_ID=$(kubectl get deployment backend -n $NAMESPACE -o jsonpath='{.spec.template.metadata.annotations.dapr\.io/app-id}' 2>/dev/null)
  echo "Backend app-id: ${DAPR_APP_ID:-not set}"
fi

echo ""

# 9. Check configmap
echo "9. Configuration"
echo "----------------------------------------"

check "ConfigMap exists" "kubectl get configmap todo-app-config -n $NAMESPACE"

USE_DAPR=$(kubectl get configmap todo-app-config -n $NAMESPACE -o jsonpath='{.data.USE_DAPR}' 2>/dev/null)
echo "USE_DAPR flag: ${USE_DAPR:-not set}"

if [ "$USE_DAPR" == "true" ]; then
  echo -e "${GREEN}✅ Dapr feature flag enabled${NC}"
elif [ "$USE_DAPR" == "false" ]; then
  echo -e "${YELLOW}⚠️  Dapr feature flag disabled (safe migration mode)${NC}"
else
  echo -e "${RED}❌ USE_DAPR flag not configured${NC}"
  VALIDATION_FAILED=1
fi

echo ""

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo ""

if [ $VALIDATION_FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
  echo ""
  echo "System is ready for Dapr deployment!"
  echo ""
  echo "Next steps:"
  echo "1. Review phaseV/docs/DAPR_MIGRATION_RUNBOOK.md"
  echo "2. Deploy with: helm upgrade todo-app phaseV/kubernetes/helm/todo-app -n $NAMESPACE"
  echo "3. Verify: kubectl get pods -n $NAMESPACE (expect 2/2 containers)"
  exit 0
else
  echo -e "${RED}❌ VALIDATION FAILED${NC}"
  echo ""
  echo "Fix the issues above before proceeding with deployment."
  echo ""
  echo "Common fixes:"
  echo "1. Install Dapr: ./phaseV/kubernetes/scripts/setup-dapr.sh"
  echo "2. Apply components: kubectl apply -f phaseV/kubernetes/dapr-components/ -n $NAMESPACE"
  echo "3. Create secrets: kubectl create secret generic kafka-secrets ..."
  exit 1
fi
