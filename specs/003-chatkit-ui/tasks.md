# Tasks: ChatKit UI Enhancements

**Input**: Design documents from `/specs/003-chatkit-ui/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Feature Type**: Configuration-only (prompt engineering + frontend config)
**Tests**: Manual testing only (no automated tests - prompt behavior validated through interaction)
**Implementation Time**: ~1-2 hours

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

This is a **Phase V web application** with:
- **Backend**: `phaseV/backend/app/`
- **Frontend**: `phaseV/frontend/`

---

## Phase 1: Setup (Project Validation)

**Purpose**: Validate prerequisites and prepare for implementation

**No dependencies** - can start immediately

- [X] T001 Verify Phase V Features 001 & 002 are deployed and 17 MCP tools are functional
- [X] T002 [P] Verify ChatKit interface is operational at phaseV/frontend
- [X] T003 [P] Verify Neon PostgreSQL has required tables (tasks_phaseiii, categories, tags_phasev, task_tags)
- [X] T004 [P] Read contracts from specs/003-chatkit-ui/contracts/ (system-prompt-schema.md, system-prompt-examples.md, chatkit-startscreen-config.md)

**Checkpoint**: Prerequisites validated - ready for implementation

---

## Phase 2: Foundational (Core Implementation Files)

**Purpose**: Identify and prepare the 2 files that will be modified

**⚠️ CRITICAL**: This phase identifies the exact files to modify (backend system prompt + frontend config)

- [X] T005 Locate backend system prompt file (phaseV/backend/app/services/task_server.py or similar)
- [X] T006 Locate frontend ChatKit configuration (phaseV/frontend/components/chat/ChatInterface.tsx or phaseV/frontend/lib/chatkit-config.ts)
- [X] T007 Backup current system prompt content for rollback
- [X] T008 Backup current ChatKit configuration for rollback

**Checkpoint**: Files identified and backed up - ready for user story implementation

---

## Phase 3: User Story 1 - Discover Advanced Features Through Suggested Prompts (Priority: P1) 🎯 MVP

**Goal**: Users see 8 diverse suggested prompts on ChatKit start screen showcasing Phase V capabilities

**Independent Test**: Open ChatKit interface, verify 8 suggested prompts are visible and clickable, click each prompt and verify successful execution

### Implementation for User Story 1

- [X] T009 [US1] Update ChatKit greeting message to mention Phase V features in phaseV/frontend/components/chat/ChatInterface.tsx (or chatkit-config.ts)
- [X] T010 [US1] Replace suggested prompts with 8 diverse prompts per contracts/chatkit-startscreen-config.md in phaseV/frontend/components/chat/ChatInterface.tsx (or chatkit-config.ts)
- [X] T011 [US1] Verify greeting is under 50 words (character count validation)
- [X] T012 [US1] Verify all 8 prompts use appropriate emoji indicators (🔴📁#📅🔄🔍⏰)

### Manual Testing for User Story 1

- [ ] T013 [US1] Open ChatKit in Chrome 120+ and verify greeting displays correctly
- [ ] T014 [P] [US1] Open ChatKit in Firefox 120+ and verify greeting displays correctly
- [ ] T015 [P] [US1] Open ChatKit in Safari 17+ and verify greeting displays correctly
- [ ] T016 [US1] Click Prompt 1 (urgent task) and verify AI creates task with 🔴 emoji
- [ ] T017 [P] [US1] Click Prompt 2 (category viewing) and verify AI lists tasks with 📁 emoji
- [ ] T018 [P] [US1] Click Prompt 3 (tag filtering) and verify AI lists tasks with # prefix
- [ ] T019 [P] [US1] Click Prompt 4 (due date) and verify AI lists tasks with 📅 emoji
- [ ] T020 [P] [US1] Click Prompt 5 (recurring task) and verify AI creates task with 🔄 emoji
- [ ] T021 [P] [US1] Click Prompt 6 (search) and verify AI displays results with 🔍 relevance scores
- [ ] T022 [P] [US1] Click Prompt 7 (reminder) and verify AI sets reminder successfully
- [ ] T023 [P] [US1] Click Prompt 8 (multi-filter) and verify AI lists filtered tasks correctly

**Checkpoint**: User Story 1 complete - users can discover Phase V features through suggested prompts

---

## Phase 4: User Story 2 - See Visual Task Priority Indicators (Priority: P1) 🎯 MVP

**Goal**: Tasks display colored emoji indicators (🔴🟠🟡⚪) based on priority in all AI responses

**Independent Test**: Create tasks with urgent, high, medium, low priorities and verify each displays correct emoji in AI responses

### Implementation for User Story 2

- [X] T024 [US2] Add "Priority Indicators" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T025 [US2] Add priority emoji mapping table to system prompt (urgent=🔴, high=🟠, medium=🟡, low=⚪)
- [X] T026 [US2] Add Example 1 (Create High Priority Task) from contracts/system-prompt-examples.md to system prompt
- [X] T027 [US2] Add Example 2 (List Tasks with Mixed Metadata) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 2

- [ ] T028 [US2] Create urgent task via ChatKit and verify 🔴 emoji displays in response
- [ ] T029 [P] [US2] Create high priority task and verify 🟠 emoji displays
- [ ] T030 [P] [US2] Create medium priority task and verify 🟡 emoji displays
- [ ] T031 [P] [US2] Create low priority task and verify ⚪ emoji displays
- [ ] T032 [US2] List all tasks and verify priority emoji appears consistently for each task
- [ ] T033 [US2] Update task priority from medium to urgent and verify emoji changes from 🟡 to 🔴
- [ ] T034 [US2] Verify tasks are sorted by priority (urgent first, then high, medium, low) in list responses

**Checkpoint**: User Story 2 complete - priority indicators are visually clear

---

## Phase 5: User Story 3 - View Category and Tag Organization Visually (Priority: P2)

**Goal**: Categories display with 📁 emoji prefix and tags display with # prefix

**Independent Test**: Create tasks with categories and tags, verify each task shows "📁 Category Name" and "Tags: #tag1 #tag2" format

### Implementation for User Story 3

- [X] T035 [US3] Add "Category Display" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T036 [US3] Add "Tag Display" section to system prompt with # prefix formatting
- [X] T037 [US3] Add Example 5 (List with Categories and Tags) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 3

- [ ] T038 [US3] Create task in "Work" category and verify "📁 Work" appears in response
- [ ] T039 [P] [US3] Add tags #urgent #meeting to a task and verify "Tags: #urgent #meeting" appears
- [ ] T040 [US3] List tasks grouped by category and verify 📁 emoji appears for each category header
- [ ] T041 [US3] Create task without category and verify no category indicator appears (graceful omission)
- [ ] T042 [US3] Create task with 5+ tags and verify all tags display with # prefix in consistent format

**Checkpoint**: User Story 3 complete - categories and tags are visually organized

---

## Phase 6: User Story 4 - See Due Dates with Relative Time Formatting (Priority: P2)

**Goal**: Due dates display in human-readable format ("Due today", "Due in 3 days", "Overdue by 2 days")

**Independent Test**: Create tasks with various due dates (today, tomorrow, next week, past date) and verify correct relative format with 📅 or ⚠️ emoji

### Implementation for User Story 4

- [X] T043 [US4] Add "Due Date Display" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T044 [US4] Add relative date formatting rules (7 categories) from research.md to system prompt
- [X] T045 [US4] Update Example 2 in system prompt to include overdue task with ⚠️ emoji

### Manual Testing for User Story 4

- [ ] T046 [US4] Create task due today and verify "📅 Due today at [time]" appears
- [ ] T047 [P] [US4] Create task due tomorrow and verify "📅 Due tomorrow at [time]" appears
- [ ] T048 [P] [US4] Create task due in 5 days and verify "📅 Due in 5 days ([date])" appears
- [ ] T049 [US4] Create overdue task (past due date) and verify "⚠️ Overdue by X days (was [date])" appears
- [ ] T050 [US4] Create task without due date and verify no due date field appears (graceful omission)

**Checkpoint**: User Story 4 complete - due dates are human-readable and actionable

---

## Phase 7: User Story 5 - Understand Recurring Task Patterns (Priority: P3)

**Goal**: Recurring tasks display human-readable patterns ("Repeats weekly on Mon, Wed, Fri") instead of RRULE syntax

**Independent Test**: Create recurring tasks with different patterns (daily, weekly, monthly) and verify human-readable description with 🔄 emoji

### Implementation for User Story 5

- [X] T051 [US5] Add "Recurrence Display" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T052 [US5] Add RRULE humanization patterns (10 common patterns) from research.md to system prompt
- [X] T053 [US5] Add Example 3 (Create Recurring Task) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 5

- [ ] T054 [US5] Create daily recurring task and verify "🔄 Repeats daily" appears
- [ ] T055 [P] [US5] Create weekly recurring task (Mon/Wed/Fri) and verify "🔄 Repeats weekly on Mon, Wed, Fri" appears
- [ ] T056 [P] [US5] Create monthly recurring task (15th) and verify "🔄 Repeats monthly on the 15th" appears
- [ ] T057 [US5] Create non-recurring task and verify no recurrence indicator appears
- [ ] T058 [US5] Create bi-weekly recurring task and verify "🔄 Repeats every 2 weeks on [day]" appears

**Checkpoint**: User Story 5 complete - recurring patterns are understandable

---

## Phase 8: User Story 6 - Get Proactive Feature Suggestions (Priority: P3)

**Goal**: AI suggests advanced features when appropriate ("Would you like to set a priority?" after creating basic task)

**Independent Test**: Create 3 basic tasks without priorities, verify AI suggests organization. Create task with due date, verify AI suggests reminder.

### Implementation for User Story 6

- [X] T059 [US6] Add "Proactive Suggestions" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T060 [US6] Add 6 trigger heuristics from research.md to system prompt (priority, organization, reminder, recurring, tag, search)
- [X] T061 [US6] Add frequency caps (max 1 per response, max 5 per conversation) to system prompt
- [X] T062 [US6] Add Example 8 (Proactive Feature Suggestion) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 6

- [ ] T063 [US6] Create basic task without priority and verify AI suggests "Would you like to set a priority?"
- [ ] T064 [US6] Create 3 tasks without categories and verify AI suggests organizing with categories after 3rd task
- [ ] T065 [US6] Create task with due date but no reminder and verify AI suggests "Should I set a reminder?"
- [ ] T066 [US6] Decline a suggestion and verify AI doesn't repeat same suggestion in next response

**Checkpoint**: User Story 6 complete - proactive suggestions drive feature adoption

---

## Phase 9: User Story 7 - Search Tasks with Relevance Scores (Priority: P3)

**Goal**: Search results show relevance scores (🔍 95% match) and highlighted keywords

**Independent Test**: Create tasks with similar words, search for keyword, verify results show percentages sorted by relevance with keyword highlighted

### Implementation for User Story 7

- [X] T067 [US7] Add "Search Results" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T068 [US7] Add formatting rules (relevance indicator, keyword bolding, sort by score) to system prompt
- [X] T069 [US7] Add Example 4 (Search Tasks) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 7

- [ ] T070 [US7] Search for "meeting" and verify each result shows "🔍 [X]% match" relevance indicator
- [ ] T071 [US7] Verify matching keywords appear in **bold** formatting in search results
- [ ] T072 [US7] Verify search results are sorted by relevance score (highest first)
- [ ] T073 [US7] Search for non-existent term and verify "No tasks found" message appears

**Checkpoint**: User Story 7 complete - search results are informative and ranked

---

## Phase 10: User Story 8 - Consistent Structured Task Lists (Priority: P2)

**Goal**: All task lists use consistent format (numbered, metadata in predictable order)

**Independent Test**: List 10+ tasks with mixed metadata and verify consistent formatting structure

### Implementation for User Story 8

- [X] T074 [US8] Add "Standard Task List Format" section to system prompt in phaseV/backend/app/services/task_server.py:_get_system_instructions()
- [X] T075 [US8] Add task list template with metadata order (priority→category→tags→due date→recurrence) to system prompt
- [X] T076 [US8] Add sorting rules (priority first, then due date) to system prompt
- [X] T077 [US8] Add completed task formatting (~~strikethrough~~ ✅) to system prompt
- [X] T078 [US8] Add Example 6 (Completed Task) and Example 7 (Overdue Tasks) from contracts/system-prompt-examples.md to system prompt

### Manual Testing for User Story 8

- [ ] T079 [US8] List 10+ tasks and verify each follows structure: [Emoji] **Title** (ID: #X) with bullets below
- [ ] T080 [US8] Verify metadata appears in consistent order (category→tags→due date→recurrence) across all tasks
- [ ] T081 [US8] Complete a task and verify title shows ~~strikethrough~~ ✅ formatting
- [ ] T082 [US8] List tasks with varying metadata (some missing categories/tags) and verify graceful omission of empty fields

**Checkpoint**: User Story 8 complete - task lists are scannable and consistent

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, performance checks, and deployment readiness

- [ ] T083 [P] Validate system prompt token count is under 4,000 tokens using tiktoken
- [ ] T084 [P] Test emoji rendering on mobile browsers (iOS 17+ Safari, Android 14+ Chrome)
- [ ] T085 [P] Verify all Markdown formatting renders correctly in ChatKit (bold, strikethrough, lists)
- [ ] T086 Measure AI response time for 5 tasks (should be <3 seconds at p95, <15% increase vs baseline)
- [ ] T087 Compare token consumption before/after (should be <15% increase)
- [ ] T088 [P] Verify system prompt examples cover all Phase V features (priorities, categories, tags, due dates, recurring, search, reminders)
- [ ] T089 [P] Test edge case: task with ALL metadata fields (priority, category, tags, due date, recurrence) - verify readable formatting
- [ ] T090 [P] Test edge case: task titles with Markdown special characters (*, **, #) - verify proper escaping
- [ ] T091 [P] Test edge case: very long task list (50+ tasks) - verify ChatKit handles without breaking
- [ ] T092 Run quickstart.md validation checklist from specs/003-chatkit-ui/quickstart.md
- [X] T093 Document rollback procedure (revert system prompt, revert ChatKit config)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (different sections of same file)
  - OR sequentially in priority order (P1 stories first: US1, US2; then P2: US3, US4, US8; then P3: US5, US6, US7)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Suggested Prompts - P1)**: INDEPENDENT - only modifies frontend config
- **US2 (Priority Indicators - P1)**: INDEPENDENT - only modifies backend system prompt
- **US3 (Category/Tag Display - P2)**: INDEPENDENT - only modifies backend system prompt
- **US4 (Due Date Formatting - P2)**: INDEPENDENT - only modifies backend system prompt
- **US5 (Recurring Patterns - P3)**: INDEPENDENT - only modifies backend system prompt
- **US6 (Proactive Suggestions - P3)**: INDEPENDENT - only modifies backend system prompt
- **US7 (Search Relevance - P3)**: INDEPENDENT - only modifies backend system prompt
- **US8 (Consistent Lists - P2)**: INDEPENDENT - only modifies backend system prompt

**⚠️ IMPORTANT**: While US1 and US2-US8 modify different files (frontend vs backend), US2-US8 all modify THE SAME FILE (system prompt). Therefore:
- US1 can run in parallel with any backend user story
- US2-US8 must be sequential (same file conflicts) OR carefully coordinated with merge strategy

### Within Each User Story

- Implementation tasks before testing tasks
- All manual testing tasks within a story marked [P] can run in parallel (different test scenarios)

### Parallel Opportunities

- **Phase 1 (Setup)**: All T001-T004 can run in parallel [P]
- **Phase 2 (Foundational)**: T005-T008 can run in parallel [P]
- **User Story 1 vs US2-US8**: US1 (frontend) can run in parallel with any backend story
- **Within each user story**: Manual testing tasks marked [P] can run in parallel
- **Phase 11 (Polish)**: T083-T091 can run in parallel [P]

---

## Parallel Example: User Story 2 Manual Testing

```bash
# Launch all browser compatibility tests together:
Task T028: "Create urgent task via ChatKit - Chrome"
Task T029: "Create high priority task - Firefox"
Task T030: "Create medium priority task - Safari"
Task T031: "Create low priority task - Edge"

# All test different scenarios in parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup (validate prerequisites)
2. Complete Phase 2: Foundational (identify files)
3. Complete Phase 3: User Story 1 (suggested prompts - frontend)
4. Complete Phase 4: User Story 2 (priority indicators - backend)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready

**Rationale**: US1+US2 deliver core value - feature discovery + visual priorities

### Incremental Delivery (P1 → P2 → P3)

1. **MVP**: US1 (suggested prompts) + US2 (priority indicators) → Deploy
2. **Enhancement 1**: Add US3 (categories/tags) + US4 (due dates) + US8 (consistent lists) → Deploy
3. **Enhancement 2**: Add US5 (recurring) + US6 (proactive) + US7 (search) → Deploy
4. Each deployment adds value without breaking previous features

### Sequential Strategy (Recommended for single developer)

**Why sequential?**: US2-US8 all modify the same file (system prompt). Sequential avoids merge conflicts.

1. Phase 1: Setup
2. Phase 2: Foundational
3. US1 (frontend - independent)
4. US2 (backend - priority indicators)
5. US3 (backend - categories/tags)
6. US4 (backend - due dates)
7. US8 (backend - consistent lists)
8. US5 (backend - recurring)
9. US6 (backend - proactive suggestions)
10. US7 (backend - search relevance)
11. Phase 11: Polish

**Total time**: ~6-8 hours (1-2 hours implementation + 4-6 hours manual testing)

---

## Notes

- **No database changes**: All tasks are configuration-only (system prompt + frontend config)
- **No new services**: Zero backend logic changes beyond system prompt text
- **No new APIs**: MCP tools remain unchanged (17 tools from Features 001/002)
- **Manual testing required**: Prompt behavior validated through AI interaction, not unit tests
- **[P] tasks**: Different files OR different test scenarios (no dependencies)
- **[Story] label**: Maps task to specific user story for traceability
- **Tests are manual**: No automated test tasks (prompt engineering cannot be unit tested)
- Commit after each user story phase for clean rollback
- Stop at any checkpoint to validate story independently
- Avoid: modifying database, creating new services, changing MCP tool signatures

---

## Success Metrics (Post-Deployment)

Track these metrics after deploying:
- ✅ Suggested prompt click-through rate >5% per prompt (US1)
- ✅ AI response time <3 seconds at p95, <15% increase vs baseline (all stories)
- ✅ Token consumption increase <15% vs baseline (all stories)
- ✅ Zero ChatKit rendering errors from malformed Markdown (all stories)
- ✅ User satisfaction +40% improvement in task visibility surveys (all stories)

---

**Status**: ✅ Tasks ready for implementation - 93 total tasks across 8 user stories
**Estimated Implementation Time**: 6-8 hours (1-2 hours config changes + 4-6 hours manual testing)
**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) = Core feature discovery + visual priorities
