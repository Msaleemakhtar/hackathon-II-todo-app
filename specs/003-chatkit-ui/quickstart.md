# Quick Start: ChatKit UI Enhancements

**Feature**: 003-chatkit-ui
**Implementation Time**: ~1-2 hours
**Complexity**: Low (configuration-only changes)
**Date**: 2026-01-05

---

## Overview

This feature enhances the ChatKit UI with visual task indicators and improved discoverability. **No database changes, no new APIs, no new services** - only prompt engineering and frontend configuration updates.

**What changes**:
1. Backend system prompt (formatting guidelines + examples)
2. Frontend greeting message (string constant)
3. Frontend suggested prompts (array of 8 strings)

**What doesn't change**:
- Database schema (zero migrations)
- MCP tools (17 tools remain unchanged)
- API endpoints (no new routes)
- Docker/Kubernetes configuration
- CI/CD pipelines

---

## Prerequisites

Before implementing this feature, ensure:
- ✅ Phase V Features 001 & 002 are deployed (17 MCP tools functional)
- ✅ ChatKit interface is operational
- ✅ OpenAI Agents SDK is configured
- ✅ Neon PostgreSQL has `tasks_phaseiii`, `categories`, `tags_phasev`, `task_tags` tables

---

## Implementation Steps

### Step 1: Update Backend System Prompt (15 minutes)

**File**: `backend/app/services/task_server.py` (or similar location)
**Method**: `_get_system_instructions()` or equivalent

**Action**: Replace or enhance the system prompt with formatting guidelines and examples.

**Reference Contract**: `specs/003-chatkit-ui/contracts/system-prompt-schema.md`

**Implementation**:
```python
def _get_system_instructions() -> str:
    return """
You are a helpful task management assistant. You help users manage their tasks through natural conversation.
You have access to 17 MCP tools for managing tasks, categories, tags, search, and reminders.

## Task Display Formatting

When displaying tasks, ALWAYS use this consistent format:

**Priority Indicators**:
- Urgent: 🔴
- High: 🟠
- Medium: 🟡 (default)
- Low: ⚪

**Category Display**:
- Format: 📁 Category Name

**Tag Display**:
- Format: Tags: #tag1 #tag2 #tag3

**Due Date Display**:
- Due today: 📅 Due today at [TIME]
- Due tomorrow: 📅 Due tomorrow at [TIME]
- Due in X days: 📅 Due in X days ([DATE])
- Overdue: ⚠️ Overdue by X days (was [DATE])

**Recurrence Display**:
- Daily: 🔄 Repeats daily
- Weekly: 🔄 Repeats weekly on [DAYS]
- Monthly: 🔄 Repeats monthly on the [Nth]

**Search Results**:
- Format: 🔍 [X]% match - [TASK]
- Bold matching keywords

**Task List Format**:
1. [EMOJI] **Task Title** (ID: #123)
   - 📁 Category (if present)
   - Tags: #tag1 #tag2 (if present)
   - 📅 Due date (if present)
   - 🔄 Recurrence (if present)

## Example: Create High Priority Task

User: "Add a high priority task to finish report by Friday 5pm"
Assistant:
I've created your task:

🟠 **Finish report** (ID: #42)
- 📅 Due Friday at 5:00 PM

[Add 4+ more examples covering categories, tags, recurring, search]
"""
```

**Validation**:
```bash
cd backend
# Restart backend to load new prompt
uv run python -m app.main
# Test by creating a high priority task via ChatKit
```

---

### Step 2: Update Frontend Greeting Message (5 minutes)

**File**: `frontend/components/chat/ChatInterface.tsx` (or ChatKit config file)
**Property**: `greeting` or `startScreen.greeting`

**Action**: Update greeting to mention Phase V capabilities.

**New Greeting**:
```text
Welcome! I'm your AI task assistant. I can help you manage tasks with priorities, categories, tags, due dates, recurring schedules, search, and reminders. Try a suggestion below or just start chatting!
```

**Implementation Example (TypeScript)**:
```typescript
const chaticConfig = {
  startScreen: {
    greeting: "Welcome! I'm your AI task assistant. I can help you manage tasks with priorities, categories, tags, due dates, recurring schedules, search, and reminders. Try a suggestion below or just start chatting!",
    // ...
  }
};
```

---

### Step 3: Update Suggested Prompts (10 minutes)

**File**: Same as Step 2
**Property**: `suggestedPrompts` or `startScreen.suggestedPrompts`

**Action**: Replace with 8 diverse prompts.

**New Suggested Prompts**:
```typescript
const suggestedPrompts = [
  "🔴 Create an urgent task to submit budget proposal by today 5pm",
  "📁 Show me all my work tasks",
  "#meeting Show tasks tagged as meetings",
  "📅 Show tasks due this week",
  "🔄 Create a recurring task to review emails every Monday at 9am",
  "🔍 Search for tasks about budget",
  "⏰ Set a reminder for task #42, 30 minutes before",
  "🔴 Show urgent tasks due today with category Work"
];
```

**Reference Contract**: `specs/003-chatkit-ui/contracts/chatkit-startscreen-config.md`

---

### Step 4: Manual Testing (30 minutes)

**Browser Compatibility Testing**:
1. Open ChatKit in Chrome 120+ → verify emoji render
2. Open ChatKit in Firefox 120+ → verify emoji render
3. Open ChatKit in Safari 17+ (macOS) → verify emoji render
4. Open ChatKit in mobile Safari (iOS 17+) → verify emoji render
5. Open ChatKit in mobile Chrome (Android 14+) → verify emoji render

**Suggested Prompt Testing**:
1. Click each of the 8 suggested prompts
2. Verify each prompt executes successfully (no errors)
3. Verify AI responses follow formatting guidelines
4. Verify emoji indicators display correctly (🔴🟠🟡⚪📁📅⚠️🔄🔍)

**Formatting Testing**:
1. Create tasks with different priorities → verify emoji indicators
2. Create tasks with categories → verify 📁 prefix
3. Create tasks with tags → verify # prefix
4. Create tasks with due dates → verify relative formatting (Due today, Due in 3 days)
5. Create recurring tasks → verify 🔄 human-readable pattern
6. Search tasks → verify relevance scores and keyword highlighting
7. Complete tasks → verify strikethrough formatting (~~Task~~ ✅)

**Test Scenarios** (from spec.md User Stories):
- User Story 1: Verify 8 suggested prompts are visible on start screen
- User Story 2: Create urgent/high/medium/low tasks, verify correct emoji
- User Story 3: Create tasks with categories/tags, verify 📁 and # formatting
- User Story 4: Create tasks with due dates (today, tomorrow, future), verify relative time
- User Story 5: Create recurring tasks (daily, weekly), verify human-readable description
- User Story 6: Ignore proactive suggestions (verify AI doesn't repeat same suggestion)
- User Story 7: Search tasks, verify relevance scores and keyword highlighting
- User Story 8: List 10+ tasks, verify consistent formatting

---

### Step 5: Performance Verification (10 minutes)

**Token Count Check**:
```python
import tiktoken

def count_tokens(text: str) -> int:
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(enc.encode(text))

system_prompt = """[paste your system prompt here]"""
token_count = count_tokens(system_prompt)
print(f"System prompt token count: {token_count}")
# MUST be under 4,000 tokens
```

**Response Time Check**:
- Create 5 tasks with varying complexity
- Measure AI response time for each (should be <3 seconds at p95)
- Compare to baseline before feature (should be <15% increase)

**Token Consumption Check**:
- Create 10 tasks and retrieve their formatted responses
- Compare token usage vs. baseline (should be <15% increase)

---

## Deployment

**Backend Deployment**:
```bash
cd backend
docker build -t todo-backend-chatkit:latest .
# OR kubectl rollout restart deployment/todo-backend (if using Kubernetes)
```

**Frontend Deployment**:
```bash
cd frontend
bun run build
docker build -t todo-frontend-chatkit:latest .
# OR kubectl rollout restart deployment/todo-frontend (if using Kubernetes)
```

**Verification Post-Deployment**:
1. Visit ChatKit UI
2. Verify greeting message displays new text
3. Verify 8 suggested prompts are visible
4. Click a suggested prompt → verify it executes successfully
5. Create a high priority task → verify 🟠 emoji displays
6. List tasks → verify consistent formatting

---

## Rollback Plan

**If formatting is broken**:
1. Revert backend system prompt to previous version
2. Restart backend pods/containers
3. Test ChatKit → verify basic functionality restored

**If suggested prompts fail**:
1. Revert frontend ChatKit config to previous prompts
2. Rebuild frontend
3. Test ChatKit → verify prompts execute successfully

**If emoji don't render**:
- Check browser version (requires Chrome 120+, Firefox 120+, Safari 17+)
- Check device OS (requires iOS 17+, Android 14+ for mobile)
- Fallback: Replace emoji with text labels (e.g., [URGENT] instead of 🔴)

---

## Troubleshooting

**Issue**: AI doesn't follow formatting guidelines

**Solution**:
1. Check system prompt is correctly loaded (add debug logging)
2. Verify examples are included in prompt (AI learns from examples)
3. Add more examples for edge cases (e.g., tasks with ALL metadata fields)
4. Increase prompt clarity (be more explicit about ALWAYS using format)

---

**Issue**: Suggested prompts return errors

**Solution**:
1. Check MCP tools are functional (test via direct API calls)
2. Verify prompts use correct tool parameters (e.g., task_id must exist)
3. Update prompts to use valid test data (e.g., task #42 must exist, or use dynamic task IDs)

---

**Issue**: Emoji don't render correctly

**Solution**:
1. Verify emoji are Unicode 9.0 compatible (older emojis have better support)
2. Test on different browsers/devices
3. Add fallback text for unsupported devices (e.g., [URGENT] 🔴)

---

**Issue**: System prompt exceeds 4,000 token limit

**Solution**:
1. Remove least important examples (keep minimum 5)
2. Shorten formatting guidelines (use bullet points instead of sentences)
3. Compress examples (remove extra whitespace, shorten task titles)
4. Split examples into separate "few-shot learning" mechanism if supported by SDK

---

## Success Metrics

After deploying, monitor these metrics:
- ✅ Suggested prompt click-through rate >5% per prompt
- ✅ AI response time <3 seconds at p95 (no degradation)
- ✅ Token consumption increase <15% vs. baseline
- ✅ Zero ChatKit rendering errors (no malformed Markdown)
- ✅ User satisfaction survey shows +40% improvement in task visibility

---

## Next Steps

After successful deployment:
1. Monitor user feedback on suggested prompts (iterate based on click-through data)
2. A/B test different prompt variations (e.g., emoji vs. text-only)
3. Consider internationalization (translate greeting/prompts)
4. Plan Phase 2: Widget-based UI (interactive priority badges, category dropdowns)

---

**Status**: ✅ Quick start guide complete - Ready for implementation
