# Dapr Migration Runbook

**Version**: 1.0
**Last Updated**: 2026-01-16
**Migration Target**: 30 minutes total (with rollback capability)

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Migration Phases](#migration-phases)
3. [Rollback Procedure](#rollback-procedure)
4. [Post-Migration Validation](#post-migration-validation)
5. [Troubleshooting](#troubleshooting)

---

## Pre-Migration Checklist

### Infrastructure Readiness

- [ ] Kubernetes cluster running (v1.21+)
- [ ] Dapr CLI installed (v1.12+)
- [ ] Dapr runtime initialized: `dapr init -k --wait`
- [ ] Dapr system pods healthy: `kubectl get pods -n dapr-system`

### Baseline Metrics Capture

```bash
# Capture current performance metrics
# Event publishing latency
kubectl logs -n todo-phasev deployment/backend -c backend --tail=1000 | \
  grep "event_publish" | awk '{print $NF}' > /tmp/pre-migration-latency.txt

# Consumer lag
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --describe \
    --group email-delivery-group > /tmp/pre-migration-lag.txt

# Task count baseline
kubectl exec -n todo-phasev deployment/backend -c backend -- \
  psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks_phaseiii;" > /tmp/pre-migration-task-count.txt
```

### Backup Current State

```bash
# Tag current Docker images for rollback
export BACKUP_TAG="pre-dapr-$(date +%Y%m%d-%H%M%S)"

docker tag backend:latest backend:$BACKUP_TAG
docker tag notification-service:latest notification-service:$BACKUP_TAG
docker tag email-delivery:latest email-delivery:$BACKUP_TAG
docker tag recurring-service:latest recurring-service:$BACKUP_TAG

# Backup Kubernetes manifests
kubectl get deployment -n todo-phasev -o yaml > /tmp/deployments-backup.yaml
kubectl get configmap todo-app-config -n todo-phasev -o yaml > /tmp/configmap-backup.yaml

# Backup Helm values
cp phaseV/kubernetes/helm/todo-app/values.yaml \
   phaseV/kubernetes/helm/todo-app/values.yaml.backup-$(date +%Y%m%d)
```

### Secrets Configuration

```bash
# Verify Kubernetes secrets exist
kubectl get secret kafka-secrets -n todo-phasev
kubectl get secret todo-app-secrets -n todo-phasev

# Verify secret keys
kubectl get secret kafka-secrets -n todo-phasev -o jsonpath='{.data}' | jq -r 'keys[]'
# Expected: KAFKA_BOOTSTRAP_SERVERS, KAFKA_SASL_USERNAME, KAFKA_SASL_PASSWORD

kubectl get secret todo-app-secrets -n todo-phasev -o jsonpath='{.data}' | jq -r 'keys[]'
# Expected: DATABASE_URL, POSTGRES_CONNECTION_STRING
```

---

## Migration Phases

### Phase 1: Deploy Dapr Components (5 minutes)

**Objective**: Apply Dapr component configurations without affecting running services.

```bash
# Navigate to component directory
cd phaseV/kubernetes/dapr-components

# Apply all Dapr components
kubectl apply -f pubsub-kafka-local.yaml -n todo-phasev
kubectl apply -f statestore-postgres.yaml -n todo-phasev
kubectl apply -f secrets-kubernetes.yaml -n todo-phasev
kubectl apply -f dapr-config.yaml -n todo-phasev

# Verify components created
kubectl get components -n todo-phasev
# Expected: pubsub-kafka, statestore-postgres, secrets-kubernetes

# Verify no errors
kubectl get components -n todo-phasev -o yaml | grep -A 5 "status:"
```

**Success Criteria**:
- ✅ All components show `READY` state
- ✅ No error messages in component status

**Rollback**: If components fail to load, delete them and investigate:
```bash
kubectl delete -f . -n todo-phasev
```

---

### Phase 2: Enable Dapr Sidecars (10 minutes)

**Objective**: Inject Dapr sidecars into all service pods while keeping USE_DAPR=false.

```bash
# Update Helm values to enable Dapr
cd phaseV/kubernetes/helm/todo-app

# Edit values.yaml:
# dapr.enabled: true
# configMap.USE_DAPR: "false"  # Keep feature flag OFF for now

# Deploy with Helm
helm upgrade todo-app . \
  -n todo-phasev \
  --wait \
  --timeout 5m

# Verify all pods have 2/2 containers (app + daprd)
kubectl get pods -n todo-phasev

# Expected output:
# NAME                                   READY   STATUS
# backend-xxxxx                          2/2     Running
# notification-service-xxxxx             2/2     Running
# email-delivery-xxxxx                   2/2     Running
# recurring-service-xxxxx                2/2     Running

# Verify Dapr sidecars loaded components
kubectl logs -n todo-phasev deployment/backend -c daprd --tail=50 | \
  grep "Component loaded"
# Expected: pubsub-kafka, statestore-postgres loaded messages
```

**Success Criteria**:
- ✅ All pods show 2/2 containers
- ✅ All pods are in `Running` state
- ✅ Dapr sidecars successfully loaded components
- ✅ Application continues working normally (USE_DAPR=false)

**Health Check**:
```bash
# Verify application endpoints still work
kubectl port-forward -n todo-phasev svc/backend 8000:8000 &
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Verify Dapr sidecar health
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl http://localhost:3500/v1.0/healthz
# Expected: empty response (200 OK)
```

**Rollback**: If sidecar injection fails:
```bash
# Disable Dapr in values.yaml
# dapr.enabled: false

helm upgrade todo-app . -n todo-phasev --wait
```

---

### Phase 3: Enable Dapr Feature Flag (10 minutes)

**Objective**: Switch event publishing/consumption from aiokafka to Dapr.

```bash
# Update configmap to enable Dapr
kubectl patch configmap todo-app-config -n todo-phasev \
  -p '{"data":{"USE_DAPR":"true"}}'

# Restart services to pick up new config
kubectl rollout restart deployment backend -n todo-phasev
kubectl rollout restart deployment notification-service -n todo-phasev
kubectl rollout restart deployment email-delivery -n todo-phasev
kubectl rollout restart deployment recurring-service -n todo-phasev

# Wait for rollout
kubectl rollout status deployment backend -n todo-phasev --timeout=3m
kubectl rollout status deployment notification-service -n todo-phasev --timeout=3m
kubectl rollout status deployment email-delivery -n todo-phasev --timeout=3m
kubectl rollout status deployment recurring-service -n todo-phasev --timeout=3m

# Verify services started successfully
kubectl get pods -n todo-phasev
```

**Success Criteria**:
- ✅ All pods restarted successfully
- ✅ All pods show 2/2 containers and `Running` state
- ✅ No crash loops or errors

**Validation**:
```bash
# Check backend logs for Dapr usage
kubectl logs -n todo-phasev deployment/backend -c backend --tail=50 | \
  grep -i "dapr\|event"

# Test event publishing via Dapr
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders \
    -H "Content-Type: application/json" \
    -d '{"task_id": "migration-test", "user_id": "test-user"}'

# Check Kafka for event
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic task-reminders \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 5000
```

**Rollback**: If event publishing fails:
```bash
# Revert feature flag
kubectl patch configmap todo-app-config -n todo-phasev \
  -p '{"data":{"USE_DAPR":"false"}}'

# Restart services
kubectl rollout restart deployment -n todo-phasev --all
```

---

### Phase 4: Validate End-to-End Flow (5 minutes)

**Objective**: Verify complete task lifecycle works via Dapr.

```bash
# Create test task via API
kubectl port-forward -n todo-phasev svc/backend 8000:8000 &
PF_PID=$!

# Create task with due date in 30 minutes
FUTURE_TIME=$(date -u -d "+30 minutes" +"%Y-%m-%dT%H:%M:%SZ")

TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "x-user-id: migration-test-user" \
  -d "{
    \"title\": \"Dapr Migration Test Task\",
    \"description\": \"Validates end-to-end Dapr integration\",
    \"priority\": \"high\",
    \"due_date\": \"$FUTURE_TIME\"
  }")

echo "Task created: $TASK_RESPONSE"
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.id')

kill $PF_PID

# Wait for reminder to be sent (notification service polls every 5s)
echo "Waiting 60 seconds for reminder processing..."
sleep 60

# Check notification service logs
kubectl logs -n todo-phasev deployment/notification-service -c notification-service --tail=100 | \
  grep -i "reminder"

# Check email delivery logs
kubectl logs -n todo-phasev deployment/email-delivery -c email-delivery --tail=100 | \
  grep -i "$TASK_ID"

# Verify reminder_sent flag updated in database
kubectl exec -n todo-phasev deployment/backend -c backend -- \
  psql $DATABASE_URL -c "SELECT id, title, reminder_sent FROM tasks_phaseiii WHERE id = $TASK_ID;"
```

**Success Criteria**:
- ✅ Task created successfully via API
- ✅ Reminder event published via Dapr
- ✅ Email delivery service received event
- ✅ Database `reminder_sent` flag updated

**Rollback**: If validation fails, proceed to full rollback procedure below.

---

## Rollback Procedure

**Time Target**: < 30 minutes
**Trigger Conditions**:
- Event publishing latency >200ms p95 for 5 minutes
- Consumer lag >1000 messages for 10 minutes
- Application error rate >1% for 5 minutes
- Dapr sidecar memory >256MB per pod
- Duplicate reminders detected

### Step 1: Disable Dapr Feature Flag (2 minutes)

```bash
# Revert USE_DAPR to false
kubectl patch configmap todo-app-config -n todo-phasev \
  -p '{"data":{"USE_DAPR":"false"}}'

# Restart services
kubectl rollout restart deployment backend -n todo-phasev
kubectl rollout restart deployment notification-service -n todo-phasev
kubectl rollout restart deployment email-delivery -n todo-phasev
kubectl rollout restart deployment recurring-service -n todo-phasev

# Wait for rollout
kubectl rollout status deployment -n todo-phasev --all --timeout=3m
```

### Step 2: Remove Dapr Sidecars (5 minutes)

```bash
# Update Helm values
cd phaseV/kubernetes/helm/todo-app

# Edit values.yaml:
# dapr.enabled: false

# Redeploy
helm upgrade todo-app . -n todo-phasev --wait --timeout 5m

# Verify pods back to 1/1 containers
kubectl get pods -n todo-phasev
```

### Step 3: Restore Pre-Migration Images (Optional, if needed)

```bash
# Only if new Docker images were deployed with breaking changes

# Rollback to previous Helm revision
helm rollback todo-app -n todo-phasev

# Or rollback specific deployments
kubectl rollout undo deployment backend -n todo-phasev
kubectl rollout undo deployment notification-service -n todo-phasev
kubectl rollout undo deployment email-delivery -n todo-phasev
kubectl rollout undo deployment recurring-service -n todo-phasev
```

### Step 4: Verify Rollback Successful (3 minutes)

```bash
# Check pods healthy
kubectl get pods -n todo-phasev
# All should be 1/1 Running

# Verify Kafka consumers reconnected
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --describe \
    --group email-delivery-group

# Test task creation
kubectl port-forward -n todo-phasev svc/backend 8000:8000 &
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "x-user-id: rollback-test" \
  -d '{"title": "Rollback Test", "priority": "medium"}'

# Verify event in Kafka
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic task-events \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 5000
```

### Step 5: Clean Up Dapr Components (Optional)

```bash
# Remove Dapr components if rollback is permanent
kubectl delete -f phaseV/kubernetes/dapr-components/ -n todo-phasev

# Dapr system pods remain - can be uninstalled if needed
# dapr uninstall -k
```

---

## Post-Migration Validation

### Performance Comparison

```bash
# Compare latency metrics
kubectl logs -n todo-phasev deployment/backend -c backend --tail=1000 | \
  grep "event_publish" | awk '{print $NF}' > /tmp/post-migration-latency.txt

# Calculate p95 latency
sort -n /tmp/post-migration-latency.txt | awk 'BEGIN{c=0} {a[c]=$1; c++} END{print a[int(c*0.95)]}'

# Compare with pre-migration baseline
echo "Pre-migration p95:"
sort -n /tmp/pre-migration-latency.txt | awk 'BEGIN{c=0} {a[c]=$1; c++} END{print a[int(c*0.95)]}'
```

### Consumer Lag Check

```bash
# Verify no consumer lag buildup
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --describe \
    --group dapr-consumer-group
```

### Functional Tests

```bash
# Run full test suite
cd phaseV/kubernetes/scripts

# Phase 4 test
./test-infrastructure-swap.sh

# Phase 5 test
./test-simplified-operations.sh

# Phase 6 test
./test-guaranteed-job-execution.sh
```

---

## Troubleshooting

### Issue: Dapr Sidecar Not Injecting

**Symptoms**: Pods show 1/1 containers instead of 2/2.

**Resolution**:
```bash
# Check Dapr injector service
kubectl get pods -n dapr-system -l app=dapr-sidecar-injector

# Verify namespace labeled for injection
kubectl get namespace todo-phasev -o yaml | grep dapr

# Check deployment annotations
kubectl get deployment backend -n todo-phasev -o yaml | grep -A 5 "annotations"

# Re-apply annotations if missing
kubectl patch deployment backend -n todo-phasev -p '
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"
    dapr.io/app-port: "8000"
'
```

### Issue: CloudEvents Parsing Errors

**Symptoms**: Consumer logs show JSON parsing errors, consumer lag increases.

**Resolution**:
```bash
# Check consumer logs for CloudEvents structure
kubectl logs -n todo-phasev deployment/email-delivery -c email-delivery --tail=100

# Verify Dapr wraps events in CloudEvents format
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}' -v

# If needed, disable CloudEvents wrapping (escape hatch)
# Add to publish metadata: rawPayload: true
```

### Issue: Duplicate Reminders

**Symptoms**: Users receive multiple reminder emails for same task.

**Resolution**:
```bash
# Check notification service replica count
kubectl get deployment notification-service -n todo-phasev

# Verify Jobs API registration
kubectl logs -n todo-phasev deployment/notification-service -c notification-service | \
  grep "job registered"

# Check Dapr scheduler logs
kubectl logs -n dapr-system deployment/dapr-scheduler | grep "check-due-tasks"

# Verify state store idempotency tracking
kubectl exec -n todo-phasev deployment/notification-service -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore-postgres/reminder:task:123
```

---

## Migration Timeline

| Phase | Duration | Critical? | Rollback Point |
|-------|----------|-----------|----------------|
| 1. Deploy Dapr Components | 5 min | No | Delete components |
| 2. Enable Dapr Sidecars | 10 min | No | Disable in Helm |
| 3. Enable Feature Flag | 10 min | **YES** | Disable flag, restart |
| 4. Validate End-to-End | 5 min | **YES** | Full rollback |
| **Total** | **30 min** | - | **< 30 min** |

## Sign-Off Checklist

Post-migration, verify:

- [ ] All services healthy (kubectl get pods)
- [ ] Event publishing working (create test task)
- [ ] Reminders being sent (check notification logs)
- [ ] No consumer lag (check Kafka consumer groups)
- [ ] Performance within baseline (< 100ms p95 latency)
- [ ] No duplicate reminders (check email delivery logs)
- [ ] Dapr sidecar memory < 128MB (kubectl top pods)
- [ ] No error spikes (check application logs)

**Migration Lead**: _________________
**Date**: _________________
**Sign-Off**: _________________
