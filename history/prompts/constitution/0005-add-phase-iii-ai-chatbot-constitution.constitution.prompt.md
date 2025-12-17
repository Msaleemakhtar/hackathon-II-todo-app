---
id: 0005
title: Add Phase III AI Chatbot Constitution
stage: constitution
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: Msaleemakhtar
command: /sp.constitution
labels: ["constitution", "phase-iii", "mcp", "openai-agents", "chatbot", "governance"]
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

You are updating the project constitution to incorporate Phase III requirements for the Todo AI Chatbot.

**Context:**
1. **Phase I and Phase II are COMPLETED** - These were separate phases focused on CLI (Phase I) and full-stack web app (Phase II)
2. **Phase III is a NEW, COMPLETELY SEPARATE implementation** for an AI-powered chatbot interface
3. **Complete separation required**: Phase III has NO dependencies on Phase I or Phase II code

**Phase III Requirements** (from @"Hackathon II - Todo Spec-Driven Development (1).md"):

**Objective:** Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture.

**Technology Stack (MANDATORY):**
- Frontend: OpenAI ChatKit (https://platform.openai.com/docs/guides/chatkit)
- Frontend Template: Managed ChatKit Starter (https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit)
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK (https://github.com/openai/openai-agents-python)
- MCP Server: Official MCP SDK (https://github.com/modelcontextprotocol/python-sdk)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth
- Package Management: UV for backend, Bun for frontend

**Architecture:**
- Stateless chat endpoint that persists conversation state to database
- MCP server exposes 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- OpenAI Agents SDK handles AI logic and tool invocation
- All MCP tools are stateless and store state in database

**Directory Structure** (from @discussedplan.md):
```
phaseIII/
├── backend/                    # Python FastAPI backend
│   ├── pyproject.toml         # UV package manager
│   ├── app/
│   │   ├── main.py
│   │   ├── models/            # Task, Conversation, Message
│   │   ├── services/          # task_service.py, chat_service.py
│   │   ├── mcp/               # MCP server and tools
│   │   └── routers/           # chat.py endpoint
│   └── tests/
├── frontend/                   # OpenAI ChatKit UI
│   ├── package.json           # Bun package manager
│   ├── app/
│   └── components/
└── README.md
```

**Specs Organization:**
- Phase III specs should be maintained in `/specs/sphaseIII/` directory
- Follow Specify Plus Kit structure: `/specs/sphaseIII/NNN-feature-name/` with spec.md, plan.md, tasks.md

**Database Models (Phase III specific):**
- Task: user_id, id, title, description, completed, created_at, updated_at (stored in `tasks_phaseiii` table - separate from Phase II)
- Conversation: user_id, id, created_at, updated_at (chat sessions)
- Message: user_id, id, conversation_id, role (user/assistant), content, created_at (chat history)

**API Endpoint:**
- POST /api/{user_id}/chat - Send message & get AI response

**Key Requirements:**
1. Implement conversational interface for task management
2. Use OpenAI Agents SDK for AI logic
3. Build MCP server with 5 tools (add, list, complete, delete, update tasks)
4. Stateless chat endpoint - all state in database
5. AI agents use MCP tools to manage tasks
6. MCP tools are stateless and store state in database

**Tasks for Constitution Update:**

1. **Update Mission Statement** - Extend to include Phase III AI chatbot development while acknowledging Phase I (CLI) and Phase II (web app) are complete

2. **Update Core Principles** - Add or modify principles for:
   - MCP Server Architecture (stateless tools, database state management)
   - OpenAI Agents SDK Integration
   - Conversational AI Standards
   - OpenAI ChatKit Frontend Requirements

3. **Update Repository Structure** - Add phaseIII directory structure showing complete separation from phaseI and phaseII

4. **Update Specs Organization** - Add `/specs/sphaseIII/` directory for Phase III specifications

5. **Update Data Model** - Add Phase III specific models (Conversation, Message) and clarify Task model separation (tasks_phaseiii table)

6. **Add MCP Tools Specification** - Document the 5 required MCP tools and their schemas

7. **Add Chat Service Requirements** - Stateless architecture, conversation persistence, agent behavior

8. **Update Technology Constraints** - Add mandatory technologies for Phase III:
   - OpenAI ChatKit for frontend
   - OpenAI Agents SDK for AI
   - Official MCP SDK for tools
   - UV for backend, Bun for frontend

9. **Update Success Criteria** - Add Phase III specific criteria (chatbot functionality, MCP tools, natural language understanding)

10. **Update API Design Standards** - Add chat endpoint specification

Follow the constitution update process:
1. Load existing constitution
2. Identify placeholders and sections to update
3. Draft updated content incorporating Phase III requirements
4. Ensure consistency across templates
5. Create Sync Impact Report
6. Validate (no unexplained placeholders, proper versioning)
7. Write updated constitution

**Version Bump Guidance:**
This is a MINOR version bump (2.3.0 -> 2.4.0) because:
- New phase/section added (Phase III)
- New architectural patterns (MCP, OpenAI Agents SDK)
- New principles added
- Backward compatible with Phase II (no changes to Phase II rules)

Please proceed with the constitution update.

## Response snapshot

Successfully updated the project constitution from version 2.3.0 to 2.4.0, incorporating comprehensive Phase III AI Chatbot governance rules. The update includes:

1. **Extended Mission Statement**: Now covers all three phases with Phase I (CLI) and Phase II (web app) marked as COMPLETED, and Phase III (AI Chatbot) as ACTIVE.

2. **Three New Core Principles Added**:
   - Principle XI: MCP Server Architecture (stateless tools, 5 tool specifications)
   - Principle XII: OpenAI Agents SDK Integration (agent behavior, conversation context)
   - Principle XIII: Conversational AI Standards (stateless architecture, conversation flow)

3. **Updated Repository Structure**: Added phaseIII directory structure with complete separation requirements, including backend (FastAPI + MCP), frontend (OpenAI ChatKit), and spec organization.

4. **Phase III Data Models**: Added Conversation and Message entities, clarified Task entity uses separate `tasks_phaseiii` table.

5. **API Design Standards**: Added Phase III chat endpoint specification (POST /api/{user_id}/chat) with request/response schemas.

6. **Technology Constraints**: Added mandatory Phase III stack (OpenAI ChatKit, Agents SDK, MCP SDK, UV, Bun).

7. **Success Criteria**: Added Phase III functional and technical requirements checklist.

8. **Requirement-to-Rule Mapping**: Added 17 new Phase III requirements (FR-P3-001 through TC-P3-005).

9. **Constitutional Self-Checks**: All 4 checks PASS (Alignment, Coverage, Conflict, Completeness).

## Outcome

- Impact: Constitution upgraded from v2.3.0 to v2.4.0 with comprehensive Phase III AI Chatbot governance. Added 3 new core principles (XI-XIII), Phase III data models, MCP tool specifications, chat endpoint standards, and 17 new traced requirements. Maintains backward compatibility with Phase II while establishing clear governance for Phase III development.
- Tests: None (constitutional document; validation via 4 self-checks - all PASS)
- Files: Modified .specify/memory/constitution.md (v2.3.0 -> v2.4.0)
- Next prompts: Create initial specs in /specs/sphaseIII/ directory; Set up phaseIII directory structure; Run /sp.specify for first Phase III feature (MCP server setup)
- Reflection: The constitution update demonstrates the importance of phase separation in multi-phase projects. By explicitly defining separate tables (tasks_phaseiii), separate directories, and NO IMPORT requirements, we ensure clean architecture boundaries while still maintaining unified governance principles.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update completed successfully following established amendment process
- Graders run and results (PASS/FAIL): Alignment PASS, Coverage PASS, Conflict-Free PASS, Completeness PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider adding MCP tool versioning strategy for future Phase III iterations
