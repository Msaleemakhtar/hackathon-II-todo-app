# ADR-0011: MCP Server Architecture: Stateless Tools with Database-Backed State

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-17
- **Feature:** 002-ai-chat-service-integration
- **Context:** Phase III requires MCP (Model Context Protocol) server with 5 task operation tools. Need to decide on tool design pattern (stateful vs stateless), state persistence strategy, and multi-user data isolation approach.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Affects scalability, data integrity, multi-tenancy
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Stateful vs stateless, in-memory vs database
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects MCP server, database, agent integration, scalability
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement MCP server with **5 stateless tools** using the **official Python MCP SDK**, with **database-backed state persistence** and **user-scoped data isolation**.

**Components**:
- **MCP Framework**: Official Python MCP SDK (`mcp` package)
- **Tool Count**: 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- **Tool Design**: Stateless - no in-memory state between invocations
- **State Persistence**: PostgreSQL via SQLModel ORM
- **Data Isolation**: All tools validate `user_id` parameter; queries scoped to user
- **Location**: `phaseIII/backend/app/mcp/` (server.py, tools.py)
- **Integration**: Tools invoked by OpenAI Agents SDK via MCP protocol

**Tool Invocation Flow**:
```
AI Agent → OpenAI Agents SDK → MCP Server → Tool Function (stateless)
                                              ↓
                                     Database Session (injected)
                                              ↓
                                     User-scoped Query → Result
```

## Consequences

### Positive

- **Constitutional Compliance**: Principle XI mandates MCP architecture with 5 tools
- **Horizontal Scalability**: Stateless tools enable multi-instance deployment without session affinity
- **Data Integrity**: Database persistence ensures task state survives server restarts
- **Multi-User Isolation**: User-scoped queries prevent cross-user data leaks
- **Testability**: Stateless functions easy to unit test with mocked database
- **Official SDK**: Using official MCP Python SDK ensures protocol compliance
- **Tool Independence**: Each tool execution is atomic; no shared state to corrupt
- **Simple Deployment**: No distributed state management (Redis, etc.) required

### Negative

- **Database Dependency**: Every tool call requires database round-trip (adds latency)
- **No Caching**: Stateless design prohibits in-memory caching (could mitigate with Redis later)
- **Repetitive Queries**: List operations may query database multiple times in single conversation
- **Testing Complexity**: Integration tests require database setup/teardown
- **Performance Ceiling**: Database latency becomes bottleneck (mitigated by indexes)

## Alternatives Considered

**Alternative 1: Stateful MCP Server with In-Memory State**
- **Pros**: Faster tool execution (no database queries), simple implementation
- **Cons**: Violates Principle XI requirement for stateless tools, cannot scale horizontally, state lost on restart, multi-user isolation complex
- **Rejected Because**: Constitutional mandate for stateless design; scalability concerns

**Alternative 2: Stateless Tools with Redis Caching**
- **Pros**: Faster repeated queries, stateless tools maintained, horizontal scaling possible
- **Cons**: Added infrastructure complexity, cache invalidation logic required, higher cost
- **Rejected Because**: Over-engineering for Phase III; can add Redis in Phase IV if needed

**Alternative 3: Custom MCP Implementation (Not Official SDK)**
- **Pros**: Full control over protocol, can optimize for specific use case
- **Cons**: Protocol compliance risk, maintenance burden, missing SDK features
- **Rejected Because**: Official SDK preferred for protocol correctness and future updates

**Alternative 4: Fewer Tools with Multi-Purpose Operations**
- **Pros**: Simpler MCP server, fewer tool definitions
- **Cons**: Violates Principle XI requirement for 5 tools, AI intent mapping becomes ambiguous
- **Rejected Because**: Constitutional mandate for exactly 5 tools

## References

- Feature Spec: `specs/sphaseIII/002-ai-chat-service-integration/spec.md`
- Research Document: `specs/sphaseIII/002-ai-chat-service-integration/research.md` (Section 3)
- MCP Tools Contract: `specs/sphaseIII/002-ai-chat-service-integration/contracts/mcp-tools.yaml`
- Data Model: `specs/sphaseIII/002-ai-chat-service-integration/data-model.md`
- Constitution: `.specify/memory/constitution.md` (Principle XI: MCP Architecture)
- Related ADRs: ADR-0010 (AI Service Architecture), ADR-0013 (Data Architecture)
