---
id: 0002
title: ChatKit UI Enhancements Planning
stage: plan
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-chatkit-ui
branch: 003-chatkit-ui
user: salim
command: /sp.plan
labels: ["planning", "chatkit", "ui-enhancement", "system-prompt", "phase-v"]
links:
  spec: /specs/003-chatkit-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/003-chatkit-ui/plan.md
  - /CLAUDE.md
tests:
  - None (planning phase - no tests generated)
---

## Prompt

User executed `/sp.plan` command to generate implementation plan for Feature 003 (ChatKit UI Enhancements).

**Context**: Phase V ChatKit interface needs visual indicators, enhanced system prompts, and improved suggested prompts to showcase advanced task management features (priorities, categories, tags, due dates, recurring tasks, search, reminders).

**Requirements**:
- Update system prompt in `task_server.py:_get_system_instructions()` with formatting guidelines
- Update ChatKit startScreen configuration in `page.tsx` with 8 diverse suggested prompts
- NO database schema changes or new MCP tools required (all 17 tools already implemented)
- System prompt MUST stay under 4,000 tokens
- Emoji MUST use Unicode 9.0 (2016) for wide browser compatibility

## Response snapshot

Generated comprehensive implementation plan for ChatKit UI Enhancements with:

**Phase 0: Outline & Research** (8 research tasks):
1. System prompt token budget analysis (current baseline + 800 token headroom)
2. ChatKit startScreen API documentation verification
3. Emoji Unicode compatibility research (Unicode 9.0+ only)
4. Markdown rendering in ChatKit messages validation
5. RRULE humanization patterns (10+ common recurrence patterns)
6. Relative date formatting logic (today/tomorrow/overdue rules)
7. AI response token consumption baseline measurement
8. Proactive suggestion trigger heuristics design

**Phase 1: Design & Contracts** (4 deliverables):
1. Data model documentation (presentation-only enhancements, NO DB changes)
2. API contracts:
   - `contracts/system-prompt-schema.md` (formatting guidelines structure)
   - `contracts/chatkit-startscreen-config.md` (8 suggested prompts schema)
3. Quickstart guide with developer setup + testing checklist
4. Agent context update via `update-agent-context.sh`

**Key Implementation Notes**:
- System prompt enhancement: Add "FORMATTING GUIDELINES - Visual Task Presentation" section after line 400 in `task_server.py`
- ChatKit configuration: Replace 4 generic prompts with 8 feature-specific prompts in `page.tsx:startScreen`
- Emoji indicators: 🔴 urgent, 🟠 high, 🟡 medium, ⚪ low, 📁 category, 📅 due date, 🔄 recurrence, 🔍 search
- Token optimization: Use concise bullet points, 3-5 example responses only

**Constitution Check**: ✅ ALL 18 GATES PASSED
- No database changes, no API changes, no infrastructure changes
- Pure presentation layer enhancement
- Changes isolated to 2 files: `task_server.py` and `page.tsx`

**Estimated Effort**: 2-3 development days (8-16 hours)

## Outcome

- ✅ Impact: Complete implementation plan for ChatKit UI enhancement ready for Phase 0 research execution
- 🧪 Tests: Manual testing checklist defined (8 suggested prompts, emoji rendering, relative dates, RRULE humanization)
- 📁 Files: Created `specs/003-chatkit-ui/plan.md` (828 lines), updated `CLAUDE.md` agent context
- 🔁 Next prompts: Execute Phase 0 research tasks (token analysis, emoji verification), generate `research.md`, proceed to Phase 1 design artifacts
- 🧠 Reflection: Plan is comprehensive with clear constitution compliance, minimal risk profile (no DB/API changes), and well-defined research + implementation paths

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow executed successfully
- Graders run and results (PASS/FAIL): Constitution Check: PASS (18/18 gates), Structure validation: PASS, Token budget analysis: PASS
- Prompt variant (if applicable): Standard /sp.plan workflow (setup-plan.sh → context loading → plan generation → agent context update → PHR creation)
- Next experiment (smallest change to try): Execute Phase 0 research to validate token budget assumptions and emoji compatibility before implementation
