# ADR-0026: Dapr Component Configuration with Kubernetes Secrets

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-15
- **Feature:** 004-dapr-integration
- **Context:** Dapr components require secure configuration of sensitive data (Kafka credentials, database connection strings). Need to establish consistent pattern for managing secrets in Kubernetes environment that follows security best practices and enables environment-specific configurations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will configure Dapr components using Kubernetes Secrets with `secretKeyRef` for all sensitive data:

**Component Configuration Pattern:**
```yaml
# kubernetes/dapr-components/pubsub-kafka.yaml
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
      value: "bootstrap.redpanda.cloud:9092"
    - name: authType
      value: "sasl"
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: enableIdempotence
      value: "true"
    - name: acks
      value: "all"
  scopes:
    - backend
    - notification-service
    - email-delivery-service
    - recurring-task-service
```

**Secret Creation Pattern:**
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username="${KAFKA_SASL_USERNAME}" \
  --from-literal=password="${KAFKA_SASL_PASSWORD}" \
  -n todo-phasev
```

## Consequences

### Positive

- **Security:** Credentials not stored in Git or plain YAML files
- **Best Practice:** Follows Kubernetes security recommendations for secret management
- **Environment Flexibility:** Different secrets per environment (dev, staging, prod)
- **Rotation Support:** Secrets can be updated without changing component YAML
- **Access Control:** Kubernetes RBAC controls who can access secrets
- **Audit Trail:** Secret access can be logged and monitored
- **Compliance:** Helps meet security compliance requirements

### Negative

- **Operational Overhead:** Requires manual secret creation in each environment
- **Deployment Complexity:** Additional step to create secrets before deploying components
- **Limited Encryption:** Kubernetes secrets are base64 encoded but not encrypted at rest by default
- **Debugging Difficulty:** Harder to troubleshoot configuration issues when secrets are involved
- **Dependency Management:** Secrets must be created before components that reference them
- **Backup/Restore:** Secrets need special handling during backup and restore procedures

## Alternatives Considered

Alternative Configuration A: Inline credentials in YAML
- Approach: Store sensitive data directly in Dapr component YAML files
- Why rejected: Security risk, credentials in Git, violates 12-factor app principles

Alternative Configuration B: External secret management (HashiCorp Vault)
- Approach: Use external secret stores with Dapr's external secret stores component
- Why rejected: Adds infrastructure complexity beyond MVP scope, requires additional service

Alternative Configuration C: ConfigMap for non-sensitive data
- Approach: Use ConfigMaps for non-sensitive config, but this doesn't address the core issue of secret management
- Why rejected: Doesn't solve the problem of sensitive data management

## References

- Feature Spec: [specs/004-dapr-integration/spec.md](../../specs/004-dapr-integration/spec.md)
- Implementation Plan: [specs/004-dapr-integration/plan.md](../../specs/004-dapr-integration/plan.md)
- Research Doc: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Section 3: Component Configuration)
- Related ADRs: ADR-0014 (Phase IV Infrastructure Stack) - builds on Kubernetes foundation
- Evaluator Evidence: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Section 3)
