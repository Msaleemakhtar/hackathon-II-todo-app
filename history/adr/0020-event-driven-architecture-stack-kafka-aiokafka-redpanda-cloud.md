# ADR-0020: Event-Driven Architecture Stack (Kafka, aiokafka, Redpanda Cloud)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-01
- **Feature:** 002-event-driven
- **Context:** Phase V requires event-driven architecture to support asynchronous task operations (reminders, recurring tasks). Need to select Kafka-compatible technology stack that integrates with existing FastAPI backend, provides reliable event delivery, and minimizes operational overhead for MVP.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement event-driven architecture using the following integrated stack:

- **Message Broker:** Redpanda Cloud (Serverless Free Tier)
- **Python Client Library:** aiokafka 0.11.0
- **Event Schema Validation:** Pydantic v2
- **Delivery Semantics:** At-least-once delivery with idempotent consumers
- **Authentication:** SASL/SCRAM-SHA-256 with TLS encryption
- **Topics:** 3 topics (task-events, task-reminders, task-recurrence) with configurable retention

## Consequences

### Positive

- **Zero operational overhead:** Redpanda Cloud manages broker infrastructure, ZooKeeper, and scaling - no cluster management required
- **Cost-effective for MVP:** Free tier provides 10GB storage, sufficient for <10,000 events/day
- **Async/await native:** aiokafka integrates seamlessly with FastAPI's async architecture without blocking event loop
- **Production-ready:** aiokafka has 4+ years active development, battle-tested in production workloads
- **Kafka compatibility:** Works with standard Kafka ecosystem (can migrate to self-hosted Kafka later if needed)
- **Type safety:** Pydantic v2 provides runtime validation for event schemas, preventing malformed messages
- **Lower complexity:** At-least-once delivery avoids distributed transaction coordinators required for exactly-once semantics
- **Security built-in:** SASL/SCRAM and TLS encryption mandatory in Redpanda Cloud (no insecure plaintext)

### Negative

- **Vendor dependency:** Tied to Redpanda Cloud (though Kafka-compatible APIs allow migration to Apache Kafka)
- **Free tier limits:** 10GB storage cap requires monitoring event volume growth
- **No exactly-once semantics:** Requires idempotent consumer logic to handle duplicate events (added complexity in business logic)
- **Async library complexity:** aiokafka requires careful lifecycle management (proper startup/shutdown with FastAPI lifespan events)
- **Single point of failure:** Free tier has single replication factor (no high availability in MVP)
- **Consumer coordination overhead:** Manual offset management required for fine-grained control

## Alternatives Considered

### Alternative Stack A: Self-Hosted Kafka (Strimzi Operator on Kubernetes)
- **Components:** Apache Kafka + Strimzi Operator + kafka-python (sync) or aiokafka (async)
- **Why rejected:**
  - High operational burden: Requires managing ZooKeeper, Kafka brokers, storage volumes, and cluster upgrades
  - Resource intensive: Minimum 3 ZooKeeper + 3 Kafka broker pods (not viable on minikube for MVP)
  - Complex setup: Strimzi CRDs, storage classes, network policies add significant configuration overhead
  - Maintenance cost: Need expertise in Kafka operations, monitoring, and troubleshooting

### Alternative Stack B: AWS Managed Streaming for Kafka (MSK)
- **Components:** AWS MSK + aiokafka + AWS IAM authentication
- **Why rejected:**
  - Vendor lock-in: Deep AWS integration makes migration difficult (IAM roles, VPCs, PrivateLink)
  - Higher cost: No free tier, minimum $0.21/hour (~$150/month for minimal cluster)
  - Overkill for MVP: Enterprise-grade features (multi-AZ, provisioned throughput) not needed
  - AWS-specific: Requires AWS account, networking setup (not aligned with current Kubernetes/Neon stack)

### Alternative Stack C: Redis Streams
- **Components:** Redis Streams + redis-py + custom consumer groups
- **Why rejected:**
  - Not Kafka-compatible: Different semantics (XREAD vs Kafka consumer groups)
  - Constitutional non-compliance: Constitution Principle XVI mandates Kafka/Redpanda for event-driven architecture
  - Less mature ecosystem: Fewer tools for monitoring, schema validation, and operations compared to Kafka
  - In-memory limitations: Persistence model differs from Kafka's log-based storage (data loss risk on restart)

### Alternative Stack D: Confluent Cloud (Kafka-as-a-Service)
- **Components:** Confluent Cloud + aiokafka + Confluent Schema Registry
- **Why rejected:**
  - Higher cost: Free tier only provides 30 days trial, then ~$1/hour minimum
  - Vendor lock-in: Confluent-specific features (ksqlDB, Connect) create migration friction
  - Over-engineered: Schema Registry, ksqlDB, and advanced connectors overkill for MVP
  - Similar to Redpanda Cloud: Same managed Kafka benefits, but higher cost and complexity

## References

- Feature Spec: [specs/002-event-driven/spec.md](../../specs/002-event-driven/spec.md)
- Implementation Plan: [specs/002-event-driven/plan.md](../../specs/002-event-driven/plan.md)
- Research Doc: [specs/002-event-driven/research.md](../../specs/002-event-driven/research.md) (Section 1: aiokafka, Section 2: Redpanda Cloud)
- Related ADRs: None (first event-driven architecture ADR)
- Constitution: `.specify/memory/constitution.md` (Principle XVI: Event-Driven Architecture)
