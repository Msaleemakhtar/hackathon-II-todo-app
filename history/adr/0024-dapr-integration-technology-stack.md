# ADR-0024: Dapr Integration Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-15
- **Feature:** 004-dapr-integration
- **Context:** Phase V requires migrating from direct aiokafka producers/consumers to Dapr's infrastructure abstraction layer to achieve portability across message brokers (Kafka, Redis Streams, RabbitMQ) without code changes. This decision encompasses the entire Dapr technology stack including runtime, client libraries, and component configurations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement Dapr integration using the following integrated stack:

- **Dapr Runtime:** Dapr v1.12.5 (latest stable)
- **Python Client Library:** httpx with custom Dapr wrapper
- **Pub/Sub Component:** Kafka (Redpanda Cloud) via Dapr Pub/Sub API
- **State Store Component:** PostgreSQL State Store v2
- **Secrets Store Component:** Kubernetes Secrets
- **Jobs API:** Alpha implementation for scheduled notification jobs
- **Infrastructure:** Kubernetes with Dapr sidecar injection

## Consequences

### Positive

- **Infrastructure Abstraction:** Application code no longer tied to specific message broker implementation (can switch from Kafka to Redis/RabbitMQ without code changes)
- **Declarative Infrastructure:** Components configured via YAML rather than code, enabling infrastructure as code practices
- **Built-in Features:** Dapr provides tracing, metrics, and health checks out-of-the-box
- **Scalability:** Sidecar pattern enables horizontal scaling with guaranteed single job execution across replicas
- **Security:** Built-in service-to-service authentication and secret management
- **Developer Productivity:** Reduced boilerplate code for common distributed system patterns
- **Observability:** Centralized monitoring of distributed system interactions

### Negative

- **Additional Complexity:** Introduces sidecar containers and additional moving parts to the system
- **Learning Curve:** Team needs to understand Dapr concepts, APIs, and debugging patterns
- **Performance Overhead:** Network hop between application and Dapr sidecar may increase latency slightly
- **Dependency Risk:** Adds dependency on Dapr runtime stability and release cycle
- **Debugging Challenges:** More complex to troubleshoot issues across application and sidecar boundary
- **Resource Usage:** Each pod now includes a Dapr sidecar, increasing overall resource consumption
- **Alpha Features:** Jobs API is still in alpha, potentially unstable for production use

## Alternatives Considered

Alternative Stack A: Continue with direct aiokafka implementation
- Components: aiokafka 0.11.0, direct PostgreSQL connections, custom polling loops
- Why rejected: Creates vendor lock-in to Kafka, requires custom infrastructure management, no abstraction layer for future flexibility

Alternative Stack B: Service Mesh (Istio/Linkerd) + Custom Infrastructure Abstraction
- Components: Istio/Linkerd for service mesh, custom abstraction layer for pub/sub, state management
- Why rejected: Significantly more complex setup, steeper learning curve, more operational overhead than Dapr's simpler abstraction model

Alternative Stack C: Cloud-Native Event Grid (AWS EventBridge, Azure Event Grid)
- Components: Cloud-specific event grid services, cloud-native SDKs
- Why rejected: Creates vendor lock-in to specific cloud providers, not compatible with current Kubernetes/Neon stack, increases cloud migration complexity

## References

- Feature Spec: [specs/004-dapr-integration/spec.md](../../specs/004-dapr-integration/spec.md)
- Implementation Plan: [specs/004-dapr-integration/plan.md](../../specs/004-dapr-integration/plan.md)
- Research Doc: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Section 1: Dapr Runtime, Section 2: HTTP Client)
- Related ADRs: ADR-0020 (Event-Driven Architecture Stack) - this ADR supersedes the direct Kafka client portion
- Evaluator Evidence: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Sections 1-3)
