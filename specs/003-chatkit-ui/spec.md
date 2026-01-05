# Feature Specification: ChatKit UI Enhancements

**Feature Branch**: `003-chatkit-ui`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "ChatKit UI Enhancements - Enhanced system prompts, visual indicators for priorities, categories, tags, due dates, and improved suggested prompts"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Advanced Task Features Through Suggested Prompts (Priority: P1)

As a new user opening the ChatKit interface for the first time, I see 8 diverse suggested prompts that showcase advanced capabilities like priorities, categories, tags, due dates, recurring tasks, search, and reminders. I can click any prompt to immediately try that feature.

**Why this priority**: This is the primary discovery mechanism. Without updated suggested prompts, users won't know about Phase V features and will continue using the app as a basic task manager.

**Independent Test**: Can be tested by opening the ChatKit interface and verifying that 8 suggested prompts are displayed with diverse examples. Each prompt should execute successfully when clicked.

**Acceptance Scenarios**:

1. **Given** I am a new user opening the chat interface, **When** the start screen loads, **Then** I see a greeting message mentioning "priorities, categories, tags, due dates, recurring schedules, search, and reminders"

2. **Given** I see the start screen, **When** I review the suggested prompts, **Then** I see 8 prompts covering: urgent task creation, category viewing, tag filtering, due date scheduling, recurring tasks, search, reminders, and multi-filter queries

3. **Given** I click the "🔴 Create urgent task" suggested prompt, **When** the AI processes my request, **Then** a task is created with urgent priority and the response includes a 🔴 emoji indicator

4. **Given** I click the "🔍 Search tasks" suggested prompt, **When** the AI executes the search, **Then** results are displayed with relevance scores and matching keywords highlighted

---

### User Story 2 - See Visual Task Priority Indicators (Priority: P1)

As a user managing multiple tasks, I want to quickly identify urgent and high-priority tasks through visual indicators (colored emojis) so I can focus on what matters most without reading every task detail.

**Why this priority**: Visual priority indicators dramatically improve task scanning efficiency. Users can identify urgent work at a glance, which is the core value of a priority system.

**Independent Test**: Create tasks with different priorities (urgent, high, medium, low) and verify each displays the correct emoji indicator (🔴, 🟠, 🟡, ⚪) in all AI responses.

**Acceptance Scenarios**:

1. **Given** I create a new urgent task, **When** the AI confirms creation, **Then** the response includes 🔴 emoji before the task title

2. **Given** I list all my tasks, **When** the AI displays the list, **Then** each task shows its priority emoji (🔴 urgent, 🟠 high, 🟡 medium, ⚪ low) consistently

3. **Given** I have tasks with mixed priorities, **When** the AI lists them, **Then** urgent and high priority tasks appear first in the list

4. **Given** I update a task's priority from medium to urgent, **When** the AI confirms the update, **Then** the response changes the emoji from 🟡 to 🔴

---

### User Story 3 - View Category and Tag Organization Visually (Priority: P2)

As a user organizing tasks with categories and tags, I want to see visual indicators (📁 for categories, # for tags) in task displays so I can quickly understand how my tasks are organized without reading full descriptions.

**Why this priority**: After priorities, categories and tags are the next most important organizational features. Visual indicators make organized tasks more scannable and encourage adoption of these features.

**Independent Test**: Create tasks with categories and tags, then list them to verify each task displays 📁 Category Name and #tag1 #tag2 format consistently.

**Acceptance Scenarios**:

1. **Given** I create a task in the "Work" category, **When** the AI displays the task, **Then** it shows "📁 Work" in the task details

2. **Given** I add tags #urgent and #meeting to a task, **When** the AI displays the task, **Then** it shows "Tags: #urgent #meeting" in the task details

3. **Given** I list tasks grouped by category, **When** the AI displays the list, **Then** tasks are visually grouped under their 📁 category headers

4. **Given** I create a task without a category, **When** the AI displays it, **Then** no category indicator appears (graceful handling of optional fields)

---

### User Story 4 - See Due Dates with Relative Time Formatting (Priority: P2)

As a user with time-sensitive tasks, I want due dates displayed in human-readable relative format ("Due today", "Due in 3 days", "Overdue by 2 days") so I can quickly assess urgency without calculating dates manually.

**Why this priority**: Relative time formatting makes due dates actionable. "Due today" is instantly meaningful, while "2026-01-05T14:00:00Z" requires mental calculation.

**Independent Test**: Create tasks with various due dates (today, tomorrow, next week, past date) and verify each displays the correct relative time format with appropriate emoji (📅 for upcoming, ⚠️ for overdue).

**Acceptance Scenarios**:

1. **Given** I create a task due today, **When** the AI displays the task, **Then** it shows "📅 Due today at [time]"

2. **Given** I create a task due tomorrow, **When** the AI displays the task, **Then** it shows "📅 Due tomorrow at [time]"

3. **Given** I create a task due in 5 days, **When** the AI displays the task, **Then** it shows "📅 Due in 5 days ([full date])"

4. **Given** I have an overdue task, **When** the AI displays it, **Then** it shows "⚠️ Overdue by X days" with the overdue indicator

5. **Given** I create a task without a due date, **When** the AI displays it, **Then** it shows "📅 No deadline" or omits the due date field

---

### User Story 5 - Understand Recurring Task Patterns (Priority: P3)

As a user creating recurring tasks, I want to see the recurrence pattern translated to human-readable format ("Repeats weekly on Mon, Wed, Fri") so I can verify my recurring schedule is correct without understanding RRULE syntax.

**Why this priority**: While important for recurring task users, this affects a smaller subset of users. It's essential for feature adoption but can come after core visual indicators.

**Independent Test**: Create recurring tasks with different patterns (daily, weekly with specific days, monthly) and verify each displays human-readable recurrence description with 🔄 emoji.

**Acceptance Scenarios**:

1. **Given** I create a daily recurring task, **When** the AI displays the task, **Then** it shows "🔄 Repeats daily"

2. **Given** I create a weekly recurring task for Mon/Wed/Fri, **When** the AI displays the task, **Then** it shows "🔄 Repeats weekly on Mon, Wed, Fri"

3. **Given** I create a monthly recurring task on the 15th, **When** the AI displays the task, **Then** it shows "🔄 Repeats monthly on the 15th"

4. **Given** I create a non-recurring task, **When** the AI displays it, **Then** no recurrence indicator appears

---

### User Story 6 - Get Proactive Feature Suggestions (Priority: P3)

As a user creating basic tasks, I receive helpful prompts from the AI suggesting advanced features I haven't tried yet ("Would you like to set a priority?" or "Should I set a reminder for this task?") so I discover capabilities organically through conversation.

**Why this priority**: Proactive suggestions drive feature adoption, but they must not annoy users. This is lower priority because users can discover features through suggested prompts and documentation.

**Independent Test**: Create 3 basic tasks without advanced features, verify AI suggests organization after 3rd task. Create task with due date, verify AI suggests reminder.

**Acceptance Scenarios**:

1. **Given** I create a basic task without priority or category, **When** the AI confirms creation, **Then** it asks "Would you like to set a priority or category for this task?"

2. **Given** I have created 3 or more tasks without categories, **When** I list my tasks, **Then** the AI suggests "I notice you have several tasks. Would you like to organize them with categories?"

3. **Given** I create a task with a due date but no reminder, **When** the AI confirms creation, **Then** it asks "Should I set a reminder for this task?"

4. **Given** I receive a proactive suggestion, **When** I decline or ignore it, **Then** the AI doesn't repeat the same suggestion in the next response (avoids annoyance)

---

### User Story 7 - Search Tasks with Relevance Scores (Priority: P3)

As a user searching for specific tasks, I want to see search results with relevance scores (🔍 95% match) and matching keywords highlighted so I can quickly identify the most relevant results.

**Why this priority**: Search is a power-user feature. While valuable, it's less critical than basic visual indicators that benefit all users every time they view tasks.

**Independent Test**: Create several tasks with similar words, search for a keyword, verify results show relevance percentages sorted by relevance with the keyword highlighted in bold.

**Acceptance Scenarios**:

1. **Given** I search for "meeting" across my tasks, **When** the AI returns results, **Then** each result shows "🔍 [X]% match" relevance indicator

2. **Given** search results are displayed, **When** I review them, **Then** matching keywords appear in **bold** formatting

3. **Given** multiple results are found, **When** the AI displays them, **Then** they are sorted by relevance score (highest first)

4. **Given** no tasks match my search, **When** the AI responds, **Then** it shows "No tasks found matching '[query]'" with a helpful suggestion

---

### User Story 8 - Consistent Structured Task Lists (Priority: P2)

As a user listing multiple tasks, I want to see them displayed in a consistent, scannable format (numbered, with all metadata in predictable locations) so I can quickly review my task list without parsing different formats.

**Why this priority**: List formatting affects every user interaction. Consistency is critical for usability, making this high priority despite being a "polish" feature.

**Independent Test**: List 10+ tasks with mixed metadata (some with categories, some with tags, varying priorities) and verify all use consistent formatting with metadata in the same order.

**Acceptance Scenarios**:

1. **Given** I list multiple tasks, **When** the AI displays them, **Then** each task follows this structure: [Priority Emoji] **Task Title** (ID: #123) with metadata bullets below

2. **Given** tasks have different metadata (some have categories, some don't), **When** the AI displays them, **Then** metadata appears in consistent order: Category, Tags, Due Date, Recurrence

3. **Given** I list completed tasks, **When** the AI displays them, **Then** completed task titles show ~~strikethrough~~ formatting

4. **Given** the task list is very long (10+ tasks), **When** the AI displays it, **Then** tasks are numbered for easy reference

---

### Edge Cases

- **What happens when a task has all possible metadata** (priority, category, multiple tags, due date, recurrence, reminder)?
  - AI should display all fields in consistent order without cluttering the response
  - Test with a maximally-configured task to ensure formatting remains readable

- **How does the system handle emoji rendering on different devices/browsers?**
  - Emojis should be widely-supported Unicode characters
  - Text fallbacks (e.g., [URGENT] prefix) should be considered for devices without emoji support
  - Test on iOS, Android, Windows, macOS browsers

- **What if the AI response exceeds ChatKit's message length limit?**
  - For very long task lists (50+ tasks), AI should paginate or summarize
  - Test with 100 tasks to verify response doesn't break ChatKit rendering

- **How does the system handle tasks with special characters in titles/descriptions?**
  - Markdown special characters (*, **, #, etc.) should be escaped properly
  - Test with task titles containing markdown syntax to ensure they don't break formatting

- **What happens when suggested prompts fail to execute?**
  - AI should return a clear error message with suggested fixes
  - Test by simulating tool failures (e.g., database connection issues)

- **How does the AI handle proactive suggestions if a user consistently ignores them?**
  - AI should reduce suggestion frequency after multiple ignored prompts
  - Balance between feature discovery and avoiding annoyance

- **What if a user creates a task with invalid RRULE syntax?**
  - AI should catch the error before calling add_task
  - Provide corrected RRULE example in error message

- **How are very long category/tag names displayed?**
  - Names should truncate gracefully in list views
  - Full names should appear in detailed single-task views

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST update the backend AI system prompt to include Phase V feature awareness (priorities, categories, tags, due dates, recurring tasks, search, reminders)

- **FR-002**: System MUST include visual formatting guidelines in the system prompt specifying emoji indicators for priorities (🔴 urgent, 🟠 high, 🟡 medium, ⚪ low), categories (📁), tags (#), due dates (📅 upcoming, ⚠️ overdue), recurrence (🔄), and search (🔍)

- **FR-003**: System MUST update the frontend ChatKit greeting to mention available Phase V capabilities in a concise, welcoming message (under 50 words)

- **FR-004**: System MUST provide 8 diverse suggested prompts on the ChatKit start screen demonstrating: urgent task creation, category filtering, tag filtering, due date scheduling, recurring tasks, search, reminders, and multi-feature queries

- **FR-005**: AI MUST format task responses using consistent Markdown structure with priority emoji, bold title, task ID, and indented metadata bullets (category, tags, due date, recurrence)

- **FR-006**: AI MUST display due dates in human-readable relative format ("Due today", "Due tomorrow", "Due in X days", "Overdue by X days") rather than raw ISO timestamps

- **FR-007**: AI MUST translate RFC 5545 RRULE patterns to human-readable descriptions ("Repeats daily", "Repeats weekly on Mon, Wed", "Repeats monthly on the 15th")

- **FR-008**: AI MUST display search results with relevance scores as percentages (🔍 95% match) and highlight matching keywords using **bold** Markdown

- **FR-009**: AI MUST include proactive feature suggestions (maximum 1 per response) at appropriate times: after basic task creation, after 3+ uncategorized tasks, and after setting due dates

- **FR-010**: AI MUST sort task lists by priority when displaying multiple tasks (urgent first, then high, medium, low)

- **FR-011**: System MUST keep the updated system prompt under 4,000 tokens to preserve conversation history context window

- **FR-012**: AI MUST use strikethrough formatting (~~text~~) for completed tasks in list displays

- **FR-013**: System MUST maintain backward compatibility with existing ChatKit configuration (no breaking changes to API endpoints or authentication)

### Key Entities

This feature does not introduce new data entities. It enhances the presentation of existing entities:

- **Task** (existing): Enhanced display with emoji indicators for priority, formatted due dates, human-readable recurrence patterns
- **Category** (existing): Display with 📁 emoji prefix
- **Tag** (existing): Display with # prefix
- **Search Result** (existing): Enhanced display with relevance scores and highlighted keywords

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users discover and try at least one advanced Phase V feature (priority, category, tag, or search) within their first 10 chat interactions (target: 80% of new users)

- **SC-002**: Average conversation length increases by 30% compared to pre-enhancement baseline, indicating deeper engagement with organized task management

- **SC-003**: Task organization adoption rate reaches 60% (percentage of users who create at least 1 category or tag within first week)

- **SC-004**: Due date usage increases to 50% of created tasks (up from estimated 10% baseline without prominent suggested prompts)

- **SC-005**: AI response time remains under 3 seconds at p95 latency (no performance degradation from enhanced formatting)

- **SC-006**: Zero increase in AI response token consumption above 10% compared to baseline (efficient formatting guidelines)

- **SC-007**: User satisfaction with task visibility and organization improves by 40% in post-feature surveys (5-point scale)

- **SC-008**: Support tickets related to "how to use priorities/categories/tags" decrease by 60% (improved discoverability through suggested prompts)

- **SC-009**: All 8 suggested prompts have >5% click-through rate within first week (validates prompt diversity and relevance)

- **SC-010**: Zero ChatKit rendering errors from malformed Markdown or emoji handling (formatting reliability)

## Assumptions

- **ASSUMPTION-001**: Users primarily interact with the application through the ChatKit conversational interface (not a traditional task list UI)

- **ASSUMPTION-002**: The underlying LLM (GPT-3.5/GPT-4) reliably follows system prompt formatting guidelines

- **ASSUMPTION-003**: All 18 Phase V MCP tools (from Features 001 & 002) are functional and deployed

- **ASSUMPTION-004**: Users access ChatKit from devices that support standard Unicode emojis

- **ASSUMPTION-005**: Current system prompt token count is approximately 3,200 tokens, leaving headroom for 600-800 token additions

- **ASSUMPTION-006**: ChatKit React SDK (v1.4.0) supports custom start screen configuration with greeting and suggested prompts

- **ASSUMPTION-007**: No Helm chart changes are required beyond restarting backend pods to load new system prompt

- **ASSUMPTION-008**: Markdown formatting (bold, strikethrough, bullet points) renders correctly in ChatKit React component

- **ASSUMPTION-009**: Users prefer conversational proactive suggestions over tooltip/modal-based feature discovery

- **ASSUMPTION-010**: Performance impact from formatting logic (emoji injection, relative date calculation, RRULE parsing) is negligible (<50ms per response)

## Out of Scope

- **ChatKit widget-based UI** (interactive buttons, clickable badges, dropdown menus)
- **Custom color schemes or theme customization** beyond ChatKit's standard light/dark mode
- **Voice input/output or accessibility enhancements** (screen reader optimization, keyboard navigation)
- **Mobile-specific UI optimizations**
- **Real-time collaborative features** (live cursor tracking, simultaneous editing)
- **Automated task list views** outside the conversational interface
- **Natural language processing improvements** beyond what the LLM provides
- **Backend MCP tool changes or additions**
- **Database schema modifications**
- **Authentication or authorization changes**
- **Internationalization or localization**
- **Analytics or telemetry** for tracking feature usage

## Dependencies

- **Feature 001 (Foundation + API)**: ✅ Completed - Required for enhanced task model
- **Feature 002 (Event-Driven Architecture)**: ✅ Completed - Required for 18 MCP tools
- **ChatKit React SDK v1.4.0+**: ✅ Installed
- **OpenAI Agents SDK 0.6.3+**: ✅ Installed
- **Neon PostgreSQL Database**: ✅ Operational
- **Kubernetes Cluster**: ✅ Operational

## Risks

- **RISK-001**: System prompt may exceed 4,000 token limit, truncating conversation history
  - **Mitigation**: Use concise bullet points; target 3,500 tokens max; test token count

- **RISK-002**: AI may not consistently follow formatting guidelines
  - **Mitigation**: Include 5+ example responses in system prompt; test multiple conversation flows

- **RISK-003**: Emoji rendering may fail on older devices
  - **Mitigation**: Use widely-supported emoji characters from Unicode 9.0 (2016)

- **RISK-004**: Proactive suggestions may annoy users if too frequent
  - **Mitigation**: Limit to 1 suggestion per response; use intelligent triggers

- **RISK-005**: ChatKit may have message length limits for very long task lists
  - **Mitigation**: Test with 50+ tasks; implement pagination for large lists

- **RISK-006**: Suggested prompts may not resonate with users
  - **Mitigation**: User testing; track click-through rates; iterate based on data

- **RISK-007**: Markdown special characters in task titles may break formatting
  - **Mitigation**: Test with special characters; document escaping requirements

- **RISK-008**: Performance degradation from additional processing
  - **Mitigation**: Benchmark p95 response times; ensure <3s target
