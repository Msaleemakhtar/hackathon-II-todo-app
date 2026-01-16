# ADR-0025: Migration Strategy from aiokafka to Dapr

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-15
- **Feature:** 004-dapr-integration
- **Context:** Need to migrate existing aiokafka-based event-driven architecture to Dapr without disrupting production services. The migration must be safe, reversible, and minimize risk to existing functionality while enabling gradual adoption of Dapr capabilities.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement a phased migration strategy with feature flags:

**Phase A: Add Dapr Layer (Non-Breaking)**
1. Install Dapr on Kubernetes
2. Deploy Dapr components (without using them)
3. Add `app/dapr/` module with HTTP client wrappers
4. Deploy with feature flag: `USE_DAPR=false` (default)

**Phase B: Migrate Producers (Low Risk)**
1. Update MCP tools to use Dapr client if `USE_DAPR=true`
2. Test with single replica in staging
3. Enable `USE_DAPR=true` in production
4. Monitor event flow for 24 hours

**Phase C: Migrate Consumers (Medium Risk)**
1. Update notification service to use Dapr subscription
2. Update email delivery service to use Dapr subscription
3. Deploy with Dapr sidecar annotations
4. Verify consumer lag and event processing

**Phase D: Remove aiokafka (Final)**
1. Remove `aiokafka` from requirements.txt
2. Delete `app/kafka/` module
3. Set `USE_DAPR=true` permanently
4. Archive pre-migration Docker images

## Consequences

### Positive

- **Risk Mitigation:** Gradual migration reduces chance of catastrophic failure
- **Reversibility:** Feature flags allow quick rollback if issues arise
- **Monitoring:** Each phase can be validated independently before proceeding
- **Team Confidence:** Incremental changes easier to understand and debug
- **Business Continuity:** Services remain available throughout migration
- **Performance Validation:** Each phase allows performance comparison with baseline

### Negative

- **Technical Debt:** Temporary dual infrastructure (both aiokafka and Dapr paths)
- **Complexity:** Feature flags and conditional code paths increase cognitive load
- **Extended Timeline:** Phased approach takes longer than big-bang migration
- **Testing Overhead:** Each phase requires separate validation and monitoring
- **Resource Usage:** Temporary duplication of infrastructure components
- **Maintenance Burden:** Supporting both systems during transition period

## Alternatives Considered

Alternative Strategy A: Big-bang migration
- Approach: Migrate entire system in single deployment
- Why rejected: Too risky for production system, no fallback mechanism, difficult to isolate issues

Alternative Strategy B: Blue-green deployment
- Approach: Deploy parallel Dapr-based system alongside existing system
- Why rejected: Requires duplicate infrastructure resources, complex data synchronization, significant operational overhead

Alternative Strategy C: Canary deployment with traffic splitting
- Approach: Route subset of events through Dapr while keeping aiokafka for others
- Why rejected: Complex to implement with event-driven architecture, potential for inconsistent state

## References

- Feature Spec: [specs/004-dapr-integration/spec.md](../../specs/004-dapr-integration/spec.md)
- Implementation Plan: [specs/004-dapr-integration/plan.md](../../specs/004-dapr-integration/plan.md)
- Research Doc: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Section 6: Migration Strategy)
- Related ADRs: ADR-0020 (Event-Driven Architecture Stack) - this ADR describes migration away from that approach
- Evaluator Evidence: [specs/004-dapr-integration/research.md](../../specs/004-dapr-integration/research.md) (Section 6)
