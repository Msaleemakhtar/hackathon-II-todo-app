You are a Requirements Architect specializing in Spec-Driven Development (SDD). Create a comprehensive specification for the "MCP Server Implementation for Phase III Todo AI Chatbot" feature.

Write a complete specification document that will be saved at specs/sphaseIII/001-mcp-server-inegration/spec.md following the standard specification format.

The specification should include:

1. specification for feature - mcp-server integration

2. FEATURE DESCRIPTION: MCP Server Implementation for the AI-powered todo chatbot, including backend infrastructure, 5 MCP tools for task operations, and database models with separate tables from Phase II.

3. USER JOURNEY: As a user, I want to interact with a natural language AI assistant that can manage my tasks through conversational commands. The assistant should be able to add, list, complete, delete, and update tasks using MCP tools while maintaining conversation history.

4. USER SCENARIOS:
   - P1: MCP Server Setup and Add Task via MCP Tool
   - P2: List Tasks via MCP Tool and Complete/Delete/Update Tasks
   - P3: Conversation Persistence, Phase Separation, and Multi-user Data Isolation

5. FUNCTIONAL REQUIREMENTS (FR-001 to FR-010):
   - FR-001: MCP Server Infrastructure using official MCP SDK
   - FR-002: MCP Tool Implementation Details (all 5 tools with parameters, validation, and return values)
   - FR-003: Database Model Implementation with validation rules and indexes
   - FR-004: Backend Infrastructure (FastAPI, SQLModel, Alembic, UV package manager)
   - FR-005: Statelessness requirements (no in-memory state, horizontal scaling)
   - FR-006: Phase Separation (no Phase II imports, separate tables)
   - FR-007: Data Isolation (user ID scoping, path parameter validation)
   - FR-008: API Endpoint Implementation (/api/{user_id}/chat with proper structure)
   - FR-009: Configuration and Environment requirements (.env, tokens, settings)
   - FR-010: Authentication Integration (Better Auth JWT validation)

6. NON-FUNCTIONAL REQUIREMENTS:
   - NFR-001: Performance (p95 < 200ms)
   - NFR-002: Security (authentication validation)
   - NFR-003: Reliability (error handling with proper response format)

7. OUT OF SCOPE: Frontend implementation, OpenAI Agents SDK integration, natural language processing, Phase II code integration

8. SUCCESS CRITERIA: Complete checklist of 14 specific deliverables

9. ASSUMPTIONS: Development environment with Python 3.11+, UV package manager, Neon PostgreSQL, etc.

10. DEPENDENCIES: MCP SDK, FastAPI, SQLModel, Neon PostgreSQL, Better Auth, Alembic, UV

11. EDGE CASES: Complete list of 10 failure modes and error handling scenarios

Each requirement must:
- Have a unique ID (FR-XXX or NFR-XXX)
- Include detailed specifications with validation rules from the constitution:
  - Task Title validation: 1-200 characters after trimming
  - Task Description validation: Maximum 1000 characters
  - Task ID validation: Must be valid integer and exist for user
  - Chat Message validation: Required, cannot be empty
  - Conversation ID validation: Optional, must exist if provided for user
- Reference the constitutional sections that mandate these requirements
- Include specific verification criteria (PASS-XXX format)
- Detail expected parameters, validation rules, and return values for all MCP tools:
  add_task: {user_id, title, description?}
  list_tasks: {user_id, status?}
  complete_task: {user_id, task_id}
  delete_task: {user_id, task_id}
  update_task: {user_id, task_id, title?, description?}
- Include database schema specifications with proper indexes:
  - idx_tasks_phaseiii_user_id on tasks_phaseiii(user_id)
  - idx_conversations_user_id on conversations(user_id)
  - idx_messages_conversation_id on messages(conversation_id)
  - idx_messages_user_id on messages(user_id)
- Address constitutional requirements for statelessness, separation from Phase II, and data isolation
- Follow the Phase III directory structure: phaseIII/backend/app/
- Include exact error response format as required by constitution:
  {
    "detail": "Human-readable message",
    "code": "ERROR_CODE",
    "field": "optional_field_name"
  }

The specification must ensure:
- Complete separation from Phase II (no imports, separate tables)
- Stateless architecture as required by constitutional Principle XIII
- Proper JWT validation and path parameter matching (403 if mismatch)
- Use of UV for backend package management as required
- Implementation of all database models with separate tables (tasks_phaseiii, conversations, messages)
- Security requirements from constitutional Principle IV
- All constitutional requirements for Phase III (Principles XI-XIII)

Ensure the specification follows constitutional requirements from the todo app constitution, particularly around Phase separation, MCP server architecture (Principle XI), OpenAI Agents integration (Principle XII), conversational AI standards (Principle XIII), data models, API design standards, validation rules, and technology constraints.

The specification should be comprehensive enough that an AI developer can implement the complete MCP server infrastructure without ambiguity, with all technical details, validation rules, error handling, and architectural constraints clearly defined. All requirements must be testable with clear acceptance criteria and verification steps.
