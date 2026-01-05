# Implementation Plan: ChatKit UI Enhancements

**Branch**: `003-chatkit-ui` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-chatkit-ui/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enhances the ChatKit UI with visual indicators and improved discoverability for Phase V advanced task management capabilities. Primary implementation approach is **prompt-based formatting** where the AI system prompt is updated with formatting guidelines and examples. The AI learns to display priorities (🔴🟠🟡⚪), categories (📁), tags (#), relative due dates (📅/⚠️), and human-readable recurrence patterns (🔄). No backend code changes or database migrations are required. The frontend is updated with 8 diverse suggested prompts and an enhanced greeting message that showcases Phase V features (priorities, categories, tags, due dates, recurring tasks, search, and reminders).

**Technical Approach**: 100% prompt engineering + minimal frontend config changes. Zero database/backend logic modifications.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend - config only)
**Primary Dependencies**: Next.js 15 (frontend), OpenAI ChatKit SDK, OpenAI Agents SDK 0.6.3+ (backend system prompt)
**Storage**: N/A (no database changes - all data models exist from Features 001/002)
**Testing**: Manual testing (browser compatibility, emoji rendering, suggested prompts)
**Target Platform**: Modern web browsers (Chrome 120+, Firefox 120+, Safari 17+, Edge 120+), mobile browsers (iOS 17+, Android 14+)
**Project Type**: Web application (frontend config + backend system prompt enhancement)
**Performance Goals**: AI response time <3s at p95 latency, token consumption increase <15% vs baseline, suggested prompt click-through rate >5% per prompt
**Constraints**: System prompt MUST stay under 4,000 tokens, all emoji MUST be Unicode 9.0 (2016) for 99% browser support, Markdown formatting MUST render correctly in ChatKit React component, no breaking changes to existing ChatKit configuration or API endpoints
**Scale/Scope**: 8 suggested prompts, 1 enhanced greeting message, 1 updated system prompt with formatting guidelines and 5+ examples, zero new components/APIs/database tables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Alignment: Phase V Feature 003

**Principle I - Spec-Driven Development**: ✅ PASS
- Specification created first (`specs/003-chatkit-ui/spec.md`) before implementation
- AI-generated implementation approach (prompt engineering + config)
- No manual coding required (config files only)

**Principle II - Repository Structure**: ✅ PASS
- Phase V directory structure maintained (`/phaseV/frontend/`, `/phaseV/backend/`)
- Spec in correct location (`/specs/003-chatkit-ui/`)
- No cross-phase imports (changes isolated to Phase V)

**Principle III - Persistent & Relational State**: ✅ PASS
- Zero database changes (no new tables, columns, or indexes)
- All data models exist from Features 001/002
- No migrations required

**Principle IV - JWT Security**: ✅ PASS (No Auth Changes)
- No authentication/authorization changes
- Uses existing Better Auth JWT validation
- No path parameter/JWT validation changes required

**Principle V - Backend Architecture Standards**: ✅ PASS (Minimal)
- Only file changed: `backend/app/services/task_server.py` (system prompt)
- No new routers, services, or API endpoints
- No business logic changes

**Principle VI - Frontend Architecture Standards**: ✅ PASS (Config Only)
- Changes limited to ChatKit configuration
- Updated greeting message (string constant)
- Updated suggested prompts (array of strings)
- Zero new components or pages

**Principle VII - Automated Testing Standards**: ⚠️ MANUAL TESTING ONLY
- No unit tests (no new logic to test)
- Manual browser testing required (emoji rendering, Markdown formatting)
- ChatKit suggested prompt testing (click-through)
- **Rationale**: Prompt-based formatting is tested through AI interaction, not unit tests

**Principle VIII - Containerization & Deployment**: ✅ PASS (No Changes)
- No Dockerfile changes
- No docker-compose changes
- Existing containers work unchanged

**Principle IX - CI/CD Pipeline**: ✅ PASS (No Changes)
- No CI/CD workflow changes
- Existing pipelines continue to work
- No new build steps required

**Principle X - Feature Scope Evolution**: ✅ PASS
- Feature enhances existing Phase V capabilities (visualization layer)
- No new MCP tools (maintains 17 tools from Feature 002)
- Improved discoverability of existing features

**Principle XI - MCP Server Architecture**: ✅ PASS (No Changes)
- MCP tools unchanged (17 tools remain functional)
- No tool signature changes
- Tool responses remain same format

**Principle XII - OpenAI Agents SDK**: ✅ PASS (System Prompt Only)
- Agent configuration unchanged
- System prompt enhanced with formatting guidelines
- No SDK version changes

**Principle XIII - Conversational AI Standards**: ✅ PASS
- Stateless architecture maintained
- No conversation flow changes
- No database persistence changes

**Principle XIV - Containerization & Orchestration**: ✅ PASS (No K8s Changes)
- No Helm chart changes
- No Kubernetes manifest changes
- No deployment strategy changes

**Principle XV - Production-Grade Deployment**: ✅ PASS (No Infra Changes)
- No infrastructure changes
- No HPA/resource changes
- Existing production deployment works unchanged

**Principle XVI - Event-Driven Architecture**: ✅ PASS (No Kafka Changes)
- No Kafka topic changes
- No event schema changes
- Existing event-driven architecture works unchanged

**Principle XVII - Dapr Integration**: ✅ PASS (No Dapr Changes)
- No Dapr component changes
- No pub/sub changes
- Existing Dapr configuration works unchanged

**Principle XVIII - Production Cloud Deployment**: ✅ PASS (No Cloud Changes)
- No Oracle Cloud OKE changes
- No CI/CD pipeline changes
- No monitoring/security changes

### Complexity Gate Evaluation

**Zero Complexity Violations**: ✅ ALL GATES PASS

This feature introduces NO new:
- Database tables or columns
- API endpoints or routers
- Services or business logic
- External dependencies
- Infrastructure components

**Scope**: Pure presentation layer (prompt engineering + frontend config)

**Rationale**: Complexity is minimal. Changes are limited to:
1. System prompt text (backend config)
2. Greeting message string (frontend config)
3. Suggested prompts array (frontend config)

No architectural decisions, no design patterns, no abstractions. This is the simplest possible feature implementation - configuration-only changes.

### Final Gate Status: ✅ ALL PASS - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (Phase V Web Application)

```text
phaseV/
├── backend/
│   └── app/
│       └── services/
│           └── task_server.py   # MODIFIED: Update _get_system_instructions()
│
└── frontend/
    ├── components/
    │   └── chat/
    │       └── ChatInterface.tsx  # MODIFIED: Update greeting + suggested prompts
    └── lib/
        └── chatkit-config.ts      # MODIFIED (if config externalized)
```

**Structure Decision**: Web application (Option 2). Changes are minimal - only configuration updates:
- **Backend**: 1 file modified (system prompt in `task_server.py`)
- **Frontend**: 1 file modified (ChatKit config - greeting + prompts)
- **No new files created**
- **No database migrations**
- **No new services/components/APIs**

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

---

## Phase 0: Research (Skipped - No Technical Unknowns)

**Status**: ✅ SKIPPED

**Rationale**: This feature has zero technical unknowns. All technologies and patterns are well-established:
- System prompts are standard OpenAI Agents SDK configuration
- ChatKit greeting/prompts are frontend string constants
- Emoji are Unicode 9.0 standard (99% browser support)
- Markdown formatting is GitHub-flavored standard

**No research artifacts needed**: All implementation details are straightforward configuration changes.

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE

### Generated Artifacts

1. **data-model.md** ✅
   - Documents presentation-only enhancements (NO database changes)
   - Defines emoji mappings, date formatting, RRULE humanization
   - Confirms zero migrations required

2. **contracts/** ✅
   - `system-prompt-schema.md` - System prompt structure and formatting guidelines
   - `system-prompt-examples.md` - 8 example responses for AI to learn from
   - `chatkit-startscreen-config.md` - Greeting message and 8 suggested prompts

3. **quickstart.md** ✅
   - Step-by-step implementation guide (5 steps, ~1-2 hours)
   - Testing checklist (browser compatibility, formatting, suggested prompts)
   - Troubleshooting guide (formatting issues, emoji rendering, token limits)

---

## Post-Design Constitution Re-Evaluation

*Re-checking all principles after Phase 1 design completion*

### Constitutional Alignment: Phase V Feature 003 (Post-Design)

**Principle I - Spec-Driven Development**: ✅ PASS (No Change)
- Design artifacts generated from specification
- Implementation will be AI-generated from contracts
- No manual coding required (string config only)

**Principle II - Repository Structure**: ✅ PASS (Confirmed)
- Phase V directory structure confirmed in Project Structure section
- Only 2 files modified: `task_server.py` (backend), `ChatInterface.tsx` or `chatkit-config.ts` (frontend)
- Zero new directories or files created

**Principle III - Persistent & Relational State**: ✅ PASS (Confirmed)
- Data model review confirms zero database changes
- All presentation enhancements are computed at display time
- No Alembic migrations required

**Principle IV - JWT Security**: ✅ PASS (No Auth Changes - Confirmed)
- No authentication flows touched
- No user_id validation changes
- Configuration-only changes

**Principle V - Backend Architecture Standards**: ✅ PASS (Minimal - Confirmed)
- Only `task_server.py:_get_system_instructions()` modified
- System prompt is a configuration string (not business logic)
- No routers, services, or API endpoints touched

**Principle VI - Frontend Architecture Standards**: ✅ PASS (Config Only - Confirmed)
- ChatKit configuration (greeting + prompts) are string constants
- No new components, pages, or state management
- Zero React hooks or custom logic

**Principle VII - Automated Testing Standards**: ⚠️ MANUAL TESTING ONLY (Confirmed)
- No automated tests (prompt engineering cannot be unit tested)
- Manual testing checklist in quickstart.md
- Browser compatibility testing required
- **Rationale Confirmed**: AI behavior is tested through interaction, not unit tests

**Principle VIII - Containerization & Deployment**: ✅ PASS (No Changes - Confirmed)
- Dockerfiles unchanged (config baked into images at build time)
- docker-compose.yml unchanged

**Principle IX - CI/CD Pipeline**: ✅ PASS (No Changes - Confirmed)
- Existing CI/CD workflows work unchanged
- No new build steps or deployment scripts

**Principle X - Feature Scope Evolution**: ✅ PASS (Confirmed)
- Feature enhances presentation layer only
- MCP tools remain unchanged (17 tools)
- No new capabilities added (only improved discoverability)

**Principle XI - MCP Server Architecture**: ✅ PASS (No Changes - Confirmed)
- MCP tools unchanged (17 tools remain functional)
- Tool signatures unchanged
- Tool responses unchanged (formatting is AI-side)

**Principle XII - OpenAI Agents SDK**: ✅ PASS (System Prompt Only - Confirmed)
- Agent configuration unchanged
- System prompt enhanced with formatting examples
- SDK version unchanged (0.6.3+)

**Principle XIII - Conversational AI Standards**: ✅ PASS (Confirmed)
- Stateless architecture unchanged
- Conversation persistence unchanged
- No database schema changes

**Principle XIV - Containerization & Orchestration**: ✅ PASS (No K8s Changes - Confirmed)
- Helm charts unchanged
- Kubernetes manifests unchanged
- Deployment strategy unchanged

**Principle XV - Production-Grade Deployment**: ✅ PASS (No Infra Changes - Confirmed)
- HPA configurations unchanged
- Resource limits unchanged
- Ingress configuration unchanged

**Principle XVI - Event-Driven Architecture**: ✅ PASS (No Kafka Changes - Confirmed)
- Kafka topics unchanged
- Event schemas unchanged
- Producers/consumers unchanged

**Principle XVII - Dapr Integration**: ✅ PASS (No Dapr Changes - Confirmed)
- Dapr components unchanged
- Pub/sub configuration unchanged
- State store unchanged

**Principle XVIII - Production Cloud Deployment**: ✅ PASS (No Cloud Changes - Confirmed)
- Oracle Cloud OKE unchanged
- CI/CD pipelines unchanged
- Monitoring/security unchanged

### Complexity Gate Re-Evaluation: ✅ ALL GATES PASS (Confirmed Post-Design)

**Complexity Tracking Table**: EMPTY (No violations)

**Final Confirmation**:
- Zero architectural decisions made
- Zero new patterns introduced
- Zero abstractions created
- Zero new dependencies added
- Zero infrastructure changes

**Scope Confirmed**: Pure presentation layer (prompt engineering + frontend config)

### Final Gate Status (Post-Design): ✅ ALL PASS - Proceed to Implementation (Phase 2: /sp.tasks)

---

## Phase 2: Task Generation

**Status**: PENDING

**Next Command**: `/sp.tasks` (NOT created by /sp.plan)

The `/sp.tasks` command will generate `tasks.md` with actionable implementation steps based on this plan and the design artifacts.

---

## Summary

**Feature**: ChatKit UI Enhancements  
**Branch**: 003-chatkit-ui  
**Phase 1 Status**: ✅ COMPLETE

**Generated Artifacts**:
- ✅ plan.md (this file)
- ✅ data-model.md
- ✅ contracts/system-prompt-schema.md
- ✅ contracts/system-prompt-examples.md
- ✅ contracts/chatkit-startscreen-config.md
- ✅ quickstart.md

**Constitutional Status**: ✅ ALL GATES PASS (Pre-Design and Post-Design)

**Implementation Complexity**: MINIMAL (2 files, configuration-only)

**Next Step**: Run `/sp.tasks` to generate actionable implementation tasks

---

**Planning Complete**: 2026-01-05

