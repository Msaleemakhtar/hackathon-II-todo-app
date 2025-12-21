# Implementation Plan: Fix ChatKit Integration and Better-Auth Backend

**Branch**: `003-fix-chatkit-auth` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fix-chatkit-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix critical Phase III ChatKit integration and Better-Auth backend implementation issues blocking the hackathon demonstration. This includes resolving TypeScript compilation errors due to missing type definitions, fixing broken JWT token retrieval for ChatKit authentication, and adding complete Better-Auth database schema for proper multi-user authentication and data isolation.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x with Next.js 16.0.8, React 19.2.1
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: @openai/chatkit-react ^1.4.0, better-auth ^1.4.6, Next.js 16, bun (package manager)
- Backend: FastAPI, better-auth (via shared secret JWT validation), python-jose, SQLModel, asyncpg, uv (package manager)

**Storage**: Neon Serverless PostgreSQL (shared database instance with Phase II)

**Testing**:
- Frontend: Not specified (vitest/jest recommended)
- Backend: pytest with pytest-asyncio

**Target Platform**: Web application (browser + server)

**Project Type**: Full-stack web application (phaseIII/frontend + phaseIII/backend)

**Performance Goals**:
- Chat response time: <5s p95 (including AI model latency)
- Frontend build: <30s compilation time
- Authentication: <2 minutes for registration/login flow

**Constraints**:
- MUST use OpenAI ChatKit (@openai/chatkit-react) for chat interface
- MUST use Better Auth for authentication (email/password only, no OAuth)
- MUST maintain complete separation from Phase II codebase (zero imports)
- MUST use separate database tables (tasks_phaseiii, conversations, messages)
- TypeScript strict mode compilation required
- ChatKit useChatKit hook API compatibility required

**Scale/Scope**:
- MVP demonstration for hackathon
- Support 50+ concurrent users
- Conversation history: up to 100 messages per conversation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitutional Requirements

| Rule | Requirement | Status | Evidence/Notes |
|------|-------------|--------|----------------|
| **Principle I** | Spec-Driven Development | ✅ PASS | This plan is generated from spec.md in /specs/003-fix-chatkit-auth/ |
| **Principle II** | Repository Structure - Phase Separation | ✅ PASS | All work confined to phaseIII/ directory, zero imports from phaseII or phaseI |
| **Principle III** | Persistent & Relational State | ✅ PASS | Using Neon PostgreSQL with SQLModel, migrations exist (001_initial_schema.py) |
| **Principle IV** | JWT Security | ⚠️ PARTIAL | Better Auth server-side configured but JWT retrieval broken on frontend; needs fix |
| **Principle V** | Backend Architecture | ✅ PASS | FastAPI with routers in app/routers/, OpenAPI docs enabled |
| **Principle VI** | Frontend Architecture | ⚠️ PARTIAL | ChatKit integration exists but TypeScript errors block build; missing type definitions |
| **Principle VII** | Testing Standards | ⚠️ NEEDS WORK | Backend pytest configured, frontend tests not yet implemented |
| **Principle XI** | MCP Server Architecture | ✅ PASS | MCP tools defined in app/mcp/tools.py, stateless design |
| **Principle XII** | OpenAI Agents SDK | ✅ PASS | Agent service exists using openai-agents ^0.6.3 |
| **Principle XIII** | Conversational AI | ✅ PASS | Stateless architecture, conversation persistence via database |
| **TC-P3-001** | OpenAI ChatKit Required | ⚠️ PARTIAL | ChatKit installed and used but broken due to type errors |
| **TC-P3-004** | UV Package Manager (backend) | ✅ PASS | pyproject.toml configured for uv |
| **TC-P3-005** | Bun Package Manager (frontend) | ✅ PASS | package.json uses bun lockfile |
| **FR-P3-008** | Better Auth Database Tables | ❌ FAIL | Missing Better Auth tables (user, session, account, verification) |

### Gate Status (Pre-Design): ⚠️ CONDITIONAL PASS WITH REQUIRED FIXES

**Blocking Issues** (Must fix before implementation):
1. **Missing Better Auth Database Schema**: No Better Auth tables exist in database (user, session, account, verification). These are required for multi-user authentication per Principle IV.
2. **TypeScript Build Failure**: Frontend cannot compile due to ChatKit type mismatch in useChatKit hook usage. Blocks all frontend development.
3. **JWT Token Retrieval Broken**: Frontend cannot extract JWT from Better Auth session, causing "Authentication Token Missing" error. Blocks chat functionality.

**Non-Blocking Issues** (Can defer):
4. Frontend test suite not implemented (acceptable for this fix - testing not in scope)

**Justification**: This is a **bug fix feature**, not new development. The issues existed from incomplete Phase III initial implementation. Fixing these issues will bring the codebase into constitutional compliance.

---

### Gate Status (Post-Design): ✅ PASS - READY FOR IMPLEMENTATION

**Phase 1 Design Complete**:
- ✅ Research completed (all unknowns resolved) → research.md
- ✅ Data model documented (Better Auth schema + relationships) → data-model.md
- ✅ Type contracts defined (TypeScript definitions) → contracts/auth-types.ts
- ✅ Setup guide created (environment config + migration) → quickstart.md
- ✅ Agent context updated (Neon PostgreSQL documented)

**Constitutional Compliance Re-evaluation**:

| Rule | Status Change | Evidence |
|------|---------------|----------|
| **Principle IV** | ⚠️ PARTIAL → ✅ READY | JWT plugin configuration documented; migration ready |
| **Principle VI** | ⚠️ PARTIAL → ✅ READY | Type definitions created; ChatKit API usage corrected |
| **FR-P3-008** | ❌ FAIL → ✅ READY | Migration 003_better_auth_tables.py design complete |

**All blocking issues have documented solutions**. Implementation can proceed via `/sp.tasks` command.

**No architectural decisions requiring ADR** - All changes follow existing patterns (Better Auth integration, database migration, TypeScript types).

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-chatkit-auth/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── auth-types.ts    # TypeScript type definitions for ChatKit and Better Auth
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Full-stack web application (Phase III)

```text
phaseIII/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry
│   │   ├── config.py                 # Configuration and settings
│   │   ├── database.py               # Database connection and models
│   │   ├── dependencies/
│   │   │   └── auth.py               # JWT verification (NEEDS FIX: Better Auth integration)
│   │   ├── models/
│   │   │   ├── task.py               # Task model (tasks_phaseiii table)
│   │   │   ├── conversation.py       # Conversation model
│   │   │   └── message.py            # Message model
│   │   ├── routers/
│   │   │   ├── chat.py               # Chat endpoint
│   │   │   └── chatkit_adapter.py    # ChatKit adapter endpoint
│   │   ├── services/
│   │   │   ├── agent_service.py      # OpenAI Agents SDK integration
│   │   │   ├── task_service.py       # Task CRUD operations
│   │   │   ├── conversation_service.py
│   │   │   └── message_service.py
│   │   └── mcp/
│   │       ├── server.py             # MCP server manager
│   │       └── tools.py              # MCP tool implementations
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial_schema.py # Existing: tasks_phaseiii, conversations, messages
│   │       └── 003_better_auth_tables.py # TO CREATE: Better Auth tables
│   └── tests/
│       ├── test_mcp_tools.py
│       └── test_chat.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Home page
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── providers.tsx         # Context providers
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Login page
│   │   │   ├── signup/
│   │   │   │   └── page.tsx          # Signup page
│   │   │   ├── chat/
│   │   │   │   └── page.tsx          # NEEDS FIX: ChatKit integration, JWT retrieval
│   │   │   └── api/
│   │   │       ├── auth/
│   │   │       │   ├── [...all]/route.ts # Better Auth API routes
│   │   │       │   └── token/route.ts    # TO CREATE: JWT token endpoint
│   │   │       └── chatkit/
│   │   │           └── route.ts      # ChatKit proxy (if needed)
│   │   ├── lib/
│   │   │   ├── auth.ts               # Better Auth exports
│   │   │   ├── auth-client.ts        # NEEDS FIX: Better Auth client config
│   │   │   └── auth-server.ts        # NEEDS FIX: Better Auth server config
│   │   ├── types/                    # TO CREATE: Type definition directory
│   │   │   ├── auth.d.ts             # Better Auth session types
│   │   │   └── chatkit.d.ts          # ChatKit component types
│   │   └── contexts/
│   │       └── AuthContext.tsx       # Authentication context
│   └── package.json                  # Bun dependencies (has ChatKit, Better Auth)
└── docker-compose.yml                # Docker services configuration
```

**Key Files to Modify**:
1. `phaseIII/frontend/src/types/` (CREATE) - TypeScript type definitions
2. `phaseIII/frontend/src/app/chat/page.tsx` (FIX) - ChatKit useChatKit usage
3. `phaseIII/frontend/src/lib/auth-client.ts` (FIX) - Better Auth JWT plugin config
4. `phaseIII/frontend/src/lib/auth-server.ts` (FIX) - Better Auth JWT plugin config
5. `phaseIII/backend/alembic/versions/003_better_auth_tables.py` (CREATE) - Better Auth schema migration

## Complexity Tracking

**No constitutional violations** - This is a bug fix bringing existing implementation into compliance. No complexity justifications required.
