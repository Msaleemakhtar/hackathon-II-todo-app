---
id: 003
title: ADR Review for Phase III AI Chat Service
stage: plan
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 002-ai-chat-service-integration
branch: 002-ai-chat-service-integration
user: salim
command: /sp.adr
labels: ["architecture", "adr", "decision-records", "phase-iii"]
links:
  spec: specs/sphaseIII/002-ai-chat-service-integration/spec.md
  ticket: null
  adr: history/adr/0010-ai-service-architecture-gemini-with-openai-agents-sdk-integration.md
  pr: null
files:
  - history/adr/0010-ai-service-architecture-gemini-with-openai-agents-sdk-integration.md
  - history/adr/0011-mcp-server-architecture-stateless-tools-with-database-backed-state.md
  - history/adr/0012-phase-iii-technology-stack-chatkit-fastapi-uv-and-bun.md
  - history/adr/0013-phase-iii-data-architecture-separate-tables-and-database-isolation.md
tests:
  - null
---

## Prompt

follow this specs/sphaseIII/002-ai-chat-service-integration

## Response snapshot

Analyzed planning artifacts (plan.md, research.md, data-model.md, contracts/) and identified 4 architecturally significant decision clusters requiring ADR documentation:

**Created ADRs**:
1. **ADR-0010**: AI Service Architecture - Gemini with OpenAI Agents SDK Integration
   - Decision: Use Gemini (gemini-1.5-flash) integrated through OpenAI Agents SDK via custom adapter
   - Alternatives: GPT-4 (cost), Claude (not required), local models (quality), custom agent framework (constitutional violation)
   - Impact: AI service choice affects cost, latency, capabilities; adapter pattern provides flexibility

2. **ADR-0011**: MCP Server Architecture - Stateless Tools with Database-Backed State
   - Decision: 5 stateless MCP tools using official Python SDK with PostgreSQL persistence and user-scoped queries
   - Alternatives: Stateful tools (scalability), Redis caching (complexity), custom MCP (risk), fewer tools (constitutional violation)
   - Impact: Enables horizontal scaling, data integrity, multi-user isolation; database latency becomes bottleneck

3. **ADR-0012**: Phase III Technology Stack - ChatKit, FastAPI, UV, and Bun
   - Decision: OpenAI ChatKit (Managed Starter) + FastAPI + UV (Python) + Bun (JS)
   - Alternatives: Custom React UI (time), React Admin (poor chat UX), Django (async issues), Next.js API routes (no MCP Python SDK)
   - Impact: Rapid development with pre-built chat UI; ChatKit vendor lock-in; fast package managers

4. **ADR-0013**: Phase III Data Architecture - Separate Tables and Database Isolation
   - Decision: Separate tables (tasks_phaseiii, conversations, messages) with independent Alembic migrations
   - Alternatives: Reuse Phase II tables (coupling), namespaced tables (incomplete isolation), separate databases (over-isolation), views (coupling remains)
   - Impact: Phase separation compliance, independent evolution, data integrity; data duplication and migration complexity

**Referenced Existing ADRs**:
- ADR-0007: Better Auth with JWT Integration (Phase II architecture reused in Phase III)
- ADR-0009: Data Isolation Architecture (Phase II patterns apply to Phase III user-scoped queries)

**No Conflicts Detected**: All new ADRs complement existing architecture decisions

## Outcome

- ✅ Impact: 4 new ADRs document architectural decisions for Phase III conversational AI implementation
- 🧪 Tests: No tests - documentation artifact
- 📁 Files: 4 ADR files created in history/adr/
- 🔁 Next prompts: /sp.tasks to generate implementation tasks based on plan and ADRs
- 🧠 Reflection: ADR clustering worked well - grouped Gemini + OpenAI SDK, grouped ChatKit + FastAPI + UV/Bun. Identified existing ADRs (Better Auth, Data Isolation) apply to Phase III, avoiding duplication.

## Evaluation notes (flywheel)

- Failure modes observed: None - all ADRs passed significance test (impact, alternatives, scope)
- Graders run and results (PASS/FAIL):
  - Clustered decisions (not atomic): PASS
  - Explicit alternatives listed: PASS
  - Pros/cons for chosen and alternatives: PASS
  - Concise but detailed: PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding migration path section to ADR-0013 for Phase II to Phase III data migration strategy
