# Phase 0: Research & Technical Decisions

**Feature**: AI-Powered Conversational Task Management
**Branch**: `002-ai-chat-service-integration`
**Date**: 2025-12-17

## Research Summary

This document resolves all technical unknowns identified during planning and establishes the foundation for Phase 1 design.

---

## 1. AI Service Selection (Gemini)

### Decision
Use **Google Gemini** as the AI service for natural language processing.

### Rationale
- **Clarification**: User explicitly specified Gemini in spec clarifications (Session 2025-12-17)
- **Integration**: Works with OpenAI Agents SDK through adapter pattern
- **Cost**: Competitive pricing for conversational AI
- **Capabilities**: Strong natural language understanding for task management intents

### Alternatives Considered
- **OpenAI GPT-4**: Excellent NLU but higher cost; ruled out per user specification
- **Anthropic Claude**: Strong reasoning but not specified by user requirements
- **Local models**: Lower cost but insufficient quality for intent detection

### Implementation Notes
- Use Gemini API through `google-generativeai` Python package
- Configure model: `gemini-1.5-flash` for fast responses (<5s p95 requirement)
- Wrap Gemini in OpenAI-compatible interface for Agents SDK integration

---

## 2. OpenAI Agents SDK Integration Strategy

### Decision
Use **OpenAI Agents SDK** with custom Gemini adapter for agent orchestration and MCP tool invocation.

### Rationale
- **Constitutional Mandate**: Phase III constitution (Principle XII) requires OpenAI Agents SDK
- **Tool Invocation**: Provides standardized tool calling mechanism for MCP tools
- **Conversation Management**: Handles multi-turn conversation context
- **Architecture**: Enables stateless server design with database-backed state

### Integration Pattern
```
User Message → FastAPI Endpoint → Load Conversation History from DB
                                 ↓
                      Build Message Array (history + new)
                                 ↓
                      OpenAI Agents SDK + Gemini Adapter
                                 ↓
                      Agent Invokes MCP Tools (add_task, list_tasks, etc.)
                                 ↓
                      Store Messages in DB → Return Response
```

### Best Practices
- **Stateless Design**: No in-memory conversation state; all context from DB
- **Tool Descriptions**: Clear, actionable descriptions for each MCP tool
- **Error Handling**: Graceful fallbacks when Gemini API unavailable
- **Context Window**: Load last 20 messages for context (constitutional requirement)

---

## 3. MCP Server Architecture

### Decision
Implement MCP server with **5 stateless tools** using official Python SDK, with database-backed state persistence.

### Rationale
- **Constitutional Mandate**: Principle XI requires MCP architecture with 5 tools
- **Stateless Tools**: Each tool execution is independent; no in-memory state
- **Database State**: All task state persisted to `tasks_phaseiii` table
- **Horizontal Scalability**: Stateless design enables multi-instance deployment

### Tool Specifications

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `add_task` | Create new task | `user_id`, `title`, `description` (optional) | `task_id`, `status: "created"`, `title` |
| `list_tasks` | Retrieve tasks | `user_id`, `status` (optional: all/pending/completed) | List of tasks with id, title, description, completed |
| `complete_task` | Mark task done | `user_id`, `task_id` | `task_id`, `status: "completed"`, `title` |
| `delete_task` | Remove task | `user_id`, `task_id` | `task_id`, `status: "deleted"`, `title` |
| `update_task` | Modify task | `user_id`, `task_id`, `title` (optional), `description` (optional) | `task_id`, `status: "updated"`, `title` |

### MCP Server Location
- **Path**: `phaseIII/backend/app/mcp/`
- **Files**:
  - `server.py` - MCP server manager and lifecycle
  - `tools.py` - Tool implementations with database access

### Database Integration
- Each tool function receives database session via dependency injection
- Tools use SQLModel ORM for database operations
- All queries scoped to `user_id` parameter for data isolation

---

## 4. OpenAI ChatKit Frontend Integration

### Decision
Use **OpenAI ChatKit** with the **Managed ChatKit Starter** template for the chat interface.

### Rationale
- **Constitutional Mandate**: Phase III constitution requires ChatKit (Principle VI)
- **Rapid Development**: Pre-built chat UI components reduce implementation time
- **Best Practices**: Starter template includes auth integration, message display, loading states
- **Domain Security**: Domain allowlist configured in OpenAI platform

### Template Source
- **Repository**: https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit
- **Documentation**: https://platform.openai.com/docs/guides/chatkit

### Implementation Approach
1. Clone Managed ChatKit Starter template to `phaseIII/frontend/`
2. Configure ChatKit domain key from OpenAI platform
3. Integrate Better Auth for user authentication
4. Connect to FastAPI chat endpoint (`/api/{user_id}/chat`)
5. Customize UI for task management context

### Key Features to Implement
- Message display with user/assistant roles
- Loading states during AI processing
- Tool call visualization (show which MCP tools invoked)
- Conversation history display
- Error handling with retry options

---

## 5. Better Auth Integration for Phase III

### Decision
Reuse Better Auth configuration with JWT plugin for Phase III authentication, maintaining consistency with Phase II.

### Rationale
- **Constitutional Mandate**: Principle IV requires Better Auth for all phases
- **Consistency**: Same auth mechanism across Phase II and Phase III
- **JWT Validation**: Backend validates tokens using shared secret
- **Session Management**: Better Auth handles token refresh and storage

### Integration Points

**Frontend (ChatKit)**:
- Better Auth client in `phaseIII/frontend/lib/auth.ts`
- API client at `phaseIII/frontend/lib/api/chat.ts` attaches JWT token
- User ID extracted from session for API URL construction (`/api/{user_id}/chat`)

**Backend (FastAPI)**:
- JWT validation dependency in `phaseIII/backend/app/routers/chat.py`
- Validate token signature with Better Auth shared secret
- Extract `user_id` from JWT payload
- Validate path parameter matches JWT `user_id` (return 403 if mismatch)
- All database queries scoped to JWT `user_id`

### Security Flow
```
User Login → Better Auth Issues JWT → Frontend Stores Token
                                     ↓
User Sends Message → Axios Interceptor Attaches JWT
                                     ↓
Backend Validates JWT → Extracts user_id → Validates Path Match
                                     ↓
Query Database (scoped to JWT user_id) → Return Response
```

---

## 6. Database Schema Design (Phase III)

### Decision
Use **separate tables** for Phase III (`tasks_phaseiii`, `conversations`, `messages`) with independent Alembic migrations.

### Rationale
- **Constitutional Mandate**: Principle II requires complete phase separation
- **No Phase II Imports**: Phase III must not depend on Phase II tables
- **Independent Evolution**: Phase III schema can evolve without affecting Phase II
- **Data Isolation**: Clear separation prevents accidental cross-phase queries

### Schema Overview

**tasks_phaseiii** (Phase III task storage):
- `id` (int, PK, autoincrement)
- `user_id` (str, indexed, NOT NULL)
- `title` (str, NOT NULL, max 200)
- `description` (str, nullable)
- `completed` (bool, NOT NULL, default False)
- `created_at` (datetime, NOT NULL)
- `updated_at` (datetime, NOT NULL)

**conversations** (Chat sessions):
- `id` (int, PK, autoincrement)
- `user_id` (str, indexed, NOT NULL)
- `created_at` (datetime, NOT NULL)
- `updated_at` (datetime, NOT NULL)

**messages** (Chat messages):
- `id` (int, PK, autoincrement)
- `conversation_id` (int, FK → conversations.id, indexed)
- `user_id` (str, indexed, NOT NULL)
- `role` (str, NOT NULL: 'user' or 'assistant')
- `content` (text, NOT NULL)
- `created_at` (datetime, NOT NULL)

### Migration Strategy
- Independent Alembic environment in `phaseIII/backend/alembic/`
- Separate migration history from Phase II
- Initial migration creates all three tables
- Index on `user_id` for efficient data filtering

---

## 7. Rate Limiting Strategy

### Decision
Implement **10 requests per minute per user** rate limiting at the API endpoint level.

### Rationale
- **Requirement**: Spec FR-010 mandates rate limiting for abuse prevention
- **Clarification**: User specified 10 req/min in spec clarifications
- **Balance**: Allows normal conversation flow while preventing spam
- **Implementation**: Use `slowapi` middleware with Redis backend

### Implementation
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=lambda: get_jwt_user_id())

@router.post("/api/{user_id}/chat")
@limiter.limit("10/minute")
async def chat_endpoint(...):
    ...
```

### Error Response (HTTP 429)
```json
{
  "detail": "Rate limit exceeded. Please try again in 60 seconds.",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## 8. Conversation Persistence Strategy

### Decision
**Store all conversations indefinitely** with user controls for conversation management (list, delete).

### Rationale
- **Requirement**: Spec clarification specifies indefinite storage with user controls
- **Context Building**: Long-lived conversations enable richer AI context
- **User Control**: Users can delete unwanted conversations
- **Scalability**: Database handles conversation growth; no archival needed initially

### Conversation Management APIs (Future)
While not in current spec, these endpoints would support user control:
- `GET /api/{user_id}/conversations` - List user's conversations
- `DELETE /api/{user_id}/conversations/{conversation_id}` - Delete conversation

---

## 9. Error Handling Strategy for AI Service Unavailability

### Decision
Provide **clear error message with retry option** when Gemini API is unavailable.

### Rationale
- **Requirement**: Spec FR-019 and clarification specify error message with retry
- **User Experience**: Informative errors reduce user frustration
- **Resilience**: Graceful degradation without system crash

### Error Response Pattern
```json
{
  "detail": "The AI service is temporarily unavailable. Please try again in a moment.",
  "code": "AI_SERVICE_UNAVAILABLE",
  "retry_after": 30
}
```

### Implementation
- Catch Gemini API exceptions (timeout, rate limit, service error)
- Return HTTP 503 Service Unavailable
- Frontend displays retry button with countdown

---

## 10. Package Management Confirmation

### Decision
- **Backend**: UV (`uv add <package>`)
- **Frontend**: Bun (`bun add <package>`)

### Rationale
- **Constitutional Mandate**: Technology Constraints (Phase III) require UV and Bun
- **UV Benefits**: Fast Python dependency resolution, lock file, reproducible builds
- **Bun Benefits**: Fast JavaScript runtime and package manager, drop-in npm replacement

### Key Packages

**Backend** (UV):
- `fastapi` - Web framework
- `sqlmodel` - ORM (combines SQLAlchemy + Pydantic)
- `alembic` - Database migrations
- `asyncpg` - Async PostgreSQL driver
- `google-generativeai` - Gemini API client
- `openai` - OpenAI Agents SDK
- `mcp` - Official MCP Python SDK
- `slowapi` - Rate limiting
- `pytest` - Testing framework
- `pydantic-settings` - Configuration management

**Frontend** (Bun):
- `next` - Next.js framework
- `react` - React library
- `better-auth` - Authentication
- `openai` - ChatKit integration (if needed)
- `axios` - HTTP client
- `zod` - Schema validation

---

## Research Completion Checklist

- [x] AI service selection resolved (Gemini)
- [x] OpenAI Agents SDK integration strategy defined
- [x] MCP server architecture specified
- [x] OpenAI ChatKit frontend approach established
- [x] Better Auth integration pattern confirmed
- [x] Database schema design completed
- [x] Rate limiting strategy defined (10 req/min)
- [x] Conversation persistence strategy clarified (indefinite storage)
- [x] Error handling for AI unavailability specified
- [x] Package management confirmed (UV + Bun)

**Status**: All technical unknowns resolved. Ready for Phase 1 design.

---

**Next Steps**: Proceed to Phase 1 to generate:
1. `data-model.md` - Entity definitions and relationships
2. `contracts/` - API contract specifications (OpenAPI)
3. `quickstart.md` - Development setup and workflow guide
