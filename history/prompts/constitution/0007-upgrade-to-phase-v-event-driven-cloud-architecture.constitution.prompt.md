---
id: 0007
title: Upgrade to Phase V Event-Driven Cloud Architecture
stage: constitution
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: Msaleemakhtar
command: /sp.constitution
labels: ["constitution", "governance", "phase-v", "kafka", "dapr", "oracle-cloud", "event-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitutional document; validation via 4 self-checks)
---

## Prompt

Update the project constitution at `.specify/memory/constitution.md` for Phase V.

**Context:**
- Phase IV has been completed and marked as COMPLETE
- Phase IV codebase has been copied into `/phaseV/` directory
- Phase V is now the ACTIVE phase
- Current constitution version: 2.5.0
- Target constitution version: 3.0.0 (MAJOR version bump due to new principles)

**Phase V Requirements (from hackathon documentation and implementation plan):**

**Part A: Advanced Features + Event-Driven Architecture**
1. Advanced task fields: priority (low/medium/high/urgent), due_date, category_id, recurrence_rule, reminder_sent
2. New entities: Categories, Tags (tags_phasev), TaskTag junction table
3. Full-text search with PostgreSQL tsvector + GIN indexes
4. Multi-criteria filtering (priority, category, tag, due dates)
5. 17 MCP tools total (5 enhanced + 12 new: search, categories, tags, reminders)
6. Kafka/Redpanda Cloud event streaming (3 topics: task-events, reminders, task-updates)
7. Event-driven services: Notification Service, Recurring Task Service
8. Kafka client: aiokafka for async Python

**Part B: Dapr Integration**
1. Dapr v1.12+ distributed application runtime
2. Dapr components: Pub/Sub (Kafka), State (PostgreSQL), Secrets (Kubernetes), Jobs API
3. Infrastructure abstraction (no direct Kafka/PostgreSQL clients in app code)
4. Dapr sidecar injection with annotations

**Part C: Production Cloud Deployment**
1. Oracle Cloud OKE (always free tier: 4 OCPU, 24GB RAM)
2. Namespace: todo-phasev
3. HTTPS with cert-manager + Let's Encrypt
4. GitHub Actions CI/CD pipeline (ci-phase-v.yml, deploy-production.yml)
5. Monitoring: Prometheus + Grafana (kube-prometheus-stack)
6. Security: NetworkPolicies, RBAC, Pod Security Standards
7. Backup: Velero for Kubernetes resources
8. Container Registry: Oracle Container Registry (OCIR)

**Required Constitution Changes:**

1. **Mission Statement**: Update Phase IV from ACTIVE -> COMPLETE, add Phase V as ACTIVE
2. **Repository Structure (Principle II)**: Add `/phaseV/` directory with structure (kafka/, dapr-components/, kubernetes/)
3. **NEW Principle XVI: Event-Driven Architecture with Kafka (Phase V Only)**
   - Kafka/Redpanda Cloud integration
   - Event topics (task-events, reminders, task-updates)
   - Event producers in MCP tools
   - Event consumer services (Notification, Recurring Task)
4. **NEW Principle XVII: Distributed Application Runtime with Dapr (Phase V Only)**
   - Dapr installation and components
   - Pub/Sub, State, Secrets, Jobs API
   - Infrastructure abstraction
5. **NEW Principle XVIII: Production Cloud Deployment (Phase V Only)**
   - Oracle Cloud OKE
   - CI/CD with GitHub Actions
   - Monitoring (Prometheus/Grafana)
   - Security hardening
6. **Feature Scope (Principle X)**: Rename to "Feature Scope Evolution", add Phase V features (14-39 tools)
7. **Data Model**: Add Phase V models (enhanced tasks_phaseiii, categories, tags_phasev, task_tags)
8. **Technology Constraints**: Add Phase V stack (Redpanda, Dapr, OKE, cert-manager, GitHub Actions)
9. **Success Criteria**: Add Phase V completion criteria for Parts A, B, C
10. **Requirement-to-Rule Mapping**: Add 25 Phase V requirements (FR-P5-001 to TC-P5-006)

**Version Information:**
- Current: 2.5.0
- New: 3.0.0
- Ratified: 2025-12-04 (original)
- Last Amended: 2025-12-30 (today)
- Bump Type: MAJOR (3 new principles added - backward incompatible governance expansion)

**Additional Context:**
- See `/home/salim/Desktop/hackathon-II-todo-app/docs/PHASE_V_IMPLEMENTATION_PLAN.md` for full implementation plan
- See `/home/salim/Desktop/hackathon-II-todo-app/docs/Hackathon II - Todo Spec-Driven Development.md` for Phase V hackathon requirements (lines 908-1107)

Please update the constitution following the constitution-writer protocol, including:
1. All 3 new principles (XVI, XVII, XVIII)
2. Updated mission statement and repository structure
3. Extended data models, feature scope, technology constraints
4. Complete requirement-to-rule mapping for Phase V
5. Sync impact report as HTML comment
6. PHR creation (MANDATORY)

The constitution is a complete document (not a template with placeholders). Update the existing content with Phase V governance rules.

## Response snapshot

Successfully upgraded the project constitution from v2.5.0 to v3.0.0 for Phase V. This is a MAJOR version bump due to three new governance principles being added.

**Key Changes Made:**

1. **Mission Statement**: Updated Phase III and Phase IV status to COMPLETED, added Phase V as ACTIVE with description of event-driven architecture, Dapr, and Oracle Cloud OKE deployment.

2. **Three New Principles Added:**
   - **Principle XVI: Event-Driven Architecture with Kafka** - Covers Redpanda Cloud setup, 3 Kafka topics (task-events, reminders, task-updates), event schemas, producer/consumer patterns, aiokafka integration, and Notification/Recurring Task consumer services.
   - **Principle XVII: Distributed Application Runtime with Dapr** - Covers Dapr v1.12+ installation, 4 components (Pub/Sub, State Store, Secrets, Jobs API), sidecar injection, infrastructure abstraction, and Dapr HTTP API usage.
   - **Principle XVIII: Production Cloud Deployment** - Covers Oracle Cloud OKE setup (always free tier), cert-manager/Let's Encrypt HTTPS, GitHub Actions CI/CD, Prometheus/Grafana monitoring, security hardening (NetworkPolicies, RBAC, Pod Security), and Velero backups.

3. **Repository Structure**: Added Phase V directory structure with kafka/, dapr-components/, kubernetes/ subdirectories, new services (notification_service.py, recurring_task_service.py, search_service.py), and CI/CD workflows.

4. **Feature Scope Evolution**: Renamed from "Feature Scope" and added Phase V MCP tools (17 total: 5 enhanced + 12 new including search, categories, tags, reminders, overdue/upcoming tasks).

5. **Data Models**: Added Phase V enhanced tasks_phaseiii table (priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector), categories table, tags_phasev table, and task_tags junction table. Added GIN index for full-text search.

6. **Success Criteria**: Added comprehensive Phase V completion criteria organized by Part A (Advanced Features), Part B (Dapr Integration), and Part C (Production Cloud Deployment) with 70+ checklist items.

7. **Requirement-to-Rule Mapping**: Added 34 Phase V requirements (FR-P5-001 through FR-P5-023, QR-P5-001 through QR-P5-002, SR-P5-001 through SR-P5-003, TC-P5-001 through TC-P5-006) with full traceability.

8. **Technology Constraints**: Added Phase V mandatory stack including Redpanda Cloud, Dapr v1.12+, Oracle Cloud OKE, cert-manager, GitHub Actions, Prometheus/Grafana, and OCIR.

9. **Constitutional Self-Checks**: All 4 checks pass (Alignment, Coverage, Conflict, Completeness).

## Outcome

- Impact: Constitution upgraded from v2.5.0 to v3.0.0, adding 3 new principles (XVI, XVII, XVIII), Phase V governance rules for event-driven architecture, Dapr distributed runtime, and Oracle Cloud production deployment. 34 new requirements mapped to constitutional rules. Constitution now governs 5 phases with comprehensive Phase V success criteria.
- Tests: None (constitutional document; validation via 4 self-checks: Alignment PASS, Coverage PASS, Conflict PASS, Completeness PASS)
- Files: Modified .specify/memory/constitution.md (complete rewrite, ~2400 lines)
- Next prompts: Create specs in /specs/sphaseV/ (001-advanced-features, 002-dapr-integration, 003-cloud-deployment); Setup Redpanda Cloud cluster; Configure Oracle Cloud OKE; Create CI/CD workflows in .github/workflows/
- Reflection: MAJOR version bump was appropriate due to three new principles and backward-incompatible governance expansion. The three-part structure (Part A, B, C) from the hackathon requirements mapped cleanly to separate principles (XVI, XVII, XVIII), making the constitution highly navigable. Dapr's infrastructure abstraction (Principle XVII) complements but doesn't conflict with Kafka integration (Principle XVI) since Dapr abstracts the underlying Kafka implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update completed successfully with all self-checks passing.
- Graders run and results (PASS/FAIL): Alignment PASS, Coverage PASS, Conflict-Free PASS, Completeness PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider adding visual architecture diagrams to Principles XVI, XVII, XVIII similar to Phase IV's service architecture ASCII diagrams already included.
