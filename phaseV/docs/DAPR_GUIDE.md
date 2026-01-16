# Dapr Integration Guide

**Version**: 1.0
**Last Updated**: 2026-01-16
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Configuration](#component-configuration)
4. [Infrastructure Portability](#infrastructure-portability)
5. [Secret Management](#secret-management)
6. [Operational Procedures](#operational-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)

---

## Overview

This guide covers the Dapr integration for the Phase V Todo App event-driven architecture. Dapr provides infrastructure abstraction for:

- **Pub/Sub**: Event publishing and consumption via Kafka or Redis
- **State Management**: Idempotency tracking and job state persistence
- **Jobs API**: Scheduled job execution with horizontal scaling
- **Secrets Management**: Secure credential storage and rotation

### Benefits

- **Infrastructure Portability**: Swap message brokers without code changes
- **Simplified Operations**: Declarative configuration for retries, DLQ, authentication
- **Horizontal Scaling**: Multi-replica safety with guaranteed single execution
- **Standardization**: CloudEvents format for event interoperability

---

## Architecture

### Component Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Backend    │  │ Notification │  │Email Delivery│     │
│  │              │  │   Service    │  │   Service    │     │
│  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │     │
│  │  │  App   │  │  │  │  App   │  │  │  │  App   │  │     │
│  │  │ (8000) │  │  │  │ (8001) │  │  │  │ (8002) │  │     │
│  │  └────┬───┘  │  │  └────┬───┘  │  │  └────┬───┘  │     │
│  │       │      │  │       │      │  │       │      │     │
│  │  ┌────▼───┐  │  │  ┌────▼───┐  │  │  ┌────▼───┐  │     │
│  │  │  Dapr  │  │  │  │  Dapr  │  │  │  │  Dapr  │  │     │
│  │  │Sidecar │  │  │  │Sidecar │  │  │  │Sidecar │  │     │
│  │  │ (3500) │  │  │  │ (3500) │  │  │  │ (3500) │  │     │
│  │  └────┬───┘  │  │  └────┬───┘  │  │  └────┬───┘  │     │
│  └───────┼──────┘  └───────┼──────┘  └───────┼──────┘     │
│          │                 │                 │             │
│          └─────────────────┴─────────────────┘             │
│                            │                                │
│          ┌─────────────────┴─────────────────┐             │
│          │        Dapr Components            │             │
│          │  - pubsub-kafka / pubsub-redis    │             │
│          │  - statestore-postgres            │             │
│          │  - secrets-kubernetes             │             │
│          │  - jobs-scheduler                 │             │
│          └─────────────────┬─────────────────┘             │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         ┌────▼────┐                  ┌────▼────┐
         │  Kafka  │                  │  Redis  │
         │ (Local) │                  │         │
         └─────────┘                  └─────────┘
```

### Event Flow

1. **Application** calls Dapr HTTP API on `localhost:3500`
2. **Dapr Sidecar** handles CloudEvents wrapping, authentication, retries
3. **Message Broker** (Kafka/Redis) receives and distributes events
4. **Dapr Sidecar** polls broker, delivers to application HTTP endpoint
5. **Application** processes event, returns HTTP 200 for success

---

## Component Configuration

### Pub/Sub - Kafka (Local)

**File**: `phaseV/kubernetes/dapr-components/pubsub-kafka-local.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-phasev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-local.todo-phasev.svc.cluster.local:9092"
    - name: authType
      value: "none"
    - name: consumerGroup
      value: "dapr-consumer-group"
    - name: clientID
      value: "dapr-kafka-client"
    - name: enableIdempotence
      value: "true"
    - name: acks
      value: "all"
```

**Key Configuration**:
- `brokers`: Kafka broker address (DNS or IP:PORT)
- `authType`: `none` (local), `sasl_plaintext`, `sasl_ssl` (production)
- `enableIdempotence`: Ensures exactly-once publishing
- `acks`: `all` for durability (leader + all replicas)

### Pub/Sub - Kafka (Production - Redpanda Cloud)

**File**: `phaseV/kubernetes/dapr-components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-phasev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: KAFKA_BOOTSTRAP_SERVERS
    - name: authType
      value: "sasl_ssl"
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: KAFKA_SASL_USERNAME
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: KAFKA_SASL_PASSWORD
    - name: consumerGroup
      value: "dapr-consumer-group"
    - name: enableIdempotence
      value: "true"
    - name: acks
      value: "all"
auth:
  secretStore: kubernetes-secrets
```

**Security Features**:
- Credentials stored in Kubernetes secrets (not inline)
- SASL_SSL authentication with SCRAM-SHA-256
- TLS encryption for data in transit
- Secret rotation without deployment changes

### Pub/Sub - Redis Streams (Alternative)

**File**: `phaseV/kubernetes/dapr-components/pubsub-redis.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-phasev
spec:
  type: pubsub.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis.todo-phasev.svc.cluster.local:6379"
    - name: redisPassword
      value: ""
    - name: consumerID
      value: "dapr-redis-consumer"
    - name: processingTimeout
      value: "60s"
    - name: redeliverInterval
      value: "30s"
```

**Use Cases**:
- Development/testing without Kafka
- Low-latency event processing (<10ms)
- Simplified infrastructure for non-critical workloads

---

## Infrastructure Portability

### Swapping Message Brokers

**Goal**: Switch from Kafka to Redis Streams without code changes.

#### Step 1: Baseline Metrics (Kafka)

```bash
# Capture current performance
kubectl port-forward -n todo-phasev svc/backend 8000:8000 &

# Run load test
for i in {1..100}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"title": "Test task '$i'", "user_id": 1}'
done

# Check consumer lag
kubectl exec -n todo-phasev kafka-local-0 -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group dapr-consumer-group
```

#### Step 2: Switch to Redis

```bash
# Apply Redis component (replaces pubsub-kafka)
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-redis.yaml

# Restart services to pick up new component
kubectl rollout restart deployment -n todo-phasev backend
kubectl rollout restart deployment -n todo-phasev notification-service
kubectl rollout restart deployment -n todo-phasev email-delivery
kubectl rollout restart deployment -n todo-phasev recurring-service

# Wait for rollout
kubectl rollout status deployment -n todo-phasev backend
```

#### Step 3: Validate Event Flow

```bash
# Test event publishing via Dapr
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders \
    -H "Content-Type: application/json" \
    -d '{"task_id": "test-123", "user_id": "user-456"}'

# Check Redis streams
kubectl exec -n todo-phasev redis-0 -- redis-cli XLEN task-reminders
kubectl exec -n todo-phasev redis-0 -- redis-cli XINFO STREAM task-reminders
```

#### Step 4: Compare Performance

```bash
# Re-run load test with Redis
for i in {1..100}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"title": "Test task Redis '$i'", "user_id": 1}'
done

# Compare latency metrics
kubectl logs -n todo-phasev deployment/backend -c backend | grep "event_publish_duration"
```

#### Step 5: Switch Back to Kafka

```bash
# Reapply Kafka component
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka-local.yaml

# Restart services
kubectl rollout restart deployment -n todo-phasev --all

# Verify zero message loss
# (Compare task count before/after swap)
```

### Migration Between Kafka Providers

**Scenario**: Migrate from Redpanda Cloud to AWS MSK without code changes.

#### Prerequisites

1. Provision AWS MSK cluster
2. Configure security groups for Kubernetes cluster access
3. Create Kafka topics on MSK (match existing topic names)
4. Generate SASL credentials for MSK

#### Migration Steps

```bash
# 1. Create new Kubernetes secret with MSK credentials
kubectl create secret generic kafka-secrets-msk \
  --from-literal=KAFKA_BOOTSTRAP_SERVERS="b-1.msk-cluster.kafka.us-east-1.amazonaws.com:9096" \
  --from-literal=KAFKA_SASL_USERNAME="msk-user" \
  --from-literal=KAFKA_SASL_PASSWORD="msk-password" \
  -n todo-phasev

# 2. Update Dapr component to reference new secret
# Edit phaseV/kubernetes/dapr-components/pubsub-kafka.yaml
# Change secretKeyRef.name from 'kafka-secrets' to 'kafka-secrets-msk'

# 3. Apply updated component
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka.yaml

# 4. Rolling restart (zero downtime)
kubectl rollout restart deployment -n todo-phasev backend
kubectl rollout restart deployment -n todo-phasev notification-service
kubectl rollout restart deployment -n todo-phasev email-delivery
kubectl rollout restart deployment -n todo-phasev recurring-service

# 5. Monitor rollout
kubectl rollout status deployment -n todo-phasev --all

# 6. Verify consumer offsets preserved
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl http://localhost:3500/v1.0-alpha1/healthz
```

**Expected Outcome**: Services reconnect to AWS MSK automatically. Consumer offsets start from 0 on new broker (topics are new), but no application code changes required.

---

## Secret Management

### Kubernetes Secret Rotation Procedure

**Goal**: Rotate Kafka credentials without service downtime.

#### Step 1: Generate New Credentials

```bash
# Generate new SASL credentials in Redpanda/MSK console
# Example: username=dapr-user-v2, password=new-secure-password
```

#### Step 2: Create New Secret Version

```bash
# Create secret with new credentials (keep old secret temporarily)
kubectl create secret generic kafka-secrets-v2 \
  --from-literal=KAFKA_BOOTSTRAP_SERVERS="your-broker.redpanda.cloud:9092" \
  --from-literal=KAFKA_SASL_USERNAME="dapr-user-v2" \
  --from-literal=KAFKA_SASL_PASSWORD="new-secure-password" \
  -n todo-phasev

# Verify secret created
kubectl get secret kafka-secrets-v2 -n todo-phasev -o yaml
```

#### Step 3: Update Dapr Component

```bash
# Edit phaseV/kubernetes/dapr-components/pubsub-kafka.yaml
# Change all secretKeyRef.name from 'kafka-secrets' to 'kafka-secrets-v2'

# Apply updated component
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka.yaml

# Verify component updated
kubectl get component pubsub-kafka -n todo-phasev -o yaml
```

#### Step 4: Rolling Restart Services

```bash
# Restart services one at a time to pick up new secret
kubectl rollout restart deployment -n todo-phasev backend
kubectl rollout status deployment -n todo-phasev backend --timeout=5m

kubectl rollout restart deployment -n todo-phasev notification-service
kubectl rollout status deployment -n todo-phasev notification-service --timeout=5m

kubectl rollout restart deployment -n todo-phasev email-delivery
kubectl rollout status deployment -n todo-phasev email-delivery --timeout=5m

kubectl rollout restart deployment -n todo-phasev recurring-service
kubectl rollout status deployment -n todo-phasev recurring-service --timeout=5m
```

#### Step 5: Validate Connectivity

```bash
# Check Dapr sidecar logs for successful Kafka connection
kubectl logs -n todo-phasev deployment/backend -c daprd | grep -i "kafka"
kubectl logs -n todo-phasev deployment/backend -c daprd | grep -i "pubsub-kafka"

# Test event publishing
kubectl exec -n todo-phasev deployment/backend -c backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders \
    -H "Content-Type: application/json" \
    -d '{"test": "connectivity", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
```

#### Step 6: Cleanup Old Secret

```bash
# Wait 24 hours to ensure no issues
# Then delete old secret
kubectl delete secret kafka-secrets -n todo-phasev
```

### Secret Rotation Best Practices

1. **Test in Staging First**: Always test rotation procedure in staging environment
2. **Maintain Old Credentials**: Keep old secret for 24-48 hours for rollback
3. **Monitor Logs**: Watch Dapr sidecar logs during rotation for connection errors
4. **Rolling Restart**: Restart services one at a time to maintain availability
5. **Verify Health**: Check Dapr health endpoints after each restart
6. **Document Changes**: Log rotation date and new secret version in runbook

---

## Operational Procedures

### Deploying Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f phaseV/kubernetes/dapr-components/

# Verify components loaded
kubectl get components -n todo-phasev

# Expected output:
# NAME               AGE
# pubsub-kafka       5m
# statestore-postgres 5m
# secrets-kubernetes  5m
# jobs-scheduler      5m
```

### Health Checks

```bash
# Check Dapr system pods
kubectl get pods -n dapr-system

# Check application pods (should be 2/2 containers)
kubectl get pods -n todo-phasev

# Check Dapr sidecar health
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl http://localhost:3500/v1.0/healthz
```

### Viewing Dapr Logs

```bash
# Application logs
kubectl logs -n todo-phasev deployment/backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -n todo-phasev deployment/backend -c daprd --tail=100 -f

# Filter for pub/sub events
kubectl logs -n todo-phasev deployment/backend -c daprd | grep "pubsub"

# Filter for component errors
kubectl logs -n todo-phasev deployment/backend -c daprd | grep -i "error"
```

### Debugging Event Flow

```bash
# 1. Publish test event directly via Dapr HTTP API
kubectl exec -n todo-phasev deployment/backend -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders \
    -H "Content-Type: application/json" \
    -d '{"task_id": "debug-123", "user_id": "user-456", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# 2. Check if event appears in Kafka
kubectl exec -n todo-phasev kafka-local-0 -- \
  kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic task-reminders \
    --from-beginning \
    --max-messages 10

# 3. Check subscription endpoint is registered
kubectl exec -n todo-phasev deployment/backend -c backend -- \
  curl http://localhost:8000/events/dapr/subscribe

# 4. Check consumer logs for event delivery
kubectl logs -n todo-phasev deployment/email-delivery -c email-delivery | grep "debug-123"
```

---

## Troubleshooting

### Issue: Dapr Sidecar Not Injecting

**Symptoms**: Pods show 1/1 containers instead of 2/2.

**Diagnosis**:
```bash
kubectl get pods -n todo-phasev
# If showing 1/1, check annotations
kubectl get deployment backend -n todo-phasev -o yaml | grep -A 5 "annotations"
```

**Solution**:
```bash
# Ensure annotations present in deployment:
# dapr.io/enabled: "true"
# dapr.io/app-id: "backend"
# dapr.io/app-port: "8000"

# If missing, add annotations and redeploy
kubectl edit deployment backend -n todo-phasev
```

### Issue: Kafka Connection Failures

**Symptoms**: Dapr logs show "failed to connect to broker" errors.

**Diagnosis**:
```bash
kubectl logs -n todo-phasev deployment/backend -c daprd | grep -i "kafka"
kubectl logs -n todo-phasev deployment/backend -c daprd | grep -i "error"
```

**Common Causes & Solutions**:

1. **Wrong Broker Address**:
   ```bash
   # Verify broker address in component
   kubectl get component pubsub-kafka -n todo-phasev -o yaml | grep -i "brokers"
   ```

2. **Invalid Credentials**:
   ```bash
   # Verify secret exists and has correct keys
   kubectl get secret kafka-secrets -n todo-phasev -o yaml
   kubectl get secret kafka-secrets -n todo-phasev -o jsonpath='{.data.KAFKA_SASL_USERNAME}' | base64 -d
   ```

3. **Network Connectivity**:
   ```bash
   # Test connectivity from pod
   kubectl exec -n todo-phasev deployment/backend -c backend -- \
     nc -zv kafka-local.todo-phasev.svc.cluster.local 9092
   ```

### Issue: CloudEvents Parsing Errors

**Symptoms**: Consumer returns HTTP 500, logs show JSON parsing errors.

**Diagnosis**:
```bash
kubectl logs -n todo-phasev deployment/email-delivery -c email-delivery | grep -i "cloudevents"
```

**Solution**:
```python
# Update consumer to extract data from CloudEvents envelope
def handle_reminder_event(request_body: dict):
    # CloudEvents structure
    if "data" in request_body and "specversion" in request_body:
        event_data = request_body["data"]  # Extract actual event
    else:
        event_data = request_body  # Raw payload mode

    # Process event_data
    task_id = event_data["task_id"]
    user_id = event_data["user_id"]
    # ...
```

### Issue: Duplicate Reminders

**Symptoms**: Users receive multiple emails for the same task.

**Diagnosis**:
```bash
# Check if multiple replicas processing same job
kubectl get pods -n todo-phasev -l app=notification-service

# Check notification service logs for duplicate processing
kubectl logs -n todo-phasev deployment/notification-service -c notification-service | grep "task_id: 123"
```

**Solution**:
```bash
# Verify Dapr Jobs API configuration
kubectl logs -n dapr-system deployment/dapr-scheduler | grep "check-due-tasks"

# Check idempotency state entries
kubectl exec -n todo-phasev deployment/notification-service -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore-postgres/last_poll_timestamp
```

---

## Performance Tuning

### Optimizing Event Latency

**Target**: Event publish latency < 100ms p95

**Tuning Parameters**:

1. **Kafka Batch Settings** (`pubsub-kafka.yaml`):
   ```yaml
   - name: lingerMs
     value: "10"  # Reduce for lower latency (trade-off: lower throughput)
   - name: batchSize
     value: "16384"  # Increase for higher throughput
   ```

2. **Dapr HTTP Client** (`phaseV/backend/app/dapr/client.py`):
   ```python
   # Use connection pooling
   self.client = httpx.AsyncClient(
       timeout=httpx.Timeout(10.0),
       limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
   )
   ```

3. **Dapr Sidecar Resources**:
   ```yaml
   annotations:
     dapr.io/sidecar-memory-limit: "256Mi"  # Increase if memory constrained
     dapr.io/sidecar-cpu-limit: "500m"  # Increase for higher throughput
   ```

### Optimizing Consumer Throughput

**Target**: Process 10 messages/batch with <200ms latency

**Tuning Parameters**:

1. **Consumer Concurrency** (`pubsub-kafka.yaml`):
   ```yaml
   - name: maxConcurrency
     value: "10"  # Parallel message processing
   ```

2. **Message Handler Timeout** (`pubsub-kafka.yaml`):
   ```yaml
   - name: messageHandlerTimeout
     value: "60s"  # Increase for slow consumers
   ```

3. **Application Processing**:
   ```python
   # Use async processing for I/O-bound operations
   async def handle_event(event_data: dict):
       async with httpx.AsyncClient() as client:
           await client.post("http://email-service/send", json=event_data)
   ```

### Monitoring Metrics

```bash
# Enable Dapr metrics
kubectl edit deployment backend -n todo-phasev
# Add annotation: dapr.io/enable-metrics: "true"

# Port-forward Prometheus endpoint
kubectl port-forward -n todo-phasev deployment/backend 9090:9090

# Query metrics
curl http://localhost:9090/metrics | grep dapr_pubsub
```

**Key Metrics**:
- `dapr_pubsub_publish_duration_ms`: Event publish latency
- `dapr_pubsub_deliver_duration_ms`: Event delivery latency
- `dapr_pubsub_failed_publishes_total`: Failed publish count
- `dapr_component_state_store_request_duration_ms`: State store latency

---

## Summary

This guide provides comprehensive documentation for:

✅ **Component Configuration**: Pub/Sub (Kafka/Redis), State Store, Secrets, Jobs
✅ **Infrastructure Portability**: Swapping message brokers without code changes
✅ **Secret Management**: Kubernetes secret rotation procedures
✅ **Operational Procedures**: Deployment, health checks, debugging
✅ **Troubleshooting**: Common issues and solutions
✅ **Performance Tuning**: Latency optimization and monitoring

For additional support:
- Dapr Documentation: https://docs.dapr.io
- Project Issues: File bug reports at project repository
- Team Contact: Reach out to DevOps team for production support
