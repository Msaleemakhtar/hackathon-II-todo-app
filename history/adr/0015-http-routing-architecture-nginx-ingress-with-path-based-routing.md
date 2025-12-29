# ADR-0015: HTTP Routing Architecture: Nginx Ingress with Path-Based Routing

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-26
- **Feature:** 001-kubernetes-deployment
- **Context:** Phase IV Kubernetes deployment requires external HTTP access to Frontend (/) and Backend (/api) services. Need to select ingress controller, routing strategy, and DNS configuration that work together for local development while supporting future production deployment.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Ingress affects external access, routing, security, scalability
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Traefik, HAProxy, Istio Gateway, host-based routing
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all external-facing services, frontend-backend communication
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Nginx Ingress Controller** with **path-based routing** and **local DNS configuration** (todo-app.local via /etc/hosts).

**HTTP Routing Components**:
- **Ingress Controller**: Nginx Ingress Controller (official Kubernetes implementation)
- **Installation**: Minikube addon (`minikube addons enable ingress`)
- **Routing Strategy**: Path-based routing (single host, multiple paths)
  - `/api` → backend-service:8000 (API requests)
  - `/` → frontend-service:3000 (frontend application)
- **Path Ordering**: /api MUST come before / in Ingress rules (ensure API requests don't route to frontend)
- **DNS Configuration**: /etc/hosts entry `<minikube-ip> todo-app.local` for local access
- **Hostname**: `todo-app.local` (local domain for development)
- **SSL/TLS**: Disabled for local dev (`ssl-redirect: "false"` annotation)

**Rationale for Integrated Architecture**:
- Nginx Ingress + Path-based routing = Single entry point for all HTTP traffic
- Minikube addon + /etc/hosts = Zero external dependencies for local dev
- Path ordering (/api before /) = Correct routing without complex regex

## Consequences

### Positive

- **Constitutional Compliance**: Principle XV mandates Nginx Ingress as MANDATORY production-grade feature
- **Native Minikube Support**: Zero-config addon installation (`minikube addons enable ingress`)
- **Industry Standard**: Nginx Ingress most widely adopted in Kubernetes ecosystem
- **Path-Based Routing**: Single hostname simplifies DNS and CORS configuration
- **Annotation-Based Config**: CORS, rate limiting, timeouts configurable via annotations (no separate config files)
- **Production Portability**: Same Nginx Ingress works in cloud Kubernetes (GKE, EKS, AKS)
- **Simplicity**: /etc/hosts DNS configuration requires no external DNS server
- **Debugging**: kubectl logs can show request routing and errors

### Negative

- **Path Ordering Critical**: Incorrect path order (/  before /api) breaks API routing silently
- **Local DNS Manual Setup**: /etc/hosts requires manual edit (not automated in Minikube)
- **SSL Complexity**: TLS certificate management required for production (deferred to Phase V)
- **Single Point of Failure**: Nginx Ingress Controller pod crash blocks all external access
- **Limited Load Balancing**: Single Nginx pod (no HA in Minikube, production requires multiple replicas)
- **Minikube IP Changes**: Minikube restart may change IP, requiring /etc/hosts update
- **Host-Based Routing Not Used**: Cannot route different hostnames to different services (all traffic to todo-app.local)

## Alternatives Considered

**Alternative 1: Traefik Ingress Controller**
- **Pros**: Simpler configuration, automatic Let's Encrypt integration, better dashboard
- **Cons**: Less documentation for Minikube, smaller community, violates Nginx constitutional requirement, fewer production deployments
- **Rejected Because**: Principle XV mandates Nginx Ingress; Nginx has larger ecosystem and better Minikube support

**Alternative 2: HAProxy Ingress Controller**
- **Pros**: High performance, mature load balancing, enterprise-grade features
- **Cons**: Smaller Kubernetes community, less documentation, violates Nginx requirement, complex configuration
- **Rejected Because**: Constitutional mandate for Nginx Ingress; HAProxy has steeper learning curve

**Alternative 3: Istio Gateway (Service Mesh)**
- **Pros**: Advanced traffic management, mTLS, observability, circuit breaking
- **Cons**: Excessive complexity for Phase IV (requires sidecar injection, control plane, telemetry), violates simplicity constraint, resource overhead
- **Rejected Because**: Service mesh complexity exceeds Phase IV requirements; Istio requires additional control plane pods

**Alternative 4: Host-Based Routing (frontend.todo-app.local, api.todo-app.local)**
- **Pros**: Clear service separation, easier DNS debugging, supports service-specific SSL certificates
- **Cons**: Requires multiple /etc/hosts entries, complicates CORS (multiple origins), more complex Ingress configuration
- **Rejected Because**: Path-based routing simpler for local dev; single hostname reduces /etc/hosts edits and CORS complexity

**Alternative 5: NodePort or LoadBalancer Services (No Ingress)**
- **Pros**: Simpler than Ingress (no controller needed), direct port access
- **Cons**: Violates Nginx Ingress constitutional requirement, no path-based routing, exposes multiple ports, not production-ready
- **Rejected Because**: Principle XV mandates Nginx Ingress as MANDATORY; NodePort not suitable for HTTP routing

## References

- Feature Spec: `specs/001-kubernetes-deployment/spec.md`
- Implementation Plan: `specs/001-kubernetes-deployment/plan.md`
- Research Document: `specs/001-kubernetes-deployment/research.md` (Section 2)
- Data Model: `specs/001-kubernetes-deployment/data-model.md` (Entity 5.1)
- Constitution: `.specify/memory/constitution.md` (Principle XV: Production-Grade Deployment - Nginx Ingress MANDATORY)
- Related ADRs: ADR-0014 (Infrastructure Stack), ADR-0016 (Autoscaling)
- Nginx Ingress Docs: https://kubernetes.github.io/ingress-nginx/
