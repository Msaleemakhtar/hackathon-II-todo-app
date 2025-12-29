# ADR-0017: Data Persistence Architecture: StatefulSet with PersistentVolumeClaim for Redis

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV requires Redis data persistence across pod deletion and recreation. Need to select pod controller type, storage mechanism, persistence strategy, and access mode that work together for data durability in local Kubernetes environment.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Data persistence affects durability, recovery, state management
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Deployment+PVC, EmptyDir, Redis Operator, external Redis
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects Redis storage layer, backup/restore, disaster recovery
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **StatefulSet** with **PersistentVolumeClaim (PVC)** and **AOF persistence** for Redis, using Minikube's **standard StorageClass** with **ReadWriteOnce** access mode.

**Data Persistence Components**:
- **Pod Controller**: StatefulSet (not Deployment) for stable network identity
- **Storage**: PersistentVolumeClaim (PVC) with 1Gi capacity
- **StorageClass**: `standard` (Minikube default hostPath provisioner)
- **Access Mode**: ReadWriteOnce (RWO) - single node read/write
- **Persistence Strategy**: Redis AOF (Append-Only File) enabled via `--appendonly yes`
- **Volume Mount**: `/data` (Redis default data directory)
- **Pod Identity**: `redis-0` (stable StatefulSet pod name)
- **Service**: Headless service (`clusterIP: None`) for stable DNS

**Rationale for Integrated Architecture**:
- StatefulSet + PVC = Stable pod identity + persistent storage across restarts
- AOF persistence + PVC = Data durability even after pod deletion
- Standard StorageClass + Minikube = Zero-config local storage provisioning
- Headless service = Direct pod DNS (`redis-0.redis-service.todo-phaseiv.svc.cluster.local`)

## Consequences

### Positive

- **Constitutional Compliance**: Principle XV mandates PersistentVolumes as MANDATORY production-grade feature
- **Data Durability**: PVC survives pod deletion, recreation, and Kubernetes node restarts
- **Stable Identity**: StatefulSet provides predictable pod name (`redis-0`) for DNS and backup scripts
- **AOF Persistence**: Redis AOF logs all write operations (data recovery even after crash)
- **Zero Configuration**: Minikube standard StorageClass auto-provisions hostPath PVs
- **Automatic Reattachment**: Kubernetes reattaches same PVC to recreated pod (no manual intervention)
- **Testing**: Can validate persistence by deleting pod and verifying data retention
- **Production Portability**: Same PVC pattern works in cloud Kubernetes (different StorageClass)

### Negative

- **Single Replica**: No Redis clustering or replication (single point of failure for availability)
- **Hostpath Limitations**: Minikube hostPath storage not suitable for production (data lost if node fails)
- **No High Availability**: StatefulSet with 1 replica means downtime during pod restart
- **Manual Backup Required**: No automatic backup to external storage (deferred to Phase V)
- **Storage Limits**: 1Gi capacity may be insufficient for large datasets (requires manual PVC resize)
- **AOF Performance**: AOF disk writes add latency compared to RDB snapshots (acceptable for local dev)
- **StatefulSet Complexity**: StatefulSet ordering and parallel update policies more complex than Deployment

## Alternatives Considered

**Alternative 1: Deployment with PersistentVolumeClaim**
- **Pros**: Simpler than StatefulSet, familiar Deployment patterns
- **Cons**: No stable network identity (pod name changes on recreation), DNS unreliable, PVC reattachment may fail
- **Rejected Because**: StatefulSet provides stable pod name required for reliable DNS and backup scripts

**Alternative 2: Redis Operator (e.g., Redis Enterprise Operator)**
- **Pros**: Automatic Redis clustering, HA, failover, backup/restore, monitoring
- **Cons**: Excessive complexity for single-replica local dev, requires operator installation, violates simplicity constraint
- **Rejected Because**: Operator overkill for Phase IV MVP; single StatefulSet sufficient for local development

**Alternative 3: EmptyDir Volume (In-Memory Storage)**
- **Pros**: Faster than disk I/O, simpler configuration (no PVC needed)
- **Cons**: Data lost on pod deletion (violates persistence requirement), violates PersistentVolume constitutional mandate
- **Rejected Because**: Principle XV mandates PersistentVolumes; EmptyDir not acceptable for production

**Alternative 4: External Redis (Cloud-Hosted or Separate VM)**
- **Pros**: No Kubernetes storage management, professional Redis hosting, automatic backups
- **Cons**: Requires external infrastructure, network latency, violates local Kubernetes deployment goal, additional cost
- **Rejected Because**: Phase IV targets local Kubernetes deployment; external dependencies contradict self-contained goal

**Alternative 5: RDB Snapshots Instead of AOF**
- **Pros**: Faster performance (periodic snapshots instead of every write), smaller disk usage
- **Cons**: Data loss window between snapshots (e.g., 5 min), less durable than AOF
- **Rejected Because**: AOF provides better durability for Phase IV; performance overhead acceptable for local dev

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md`
- Research Document: `specs/001-kubernetes-deployment/research.md` (Section 4)
- Data Model: `specs/001-kubernetes-deployment/data-model.md` (Entity 3.1)
- Constitution: `.specify/memory/constitution.md` (Principle XV: Production-Grade Deployment - PersistentVolumes MANDATORY)
- Related ADRs: ADR-0014 (Infrastructure Stack), ADR-0018 (Resource Management)
- Kubernetes StatefulSet Docs: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Redis Persistence: https://redis.io/docs/management/persistence/
