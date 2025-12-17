# Tasks: AI-Powered Conversational Task Management

**Input**: Design documents from `/specs/sphaseIII/002-ai-chat-service-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in spec - OPTIONAL. Not included in this tasks list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Web application structure** (from plan.md):
- Backend: `phaseIII/backend/`
- Frontend: `phaseIII/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Phase III directory structure at phaseIII/backend/ and phaseIII/frontend/
- [ ] T002 [P] Initialize UV Python project with pyproject.toml in phaseIII/backend/
- [ ] T003 [P] Initialize Bun Next.js project with package.json in phaseIII/frontend/
- [ ] T004 [P] Create backend configuration module in phaseIII/backend/app/config.py
- [ ] T005 [P] Create frontend environment configuration in phaseIII/frontend/.env.local
- [ ] T006 [P] Create backend .env file with required environment variables
- [ ] T007 [P] Set up .gitignore for Python and Node.js in phaseIII/ directories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & ORM Setup

- [ ] T008 Install backend dependencies using UV (FastAPI, SQLModel, Alembic, asyncpg, pydantic-settings)
- [ ] T009 Create database connection module in phaseIII/backend/app/database.py
- [ ] T010 [P] Define TaskPhaseIII model in phaseIII/backend/app/models/task.py
- [ ] T011 [P] Define Conversation model in phaseIII/backend/app/models/conversation.py
- [ ] T012 [P] Define Message model with MessageRole enum in phaseIII/backend/app/models/message.py
- [ ] T013 Initialize Alembic in phaseIII/backend/alembic/
- [ ] T014 Create initial migration for tasks_phaseiii, conversations, messages tables
- [ ] T015 Apply migration to Neon database (uv run alembic upgrade head)

### Authentication & Security

- [ ] T016 Create JWT validation dependency in phaseIII/backend/app/dependencies/auth.py
- [ ] T017 Implement verify_jwt function to validate Better Auth tokens
- [ ] T018 Implement validate_user_id_match function to ensure path user_id matches JWT user_id

### API Infrastructure

- [ ] T019 Create FastAPI application in phaseIII/backend/app/main.py with CORS configuration
- [ ] T020 [P] Add health check endpoint at /health in phaseIII/backend/app/main.py
- [ ] T021 [P] Configure rate limiting middleware using slowapi (10 req/min per user)
- [ ] T022 [P] Create error response schemas in phaseIII/backend/app/schemas/errors.py
- [ ] T023 Create chat request/response schemas in phaseIII/backend/app/schemas/chat.py

### MCP Server Setup

- [ ] T024 Install MCP Python SDK using UV (uv add mcp)
- [ ] T025 Create MCP server manager in phaseIII/backend/app/mcp/server.py
- [ ] T026 Initialize MCP server lifecycle in phaseIII/backend/app/main.py

### AI Service Setup

- [ ] T027 Install Gemini SDK using UV (uv add google-generativeai)
- [ ] T028 Install OpenAI Agents SDK using UV (uv add openai)
- [ ] T029 Create Gemini client wrapper in phaseIII/backend/app/services/gemini_service.py
- [ ] T030 Create AI agent orchestrator in phaseIII/backend/app/services/agent_service.py

### Frontend Foundation

- [ ] T031 Install frontend dependencies using Bun (next, react, better-auth, axios, zod)
- [ ] T032 Clone OpenAI ChatKit Managed starter template to phaseIII/frontend/
- [ ] T033 Create Better Auth client in phaseIII/frontend/lib/auth.ts
- [ ] T034 Create Axios API client with JWT interceptor in phaseIII/frontend/lib/api/chat.ts
- [ ] T035 Configure Next.js with ChatKit integration in phaseIII/frontend/app/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Task Management Through Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can create, view, complete, and delete their todo tasks using natural language conversation instead of traditional UI forms or buttons.

**Independent Test**: Start a conversation, issue various task management commands in natural language (add, list, complete, delete), and verify that tasks are correctly managed. Delivers immediate value by allowing users to manage tasks without navigating traditional UI.

### MCP Tools Implementation (US1)

- [ ] T036 [P] [US1] Implement add_task tool in phaseIII/backend/app/mcp/tools.py
- [ ] T037 [P] [US1] Implement list_tasks tool in phaseIII/backend/app/mcp/tools.py
- [ ] T038 [P] [US1] Implement complete_task tool in phaseIII/backend/app/mcp/tools.py
- [ ] T039 [P] [US1] Implement delete_task tool in phaseIII/backend/app/mcp/tools.py
- [ ] T040 [P] [US1] Implement update_task tool in phaseIII/backend/app/mcp/tools.py
- [ ] T041 [US1] Register all 5 MCP tools with server in phaseIII/backend/app/mcp/server.py

### Database Services (US1)

- [ ] T042 [P] [US1] Create TaskService with CRUD operations in phaseIII/backend/app/services/task_service.py
- [ ] T043 [P] [US1] Create ConversationService for conversation management in phaseIII/backend/app/services/conversation_service.py
- [ ] T044 [P] [US1] Create MessageService for message persistence in phaseIII/backend/app/services/message_service.py
- [ ] T045 [US1] Add validation functions (validate_task_title, validate_message_content) in phaseIII/backend/app/utils/validation.py

### AI Agent Integration (US1)

- [ ] T046 [US1] Implement Gemini-to-OpenAI adapter in phaseIII/backend/app/services/gemini_service.py
- [ ] T047 [US1] Implement agent orchestration with MCP tool invocation in phaseIII/backend/app/services/agent_service.py
- [ ] T048 [US1] Add error handling for Gemini API failures (503 response) in phaseIII/backend/app/services/agent_service.py

### Chat API Endpoint (US1)

- [ ] T049 [US1] Create chat router in phaseIII/backend/app/routers/chat.py
- [ ] T050 [US1] Implement POST /api/{user_id}/chat endpoint with JWT validation
- [ ] T051 [US1] Add conversation_id handling (create new or continue existing) in chat endpoint
- [ ] T052 [US1] Integrate agent service to process user messages in chat endpoint
- [ ] T053 [US1] Store user messages and assistant responses in database
- [ ] T054 [US1] Return ChatResponse with conversation_id, response, and tool_calls

### Frontend Chat Interface (US1)

- [ ] T055 [US1] Create ChatInterface component in phaseIII/frontend/components/chat/ChatInterface.tsx
- [ ] T056 [US1] Implement message input field with send functionality in ChatInterface
- [ ] T057 [US1] Implement message display (user and assistant messages) in ChatInterface
- [ ] T058 [US1] Add loading state during AI processing in ChatInterface
- [ ] T059 [US1] Display tool calls invoked by the AI agent in ChatInterface
- [ ] T060 [US1] Create chat page at phaseIII/frontend/app/chat/page.tsx
- [ ] T061 [US1] Integrate Better Auth session management in chat page
- [ ] T062 [US1] Call sendChatMessage API with user_id from session

### Error Handling (US1)

- [ ] T063 [P] [US1] Add error handling for 400 (invalid message) in frontend
- [ ] T064 [P] [US1] Add error handling for 401 (unauthorized) in frontend
- [ ] T065 [P] [US1] Add error handling for 403 (user_id mismatch) in frontend
- [ ] T066 [P] [US1] Add error handling for 429 (rate limit) in frontend
- [ ] T067 [P] [US1] Add error handling for 503 (AI service unavailable) with retry in frontend

### Data Isolation & Security (US1)

- [ ] T068 [US1] Add user_id validation in all MCP tools (reject if task doesn't belong to user)
- [ ] T069 [US1] Add user_id scoping to all database queries in TaskService
- [ ] T070 [US1] Add conversation ownership validation in ConversationService
- [ ] T071 [US1] Verify path user_id matches JWT user_id in chat endpoint (return 403 if mismatch)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can manage tasks through natural language conversation.

---

## Phase 4: User Story 2 - Contextual Conversation Continuity (Priority: P2)

**Goal**: Users can have ongoing conversations where the system remembers previous exchanges and maintains context across multiple requests.

**Independent Test**: Initiate a conversation, perform several actions, then close and reopen the conversation using its ID. Verify that the assistant can reference previous messages and maintain context about tasks discussed earlier.

### Conversation History Management (US2)

- [ ] T072 [US2] Implement get_conversation_with_messages in ConversationService (load last 20 messages)
- [ ] T073 [US2] Update agent orchestrator to include conversation history in AI context in phaseIII/backend/app/services/agent_service.py
- [ ] T074 [US2] Format conversation history for Gemini API (chronological order) in agent service
- [ ] T075 [US2] Update chat endpoint to load conversation history when conversation_id provided

### Frontend Conversation Continuity (US2)

- [ ] T076 [US2] Store conversation_id in React state after first message in ChatInterface
- [ ] T077 [US2] Include conversation_id in subsequent API requests in ChatInterface
- [ ] T078 [US2] Display full conversation history in ChatInterface (scroll to bottom on new message)
- [ ] T079 [US2] Persist conversation_id in URL query parameter for conversation resumption
- [ ] T080 [US2] Load conversation history from API on component mount if conversation_id in URL

### Context Window Management (US2)

- [ ] T081 [US2] Implement message limiting (last 20 messages) in get_conversation_with_messages
- [ ] T082 [US2] Add conversation timestamp updates on new messages in ConversationService
- [ ] T083 [US2] Verify AI can reference previous context (test with ambiguous pronouns)

### Conversation Metadata (US2)

- [ ] T084 [US2] Add conversation creation timestamp display in frontend
- [ ] T085 [US2] Add last updated timestamp display in frontend
- [ ] T086 [US2] Show message count indicator in frontend

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Conversations maintain context across sessions.

---

## Phase 5: User Story 3 - Intelligent Error Handling and Guidance (Priority: P3)

**Goal**: When users make requests that cannot be fulfilled or use unclear language, they receive helpful, informative feedback that guides them toward successful task completion.

**Independent Test**: Deliberately trigger various error conditions (invalid task IDs, ambiguous requests, system unavailability, unauthorized access attempts) and verify that users receive clear, actionable feedback in each case.

### Enhanced Error Detection (US3)

- [ ] T087 [US3] Implement ambiguity detection in agent service (multiple task matches) in phaseIII/backend/app/services/agent_service.py
- [ ] T088 [US3] Add task title search when user references task by title instead of ID in agent service
- [ ] T089 [US3] Implement confidence scoring for intent detection in agent service
- [ ] T090 [US3] Add clarification prompt generation when confidence below threshold in agent service

### User-Friendly Error Messages (US3)

- [ ] T091 [P] [US3] Enhance TASK_NOT_FOUND error with task list suggestion
- [ ] T092 [P] [US3] Enhance INVALID_TITLE error with character count and example
- [ ] T093 [P] [US3] Enhance AI_SERVICE_UNAVAILABLE error with retry countdown
- [ ] T094 [P] [US3] Add helpful context to CONVERSATION_NOT_FOUND error

### Guided User Interactions (US3)

- [ ] T095 [US3] Implement disambiguation flow when multiple tasks match in agent service
- [ ] T096 [US3] Add example phrases for unclear intents in agent responses
- [ ] T097 [US3] Implement fallback responses with action suggestions in agent service
- [ ] T098 [US3] Add conversation starter suggestions in frontend (e.g., "Try: 'Show my tasks'")

### Frontend Error UI Enhancements (US3)

- [ ] T099 [US3] Create ErrorMessage component with retry button in phaseIII/frontend/components/chat/ErrorMessage.tsx
- [ ] T100 [US3] Add inline help tooltips for common operations in ChatInterface
- [ ] T101 [US3] Display suggested actions when errors occur in ChatInterface
- [ ] T102 [US3] Show typing indicator during AI processing in ChatInterface

### Security Error Handling (US3)

- [ ] T103 [US3] Add user-friendly message for unauthorized access attempts (403 errors)
- [ ] T104 [US3] Implement session expiry detection with re-authentication prompt in frontend
- [ ] T105 [US3] Add cross-user access prevention with clear error message in backend

**Checkpoint**: All user stories should now be independently functional with polished error handling and user guidance.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance Optimization

- [ ] T106 [P] Add database indexes for tasks_phaseiii (user_id, user_id+completed) in migration
- [ ] T107 [P] Add database indexes for conversations (user_id) in migration
- [ ] T108 [P] Add database indexes for messages (conversation_id, user_id) in migration
- [ ] T109 Verify query performance meets targets (<50ms for tasks, <100ms for messages)

### Logging & Monitoring

- [ ] T110 [P] Add structured logging for all MCP tool invocations in tools.py
- [ ] T111 [P] Add logging for JWT validation failures in auth dependency
- [ ] T112 [P] Add logging for Gemini API errors in gemini_service.py
- [ ] T113 [P] Add logging for rate limit events in chat endpoint

### Code Quality

- [ ] T114 [P] Run ruff linter on backend code (uv run ruff check .)
- [ ] T115 [P] Run ruff formatter on backend code (uv run ruff format .)
- [ ] T116 [P] Run Next.js linter on frontend code (bun run lint)
- [ ] T117 Type annotation completeness check in Python files

### Documentation

- [ ] T118 [P] Add docstrings to all MCP tools in tools.py
- [ ] T119 [P] Add docstrings to all service methods in services/
- [ ] T120 [P] Add JSDoc comments to frontend API functions in lib/api/chat.ts
- [ ] T121 Create API documentation from OpenAPI spec (chat-api.yaml)

### Security Hardening

- [ ] T122 Verify all database queries are scoped to user_id
- [ ] T123 Verify JWT validation on all protected endpoints
- [ ] T124 Test conversation access control (reject if conversation belongs to another user)
- [ ] T125 Add input sanitization for user messages (prevent injection attacks)

### Deployment Preparation

- [ ] T126 [P] Create Dockerfile for backend in phaseIII/backend/Dockerfile
- [ ] T127 [P] Create Dockerfile for frontend in phaseIII/frontend/Dockerfile
- [ ] T128 Create docker-compose.yml for local development
- [ ] T129 Run quickstart.md validation (verify all setup steps work)

### Final Validation

- [ ] T130 Manual end-to-end test following spec acceptance scenarios for US1
- [ ] T131 Manual end-to-end test following spec acceptance scenarios for US2
- [ ] T132 Manual end-to-end test following spec acceptance scenarios for US3
- [ ] T133 Verify all edge cases from spec (multi-user isolation, rate limiting, concurrent modifications)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 infrastructure but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1/US2 but independently testable

### Within Each User Story

- MCP tools before agent integration
- Services before API endpoints
- Backend endpoints before frontend integration
- Core functionality before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Setup (Phase 1)**:
- T002, T003, T004, T005, T006, T007 can run in parallel

**Foundational (Phase 2)**:
- Database models: T010, T011, T012 can run in parallel
- Security: T016, T017, T018 can run in parallel (after database setup)
- API infrastructure: T020, T021, T022, T023 can run in parallel
- Services: T027, T028, T031 can run in parallel

**User Story 1**:
- MCP tools: T036, T037, T038, T039, T040 can run in parallel
- Services: T042, T043, T044 can run in parallel (after models)
- Error handlers: T063, T064, T065, T066, T067 can run in parallel

**User Story 3**:
- Error enhancements: T091, T092, T093, T094 can run in parallel

**Polish**:
- Indexes: T106, T107, T108 can run in parallel
- Logging: T110, T111, T112, T113 can run in parallel
- Code quality: T114, T115, T116, T117 can run in parallel
- Docs: T118, T119, T120 can run in parallel
- Dockerfiles: T126, T127 can run in parallel

---

## Parallel Example: User Story 1 MCP Tools

```bash
# Launch all MCP tool implementations together:
Task: "Implement add_task tool in phaseIII/backend/app/mcp/tools.py"
Task: "Implement list_tasks tool in phaseIII/backend/app/mcp/tools.py"
Task: "Implement complete_task tool in phaseIII/backend/app/mcp/tools.py"
Task: "Implement delete_task tool in phaseIII/backend/app/mcp/tools.py"
Task: "Implement update_task tool in phaseIII/backend/app/mcp/tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T035) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T036-T071)
4. **STOP and VALIDATE**: Test User Story 1 independently using spec acceptance scenarios
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add Polish (Phase 6) → Final production-ready release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T035)
2. Once Foundational is done:
   - Developer A: User Story 1 (T036-T071)
   - Developer B: User Story 2 (T072-T086)
   - Developer C: User Story 3 (T087-T105)
3. Stories complete and integrate independently
4. Team collaborates on Polish phase

---

## Task Summary

- **Total Tasks**: 133
- **Setup**: 7 tasks
- **Foundational**: 28 tasks (BLOCKING)
- **User Story 1 (P1)**: 36 tasks (MVP)
- **User Story 2 (P2)**: 15 tasks
- **User Story 3 (P3)**: 19 tasks
- **Polish**: 28 tasks

**Parallel Opportunities**: 45+ tasks can run in parallel within their phases

**MVP Scope**: Phases 1-3 (71 tasks) deliver core conversational task management

---

## Notes

- [P] tasks = different files or independent work, no dependencies
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are OPTIONAL (not included as not explicitly requested in spec)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
