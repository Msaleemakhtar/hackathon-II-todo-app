# ADR-0018: Resource Management Strategy: Burstable QoS with CPU and Memory Limits

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV requires resource allocation for Frontend, Backend, MCP Server, and Redis containers. Need to select QoS class, CPU/memory sizing, requests/limits ratio, and enforcement policy that work together for stable performance and efficient resource utilization.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Resource management affects stability, cost, OOMKilled risk
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Guaranteed QoS, BestEffort, no limits, VPA
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all 4 services, node capacity planning, autoscaling
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Burstable QoS class** with **2:1 limits-to-requests ratio** for all containers, with service-specific resource sizing based on Phase III Docker Compose constraints.

**Resource Management Components**:
- **QoS Class**: Burstable (requests < limits for all containers)
- **Frontend (Next.js SSR)**:
  - Requests: 500m CPU, 512Mi RAM
  - Limits: 1000m CPU, 1024Mi RAM (2x requests)
- **Backend (FastAPI + Uvicorn)**:
  - Requests: 500m CPU, 512Mi RAM
  - Limits: 1000m CPU, 1024Mi RAM (2x requests)
- **MCP Server (FastMCP)**:
  - Requests: 250m CPU, 256Mi RAM
  - Limits: 500m CPU, 512Mi RAM (2x requests)
- **Redis (In-Memory Cache)**:
  - Requests: 250m CPU, 128Mi RAM
  - Limits: 500m CPU, 256Mi RAM (2x requests)
- **Enforcement**: Kubernetes cgroup limits, OOMKiller for memory violations

**Rationale for Integrated Strategy**:
- Burstable QoS = Guaranteed minimum (requests) + burst capacity (limits) without resource waste
- 2:1 ratio = Burst capacity for traffic spikes while preventing runaway resource consumption
- Service-specific sizing = Match workload characteristics (SSR > API > tools > cache)
- Constitutional alignment = Matches Phase III Docker Compose resource constraints

## Consequences

### Positive

- **Constitutional Compliance**: Principle XV mandates resource limits as MANDATORY; plan.md specifies exact values
- **Guaranteed Minimum**: Requests ensure each service gets minimum CPU/RAM (prevents starvation)
- **Burst Capacity**: Limits allow 2x burst during traffic spikes (handles load without OOMKilled)
- **Cost Efficiency**: Burstable uses less resources than Guaranteed (idle services consume only requests, not limits)
- **Eviction Priority**: Medium priority (lower than Guaranteed, higher than BestEffort) - balanced stability
- **HPA Compatibility**: HPA uses CPU requests as baseline (70% of 500m = 350m triggers scale-up)
- **OOM Protection**: Memory limits prevent single service consuming entire node RAM
- **Minikube Feasibility**: Total resources (4 services × max limits) fit in 4 CPU + 8GB Minikube cluster

### Negative

- **OOMKilled Risk**: Containers exceeding memory limits killed by Kubernetes (requires restart)
- **CPU Throttling**: Containers exceeding CPU limits throttled (increased latency during burst)
- **No Auto-Adjustment**: Manual sizing (no VPA auto-tuning based on actual usage)
- **Over-Provisioning Risk**: If workloads never burst, limits-to-requests gap wastes capacity
- **Under-Provisioning Risk**: If requests too low, HPA scales prematurely (inefficient replica count)
- **Debugging Difficulty**: OOMKilled events require log analysis to identify memory leaks
- **Minikube Single-Node Limits**: Cannot exceed 4 CPU + 8GB total across all pods

## Alternatives Considered

**Alternative 1: Guaranteed QoS (Requests == Limits)**
- **Pros**: Highest priority, never throttled, never evicted, predictable performance
- **Cons**: Wastes resources during idle periods, higher cost, less efficient cluster utilization, prevents burst capacity
- **Rejected Because**: Burstable preferred for efficiency; Guaranteed wastes resources when services idle

**Alternative 2: BestEffort QoS (No Requests/Limits)**
- **Pros**: Maximum cluster utilization, simplest configuration, no resource waste
- **Cons**: Violates constitutional requirement for resource limits, lowest priority (first to be evicted), no QoS guarantees, OOMKilled under pressure
- **Rejected Because**: Principle XV mandates resource limits as MANDATORY; BestEffort violates constitution

**Alternative 3: Vertical Pod Autoscaler (VPA)**
- **Pros**: Automatically tunes requests/limits based on actual usage, reduces over/under-provisioning
- **Cons**: Requires pod restart to apply new limits (downtime), manual sizing acceptable for MVP, deferred to Phase V
- **Rejected Because**: Manual sizing sufficient for Phase IV; VPA adds complexity without proportional value

**Alternative 4: No Memory Limits (CPU Limits Only)**
- **Pros**: Prevents OOMKilled events, allows unbounded memory usage during burst
- **Cons**: Single service memory leak can consume entire node RAM, violates Burstable QoS definition, risky for stability
- **Rejected Because**: Memory limits required for OOM protection; unbounded memory risk unacceptable

**Alternative 5: Higher Limits-to-Requests Ratio (e.g., 4:1 or 8:1)**
- **Pros**: More burst capacity, handles extreme traffic spikes better
- **Cons**: Greater resource waste, higher OOMKilled risk (pods request 250m but can consume 1000m+), less predictable behavior
- **Rejected Because**: 2:1 ratio industry standard; higher ratios increase instability risk

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md` (lines 44-46)
- Research Document: `specs/001-kubernetes-deployment/research.md` (Section 6)
- Data Model: `specs/001-kubernetes-deployment/data-model.md` (Entities 2.1-3.1)
- Constitution: `.specify/memory/constitution.md` (Principle XV: Production-Grade Deployment - Resource Limits MANDATORY)
- Related ADRs: ADR-0014 (Infrastructure Stack), ADR-0016 (Autoscaling Strategy)
- Kubernetes QoS Docs: https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/
