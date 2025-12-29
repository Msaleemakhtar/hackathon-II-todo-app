# ADR-0016: Autoscaling Strategy: HPA with CPU and Memory Metrics

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV requires dynamic scaling of Frontend and Backend deployments based on load. Need to select autoscaling mechanism, metrics source, scaling thresholds, and stabilization policies that work together for responsive scaling while preventing thrashing.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Autoscaling affects performance, cost, reliability under load
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - VPA, KEDA, custom metrics, manual scaling
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects Frontend and Backend deployments, resource planning
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Horizontal Pod Autoscaler (HPA)** with **CPU-based scaling** for Frontend and **CPU + Memory-based scaling** for Backend, using **Metrics Server** for data collection.

**Autoscaling Components**:
- **Autoscaler**: HorizontalPodAutoscaler v2 (Kubernetes built-in)
- **Metrics Source**: Metrics Server (enabled via `minikube addons enable metrics-server`)
- **Frontend HPA**:
  - Min replicas: 2, Max replicas: 5
  - Metric: CPU utilization (70% threshold)
  - Scale-up: Immediate (0s stabilization)
  - Scale-down: 5 minutes stabilization (prevent thrashing)
- **Backend HPA**:
  - Min replicas: 2, Max replicas: 5
  - Metrics: CPU utilization (70% threshold) OR Memory utilization (80% threshold)
  - Scale-up: Immediate (0s stabilization)
  - Scale-down: 5 minutes stabilization
- **MCP Server**: No autoscaling (fixed 1 replica)
- **Redis**: No autoscaling (fixed 1 replica, StatefulSet)

**Rationale for Integrated Strategy**:
- HPA + Metrics Server = Native Kubernetes autoscaling without external dependencies
- CPU-based (Frontend) + CPU+Memory (Backend) = Match workload characteristics (SSR vs API processing)
- 70% CPU / 80% memory thresholds = Industry-standard headroom before scaling
- 5-minute scale-down stabilization = Prevent flapping during traffic spikes

## Consequences

### Positive

- **Constitutional Compliance**: Principle XV mandates HPA as MANDATORY production-grade feature
- **Native Kubernetes**: HPA built into Kubernetes API, no external operators required
- **Responsive Scaling**: Immediate scale-up (0s stabilization) handles traffic spikes quickly
- **Cost Efficiency**: Scale-down after 5 min stabilization reduces resource waste during idle periods
- **Workload-Specific**: Frontend (CPU-only) vs Backend (CPU+memory) matches service characteristics
- **Minikube Addon**: Metrics Server enabled with single command (`minikube addons enable metrics-server`)
- **Resource Baseline**: HPA uses CPU requests as baseline (70% of 500m = 350m triggers scale-up)
- **Testing**: Load tests with Apache Bench can validate HPA behavior in local Minikube

### Negative

- **Metrics Delay**: Metrics Server scrapes every 15s (scaling decisions lag behind real-time load)
- **Cold Start Penalty**: New pods take 10-20s to start (initial delay during scale-up)
- **Thrashing Risk**: Rapid load changes may cause scale-up/scale-down cycles (mitigated by 5-min stabilization)
- **No Custom Metrics**: CPU/memory only (cannot scale on request latency, queue depth, custom business metrics)
- **Memory Metric Instability**: Memory usage may not decrease after scale-down (garbage collection timing)
- **Single Replica Risk**: MCP Server and Redis have no autoscaling (single point of failure under load)
- **Resource Overhead**: Minimum 2 replicas (Frontend + Backend) consume resources even when idle

## Alternatives Considered

**Alternative 1: Vertical Pod Autoscaler (VPA)**
- **Pros**: Automatically adjusts CPU/memory requests and limits based on usage, better resource utilization
- **Cons**: Requires pod restart to apply new limits (downtime), does not increase replica count (no horizontal scaling), not suitable for stateless workloads
- **Rejected Because**: HPA preferred for stateless services (Frontend, Backend); VPA requires pod restart

**Alternative 2: KEDA (Kubernetes Event-Driven Autoscaling)**
- **Pros**: Scales based on external events (message queues, HTTP metrics, custom metrics), scale-to-zero support
- **Cons**: Requires KEDA operator installation, no event sources in Phase IV (no queues, no custom metrics), excessive complexity for CPU-based scaling
- **Rejected Because**: No event sources in Phase IV; CPU/memory metrics sufficient for MVP

**Alternative 3: Custom Metrics (Prometheus + Custom Metrics API)**
- **Pros**: Scale on application-specific metrics (request latency, active users, queue depth)
- **Cons**: Requires Prometheus installation, custom metrics adapter, additional infrastructure, deferred to Phase V
- **Rejected Because**: CPU/memory metrics sufficient for Phase IV; Prometheus setup adds complexity

**Alternative 4: Manual Scaling (kubectl scale)**
- **Pros**: Simple, full control, no metrics dependency
- **Cons**: Violates HPA constitutional requirement, requires manual intervention during traffic spikes, not production-ready
- **Rejected Because**: Principle XV mandates HPA as MANDATORY; manual scaling not acceptable for production

**Alternative 5: Cluster Autoscaler (Node-Level Scaling)**
- **Pros**: Adds nodes when pods cannot be scheduled (resource exhaustion), works with HPA
- **Cons**: Minikube single-node (no node autoscaling possible), cloud-only feature, deferred to Phase V
- **Rejected Because**: Minikube single-node cluster; cluster autoscaling requires multi-node cloud Kubernetes

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md`
- Research Document: `specs/001-kubernetes-deployment/research.md` (Section 3)
- Data Model: `specs/001-kubernetes-deployment/data-model.md` (Entities 6.1, 6.2)
- Constitution: `.specify/memory/constitution.md` (Principle XV: Production-Grade Deployment - HPA MANDATORY)
- Related ADRs: ADR-0014 (Infrastructure Stack), ADR-0018 (Resource Management)
- Kubernetes HPA Docs: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
