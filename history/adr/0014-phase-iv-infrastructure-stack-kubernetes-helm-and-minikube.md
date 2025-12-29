# ADR-0014: Phase IV Infrastructure Stack: Kubernetes, Helm, and Minikube

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV requires deploying the Phase III Todo Chatbot (Frontend, Backend, MCP Server, Redis) to a container orchestration platform with production-grade features including ingress routing, autoscaling, persistent storage, and health monitoring. Need to select orchestration platform, package management, and local development environment that work together for infrastructure-as-code deployment.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Infrastructure stack affects deployment, scalability, operations, cost
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Kustomize, raw kubectl, Docker Swarm, cloud-managed Kubernetes
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects entire deployment architecture, local dev, CI/CD
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Kubernetes v1.28+** for orchestration, **Helm v3.13+** for package management, and **Minikube** for local cluster with **Docker Desktop** as container runtime.

**Infrastructure Stack Components**:
- **Orchestration Platform**: Kubernetes v1.28+ (declarative YAML manifests)
- **Package Manager**: Helm v3.13+ (templated chart deployment)
- **Local Cluster**: Minikube (single-node Kubernetes for development)
- **Container Runtime**: Docker Desktop (image building and runtime)
- **Namespace Isolation**: `todo-phaseiv` (dedicated namespace per constitutional requirement)
- **Ingress Controller**: Nginx Ingress (HTTP routing, enabled via Minikube addon)
- **Metrics**: Metrics Server (CPU/memory metrics for HPA, enabled via Minikube addon)

**Rationale for Integrated Stack**:
- Kubernetes + Helm = Industry-standard orchestration + version-controlled deployment
- Minikube + Docker Desktop = Local development matches production Kubernetes
- Nginx Ingress + Metrics Server = Native Minikube addons (zero external dependencies)
- Helm Charts provide templating for multi-environment deployment (dev, staging, prod)

## Consequences

### Positive

- **Constitutional Compliance**: Principle XIV mandates Kubernetes; Principle XV mandates Helm, Nginx Ingress, HPA, PersistentVolumes
- **Production Parity**: Minikube provides identical Kubernetes API to cloud-managed clusters (GKE, EKS, AKS)
- **Version Control**: Helm charts and YAML manifests are declarative infrastructure-as-code
- **Portability**: Kubernetes manifests portable across Minikube, cloud providers, on-premises clusters
- **Developer Experience**: Minikube addons (`ingress`, `metrics-server`) enable production features locally
- **Rollback Support**: Helm provides one-command rollback to previous releases
- **Ecosystem**: Kubernetes has largest cloud-native ecosystem (CNI plugins, operators, monitoring tools)
- **Learning Value**: Kubernetes skills transfer to production cloud environments

### Negative

- **Complexity**: Kubernetes learning curve steeper than Docker Compose (pods, services, deployments, etc.)
- **Resource Overhead**: Minikube requires 4 CPU + 8GB RAM minimum (heavier than Docker Compose)
- **Local-Only**: Minikube not suitable for production (single-node, no HA, limited scalability)
- **Helm Lock-in**: Switching to Kustomize or raw kubectl requires rewriting templates
- **YAML Verbosity**: Kubernetes manifests more verbose than Docker Compose syntax
- **Startup Time**: Minikube cluster startup slower than `docker-compose up`
- **Debugging Difficulty**: Kubernetes failure modes (CrashLoopBackOff, ImagePullBackOff) require kubectl knowledge

## Alternatives Considered

**Alternative 1: Kustomize + kubectl + Minikube**
- **Pros**: Simpler than Helm (no templating engine), native kubectl support, YAML patches instead of templates
- **Cons**: Less flexible multi-environment configuration, no versioned releases, no rollback support, violates Helm requirement
- **Rejected Because**: Constitutional mandate for Helm v3.13+; Helm provides superior version management and rollback

**Alternative 2: Docker Compose (Phase III approach)**
- **Pros**: Simpler syntax, faster startup, less resource usage, familiar developer experience
- **Cons**: No Kubernetes features (ingress, HPA, PersistentVolumes, namespace isolation), violates constitutional requirement, not production-ready
- **Rejected Because**: Principle XIV requires Kubernetes orchestration; Principle XV requires production-grade features (Ingress, HPA)

**Alternative 3: Cloud-Managed Kubernetes (GKE, EKS, AKS)**
- **Pros**: Production-ready HA, managed control plane, auto-scaling nodes, integrated monitoring
- **Cons**: Requires cloud account, billing setup, network egress costs, slower iteration cycle for local development
- **Rejected Because**: Phase IV targets local development environment; cloud deployment deferred to Phase V

**Alternative 4: Docker Swarm + Minikube Alternative**
- **Pros**: Simpler than Kubernetes, built into Docker, faster learning curve
- **Cons**: Smaller ecosystem, no Helm support, limited cloud provider support, dying technology, violates Kubernetes requirement
- **Rejected Because**: Constitutional mandate for Kubernetes; Docker Swarm has limited industry adoption

**Alternative 5: Kind (Kubernetes in Docker) or K3s (Lightweight Kubernetes)**
- **Pros**: Faster startup than Minikube, lower resource usage, multi-node support (Kind)
- **Cons**: Less mature addon ecosystem than Minikube, fewer tutorials/docs, different cluster architecture
- **Rejected Because**: Minikube has best addon support (ingress, metrics-server) and most comprehensive documentation for local dev

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md`
- Research Document: `specs/001-kubernetes-deployment/research.md` (Sections 1, 2, 3)
- Constitution: `.specify/memory/constitution.md` (Principle XIV: Containerization & Orchestration; Principle XV: Production-Grade Deployment)
- Related ADRs: ADR-0015 (HTTP Routing), ADR-0016 (Autoscaling), ADR-0017 (Data Persistence)
