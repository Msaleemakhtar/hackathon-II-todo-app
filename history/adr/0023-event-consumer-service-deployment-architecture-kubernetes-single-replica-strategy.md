# ADR-0023: Event Consumer Service Deployment Architecture (Kubernetes Single-Replica Strategy)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-01
- **Feature:** 002-event-driven
- **Context:** Phase V introduces two new Kafka consumer services (Notification Service for reminders, Recurring Task Service for task regeneration) that must be deployed alongside existing Phase IV backend. Need to determine deployment architecture that handles consumer group coordination, ensures idempotent processing, and avoids duplicate event handling, while balancing availability against operational complexity for MVP.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will deploy event consumer services using Kubernetes with single-replica strategy for MVP:

- **Deployment Type:** Kubernetes Deployment (not StatefulSet or DaemonSet)
- **Replica Count:** 1 replica per consumer service (notification-service, recurring-task-service)
- **Resource Allocation:** Burstable QoS class (200m CPU request, 256Mi memory limit)
- **Health Checks:** Liveness probe (checks Kafka + DB connectivity), readiness probe (checks consumer lag)
- **Graceful Shutdown:** PreStop hook to commit offsets and close Kafka connections
- **Restart Policy:** Always (automatic restart on failure)
- **Consumer Group Strategy:** Single consumer per group (no partition rebalancing)
- **Idempotency:** Database-level atomic operations (UPDATE with WHERE conditions, duplicate detection)
- **Namespace:** todo-phasev (isolated from Phase IV)

**Kubernetes Deployment Pattern:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
spec:
  replicas: 1  # Single replica for MVP
  template:
    spec:
      containers:
      - name: notification-service
        resources:
          requests: {cpu: 200m, memory: 256Mi}
          limits: {cpu: 500m, memory: 512Mi}
        livenessProbe: {httpGet: {path: /health, port: 8080}}
        lifecycle:
          preStop: {exec: {command: ["/bin/sh", "-c", "sleep 15"]}}
```

## Consequences

### Positive

- **Simplified coordination:** Single replica eliminates Kafka partition rebalancing, consumer group coordination overhead
- **Predictable behavior:** No race conditions between multiple consumers, easier to debug and monitor
- **Lower resource usage:** 200m CPU + 256Mi RAM per service (total 400m CPU, 512Mi RAM for both services)
- **Idempotency simplicity:** Database-level atomic updates sufficient (no distributed locks or external coordination)
- **Faster deployment:** No need to wait for consumer group rebalancing on rolling updates
- **Easier debugging:** Single process to trace logs, no distributed tracing needed for MVP
- **Cost-effective:** Minimal resource footprint fits within minikube development environment
- **Graceful shutdown:** PreStop hook ensures offsets committed before pod termination

### Negative

- **Single point of failure:** If pod crashes, event processing pauses until Kubernetes restarts it (15-30 second gap)
- **No horizontal scaling:** Cannot handle increased event throughput by adding replicas (limited to single consumer)
- **Restart latency:** Kubernetes restart takes 15-30 seconds (users may experience delayed reminders or recurring tasks)
- **No high availability:** Zero redundancy means service is unavailable during pod restarts or node failures
- **Manual scaling required:** Must increase replica count and add partition rebalancing logic for production
- **Resource bottleneck:** Single replica limited by single CPU core and memory limit

## Alternatives Considered

### Alternative A: Multi-Replica Deployment with Consumer Group Coordination
- **Components:** Deployment with 2-3 replicas + Kafka consumer groups with partition assignment
- **Why rejected:**
  - **Coordination complexity:** Requires implementing partition rebalancing logic and handling consumer group state
  - **Idempotency overhead:** Need distributed locks (Redis SETNX) or deduplication tables to prevent duplicate processing
  - **Resource overhead:** 2-3x resource usage (400-600m CPU, 512-768Mi RAM) not justified for <10,000 events/day
  - **Rebalancing delays:** Partition reassignment during rolling updates causes 30-60 second processing pauses
  - **Overkill for MVP:** High availability benefits don't outweigh added complexity at this scale

### Alternative B: StatefulSet with Persistent Volumes
- **Components:** StatefulSet with PersistentVolumeClaim for offset storage + local state management
- **Why rejected:**
  - **Unnecessary persistence:** Kafka manages consumer offsets, no need for local state storage
  - **Higher complexity:** StatefulSet lifecycle management (ordered startup/shutdown) adds complexity
  - **Storage overhead:** PersistentVolumes consume cluster resources and complicate backups
  - **Not suited for consumers:** StatefulSets designed for stateful apps (databases, caches), not event consumers
  - **Slower deployments:** Ordered pod updates slower than Deployment rolling updates

### Alternative C: DaemonSet (One Pod per Node)
- **Components:** DaemonSet to run one consumer pod on each cluster node
- **Why rejected:**
  - **Unsuitable pattern:** DaemonSets are for node-level agents (log collectors, monitoring), not event consumers
  - **No autoscaling:** Cannot scale consumers independently of cluster nodes
  - **Resource waste:** Minikube has single node, so DaemonSet behaves like single-replica Deployment
  - **No benefit:** Consumer workload not node-specific, no advantage to node affinity

### Alternative D: Serverless Functions (Kubernetes-based FaaS like Knative)
- **Components:** Knative Serving + Kafka event source + autoscaling to zero
- **Why rejected:**
  - **Cold start latency:** Scaling from zero adds 5-10 second delay for first event (unacceptable for reminders)
  - **Operational complexity:** Requires Knative installation, eventing configuration, and custom resource management
  - **Consumer group mismatch:** Serverless functions designed for HTTP requests, not long-running Kafka consumers
  - **Offset management issues:** Scaling to zero loses consumer offset state (requires external offset storage)
  - **Overkill for MVP:** Autoscaling benefits not needed for <10,000 events/day

## References

- Feature Spec: [specs/002-event-driven/spec.md](../../specs/002-event-driven/spec.md) (NFR-001, NFR-002)
- Implementation Plan: [specs/002-event-driven/plan.md](../../specs/002-event-driven/plan.md) (Service Deployment section)
- Data Model: [specs/002-event-driven/data-model.md](../../specs/002-event-driven/data-model.md) (Notification Service, Recurring Task Service)
- Related ADRs:
  - ADR-0020 (Event-Driven Architecture Stack)
  - ADR-0014 (Phase IV Infrastructure Stack - Kubernetes, Helm, Minikube)
  - ADR-0018 (Resource Management Strategy - Burstable QoS)
- Kubernetes Docs: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
