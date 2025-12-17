# ADR-0012: Phase III Technology Stack: ChatKit, FastAPI, UV, and Bun

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-17
- **Feature:** 002-ai-chat-service-integration
- **Context:** Phase III requires full-stack conversational task management. Need to select frontend chat UI framework, backend web framework, and package managers that work together for rapid development and constitutional compliance.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Technology stack affects development speed, maintenance, scalability
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - React Admin, custom chat UI, different package managers
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects entire Phase III codebase, developer experience, deployment
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **OpenAI ChatKit** (Managed ChatKit Starter template) for frontend, **FastAPI** for backend, **UV** for Python package management, and **Bun** for JavaScript package management.

**Frontend Stack**:
- **Chat UI**: OpenAI ChatKit (pre-built conversational interface)
- **Template**: Managed ChatKit Starter (https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit)
- **Framework**: Next.js (included in template)
- **Authentication**: Better Auth integration
- **Package Manager**: Bun (`bun add <package>`)

**Backend Stack**:
- **Web Framework**: FastAPI (async Python framework)
- **ORM**: SQLModel (SQLAlchemy + Pydantic integration)
- **Database Driver**: asyncpg (async PostgreSQL)
- **Migrations**: Alembic
- **Package Manager**: UV (`uv add <package>`)

**Rationale for Integrated Stack**:
- ChatKit + FastAPI = Pre-built chat UI + flexible async backend
- UV + Bun = Fast dependency resolution on both sides
- Better Auth spans both frontend and backend for unified auth
- SQLModel provides type-safe ORM matching Pydantic validation

## Consequences

### Positive

- **Constitutional Compliance**: Principle VI mandates ChatKit; Tech Constraints mandate UV and Bun
- **Rapid Development**: ChatKit eliminates custom chat UI implementation (weeks of work saved)
- **Best Practices**: Managed ChatKit Starter includes auth, message display, loading states, error handling
- **Type Safety**: FastAPI + SQLModel + ChatKit all use TypeScript/Python type systems
- **Performance**: UV (Rust-based) and Bun (Zig-based) provide fast dependency resolution
- **Async First**: FastAPI async handlers match database async operations (no blocking)
- **Domain Security**: ChatKit domain allowlist configured in OpenAI platform prevents unauthorized domains
- **Developer Experience**: Hot reload, fast installs, integrated tooling

### Negative

- **ChatKit Vendor Lock-in**: Switching chat UI requires rewriting frontend
- **OpenAI Platform Dependency**: ChatKit requires OpenAI platform account and domain configuration
- **Learning Curve**: Developers need to learn ChatKit API and configuration
- **UV/Bun Adoption**: Newer package managers may have less community support than pip/npm
- **Template Customization**: Managed ChatKit Starter requires understanding template structure before customization
- **ChatKit Limitations**: May not support all custom UI features (e.g., custom message rendering)

## Alternatives Considered

**Alternative 1: Custom React Chat UI + FastAPI**
- **Pros**: Full UI control, no vendor lock-in, standard React patterns
- **Cons**: Weeks of implementation time, need to build message display, loading states, error handling, websockets
- **Rejected Because**: Violates Principle VI requiring ChatKit; development time prohibitive

**Alternative 2: React Admin Dashboard + FastAPI**
- **Pros**: Full-featured admin UI, form generation, data grids
- **Cons**: Not designed for conversational interfaces, poor chat UX, violates ChatKit requirement
- **Rejected Because**: Constitutional mandate for ChatKit

**Alternative 3: ChatKit + Django (with pip/npm)**
- **Pros**: Mature Django ecosystem, simpler ORM
- **Cons**: Violates UV/Bun constitutional requirement, Django synchronous by default (poor async support), heavier framework
- **Rejected Because**: Constitutional mandate for UV and Bun; FastAPI preferred for async

**Alternative 4: ChatKit + Next.js API Routes (No Separate Backend)**
- **Pros**: Single deployment, simpler architecture, Next.js handles both frontend and backend
- **Cons**: Cannot use MCP Python SDK (JavaScript only), violates FastAPI requirement, poor type safety for database operations
- **Rejected Because**: MCP Python SDK required; FastAPI + SQLModel provides better backend type safety

## References

- Feature Spec: `specs/sphaseIII/002-ai-chat-service-integration/spec.md`
- Research Document: `specs/sphaseIII/002-ai-chat-service-integration/research.md` (Section 4, 10)
- ChatKit Documentation: https://platform.openai.com/docs/guides/chatkit
- Managed ChatKit Starter: https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit
- Constitution: `.specify/memory/constitution.md` (Principle VI: ChatKit; Tech Constraints: UV, Bun)
- Related ADRs: ADR-0010 (AI Service), ADR-0014 (Better Auth Integration)
