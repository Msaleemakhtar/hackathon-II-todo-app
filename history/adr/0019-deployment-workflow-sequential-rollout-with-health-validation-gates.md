# ADR-0019: Deployment Workflow: Sequential Rollout with Health Validation Gates

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV requires deploying 4 interdependent services (Redis, MCP Server, Backend, Frontend) with external Neon PostgreSQL. Need to select deployment order, health validation strategy, wait conditions, and failure handling that work together for reliable startup and dependency satisfaction.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Deployment workflow affects reliability, debugging, rollback
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Parallel deployment, Helm hooks, Init containers
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all services, CI/CD, helm install/upgrade
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **sequential rollout** in **dependency order** with **health validation gates** using `helm install --wait` and `kubectl wait` for readiness confirmation.

**Deployment Workflow Components**:
- **Deployment Order** (sequential, not parallel):
  1. **Redis StatefulSet** (no dependencies) → Wait for Ready
  2. **MCP Server Deployment** (depends on Redis) → Wait for Ready
  3. **Backend Deployment** (depends on Redis, PostgreSQL, MCP) → Wait for Ready (120s timeout for DB migrations)
  4. **Frontend Deployment** (depends on Backend API) → Wait for Ready
  5. **Ingress Resource** (depends on all services) → Wait for LoadBalancer IP
- **Health Validation**: `kubectl wait --for=condition=ready pod -l app=<service> --timeout=60s`
- **Helm Strategy**: `helm install --wait --timeout 10m` (waits for all pods Ready before success)
- **Image Build**: `eval $(minikube docker-env)` + `docker build` (build images inside Minikube)
- **Database Migrations**: Backend initContainer or pre-install Job (run before Backend pods start)

**Rationale for Sequential Workflow**:
- Sequential deployment = Respect dependency graph (Backend needs Redis before startup)
- Health validation gates = Prevent cascading failures from missing dependencies
- Helm --wait flag = Atomic deployment (all services Ready or rollback)
- Minikube Docker env = Use local images without pushing to registry

## Consequences

### Positive

- **Constitutional Compliance**: Research.md Section 8 specifies sequential rollout; plan.md lines 92-93 confirm workflow
- **Dependency Safety**: Each service waits for dependencies to be Ready (prevents CrashLoopBackOff)
- **Clear Failure Modes**: If Redis fails, deployment stops before Backend (easier debugging)
- **Atomic Deployment**: Helm --wait ensures all services Ready or entire deployment fails
- **Fast Iteration**: Minikube Docker env builds images locally (no registry push/pull latency)
- **Health Probe Integration**: kubectl wait uses readinessProbe (validates HTTP /health endpoints)
- **Rollback Support**: Helm rollback to previous release if deployment fails
- **Testing**: Can simulate failures by kubectl delete pod during deployment

### Negative

- **Slower Deployment**: Sequential rollout takes longer than parallel (60s × 4 services = 4 min minimum)
- **Initial Delay**: Must wait for each service before starting next (no concurrent startup)
- **Single Failure Blocks All**: If Redis fails, entire deployment stops (no partial deployment)
- **Manual Dependency Management**: Must maintain correct deployment order in script (no automatic DAG resolution)
- **Cold Start Penalty**: Backend migration initContainer adds 10-20s startup time
- **Minikube IP Change**: Minikube restart requires re-running `eval $(minikube docker-env)`
- **No Rollback Granularity**: Helm rollback all-or-nothing (cannot rollback single service)

## Alternatives Considered

**Alternative 1: Parallel Deployment (helm install without ordering)**
- **Pros**: Faster deployment (all services start simultaneously), simpler script
- **Cons**: Backend/Frontend crash if Redis not ready, CrashLoopBackOff noise, hard to debug, violates dependency graph
- **Rejected Because**: Research.md Section 8 explicitly requires sequential deployment; parallel causes startup failures

**Alternative 2: Helm Hooks for Dependency Ordering**
- **Pros**: Declarative ordering in YAML (pre-install/post-install hooks), no bash script needed
- **Cons**: Helm hooks limited to Jobs/Pods (not for ordering Deployments), complex hook weight management, less readable
- **Rejected Because**: Helm hooks not designed for Deployment ordering; bash script + --wait simpler and more explicit

**Alternative 3: Init Containers for Dependency Waiting**
- **Pros**: Each pod waits for dependencies (e.g., Backend initContainer waits for Redis), declarative in YAML
- **Cons**: Init containers only delay pod startup (do not prevent deployment), CrashLoopBackOff still occurs, less debuggable
- **Rejected Because**: Init containers supplement sequential rollout (used for DB migrations) but do not replace it

**Alternative 4: Kubernetes Operators (e.g., Custom Operator for Todo App)**
- **Pros**: Automatic dependency management, health monitoring, self-healing
- **Cons**: Excessive complexity for Phase IV, requires Go/Rust operator development, violates simplicity constraint
- **Rejected Because**: Operator overkill for 4-service deployment; bash script sufficient for MVP

**Alternative 5: External Orchestration (Argo Workflows, Tekton)**
- **Pros**: DAG-based workflow, visual pipeline UI, advanced dependency management, retry logic
- **Cons**: Requires additional infrastructure (Argo/Tekton installation), violates local Kubernetes simplicity, deferred to Phase V CI/CD
- **Rejected Because**: Phase IV targets local deployment; external orchestration adds unnecessary complexity

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md` (lines 92-93)
- Research Document: `specs/001-kubernetes-deployment/research.md` (Section 8)
- Quickstart: `specs/001-kubernetes-deployment/quickstart.md` (deployment steps)
- Constitution: `.specify/memory/constitution.md` (Principle XV: Production-Grade Deployment)
- Related ADRs: ADR-0014 (Infrastructure Stack), ADR-0015 (HTTP Routing), ADR-0017 (Data Persistence)
- Helm Install Docs: https://helm.sh/docs/helm/helm_install/
- kubectl wait Docs: https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#wait
