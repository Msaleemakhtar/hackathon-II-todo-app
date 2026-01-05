# ChatKit Start Screen Configuration

**Feature**: 003-chatkit-ui
**Contract Type**: Frontend Configuration Schema
**Date**: 2026-01-05

---

## Overview

This document defines the configuration for the ChatKit start screen, including the greeting message and 8 diverse suggested prompts. Implementation is in the frontend ChatKit component configuration (exact file location TBD based on ChatKit SDK structure).

---

## Greeting Message

**Location**: ChatKit start screen configuration
**Character Limit**: Under 50 words (approximately 250 characters)
**Format**: Plain text (Markdown not supported in greeting)

### Specification

```text
Welcome! I'm your AI task assistant. I can help you manage tasks with priorities, categories, tags, due dates, recurring schedules, search, and reminders. Try a suggestion below or just start chatting!
```

**Character Count**: 209 characters
**Word Count**: 33 words
**Status**: ✅ Meets constraint (under 50 words)

---

## Suggested Prompts

**Count**: Exactly 8 prompts
**Purpose**: Demonstrate diverse Phase V capabilities
**Coverage**: Must include priority, category, tag, due date, recurrence, search, reminder, and multi-feature examples

### Prompt 1: Urgent Task Creation

```text
🔴 Create an urgent task to submit budget proposal by today 5pm
```

**Feature Demonstrated**: Priority (urgent) + Due date (relative time)
**Expected AI Action**: Call `add_task` with priority="urgent", due_date, title
**MCP Tool**: `add_task`

---

### Prompt 2: Category Viewing

```text
📁 Show me all my work tasks
```

**Feature Demonstrated**: Category filtering
**Expected AI Action**: Call `list_tasks` with category filter
**MCP Tool**: `list_tasks`

---

### Prompt 3: Tag Filtering

```text
#meeting Show tasks tagged as meetings
```

**Feature Demonstrated**: Tag filtering
**Expected AI Action**: Call `list_tasks` with tag filter
**MCP Tool**: `list_tasks`

---

### Prompt 4: Due Date Scheduling

```text
📅 Show tasks due this week
```

**Feature Demonstrated**: Due date filtering (relative time)
**Expected AI Action**: Call `get_upcoming_tasks` with days=7 or `list_tasks` with due_before filter
**MCP Tool**: `get_upcoming_tasks` or `list_tasks`

---

### Prompt 5: Recurring Task Creation

```text
🔄 Create a recurring task to review emails every Monday at 9am
```

**Feature Demonstrated**: Recurring task with specific schedule
**Expected AI Action**: Call `add_task` with recurrence_rule="FREQ=WEEKLY;BYDAY=MO", due_date
**MCP Tool**: `add_task`

---

### Prompt 6: Full-Text Search

```text
🔍 Search for tasks about budget
```

**Feature Demonstrated**: Full-text search
**Expected AI Action**: Call `search_tasks` with query="budget"
**MCP Tool**: `search_tasks`

---

### Prompt 7: Reminder Setting

```text
⏰ Set a reminder for task #42, 30 minutes before
```

**Feature Demonstrated**: Reminder scheduling
**Expected AI Action**: Call `set_reminder` with task_id=42, remind_before_minutes=30
**MCP Tool**: `set_reminder`

---

### Prompt 8: Multi-Feature Query

```text
🔴 Show urgent tasks due today with category Work
```

**Feature Demonstrated**: Multi-filter query (priority + due date + category)
**Expected AI Action**: Call `list_tasks` with priority="urgent", due_before=today, category filter
**MCP Tool**: `list_tasks`

---

## Configuration Schema (JSON)

**Note**: Exact schema depends on ChatKit SDK version. This is a reference implementation.

```json
{
  "startScreen": {
    "greeting": "Welcome! I'm your AI task assistant. I can help you manage tasks with priorities, categories, tags, due dates, recurring schedules, search, and reminders. Try a suggestion below or just start chatting!",
    "suggestedPrompts": [
      "🔴 Create an urgent task to submit budget proposal by today 5pm",
      "📁 Show me all my work tasks",
      "#meeting Show tasks tagged as meetings",
      "📅 Show tasks due this week",
      "🔄 Create a recurring task to review emails every Monday at 9am",
      "🔍 Search for tasks about budget",
      "⏰ Set a reminder for task #42, 30 minutes before",
      "🔴 Show urgent tasks due today with category Work"
    ]
  }
}
```

---

## Design Rationale

### Why These 8 Prompts?

1. **Priority Coverage**: Prompts 1 and 8 demonstrate priority feature (urgent)
2. **Organization Coverage**: Prompts 2 and 3 show category and tag filtering
3. **Time Management**: Prompts 4, 5, and 7 cover due dates, recurring, and reminders
4. **Search**: Prompt 6 demonstrates full-text search
5. **Complexity Progression**: Starts simple (Prompt 1), ends complex (Prompt 8 - multi-filter)

### Why Emoji Prefixes?

- **Visual Distinction**: Makes each prompt immediately recognizable
- **Feature Association**: Users learn emoji = feature (🔴 = urgent, 📁 = category, etc.)
- **Engagement**: Colorful prompts are more clickable than plain text
- **Consistency**: Matches emoji used in AI responses

### Why "Try a suggestion below or just start chatting!"?

- **Low Barrier**: Users can ignore suggestions and type naturally
- **Flexibility**: Doesn't force users into predefined commands
- **Discovery**: Encourages exploration without pressure

---

## A/B Testing Recommendations (Future)

**Metrics to Track**:
- Click-through rate per prompt (target: >5% each)
- First-interaction type (suggested vs. custom)
- Feature adoption after suggestion click

**Variants to Test**:
- Prompt ordering (simple-to-complex vs. complex-to-simple)
- Emoji vs. text-only prompts
- Greeting tone (friendly vs. professional)
- Number of prompts (6 vs. 8 vs. 10)

**Out of Scope for Feature 003**: A/B testing infrastructure

---

## Validation Checklist

Before deployment, verify:
- ✅ Greeting is under 50 words
- ✅ Exactly 8 suggested prompts
- ✅ All 8 prompts execute successfully (no tool errors)
- ✅ Prompts cover all Phase V features (priorities, categories, tags, due dates, recurring, search, reminders)
- ✅ Emoji render correctly across browsers (iOS, Android, Windows, macOS)
- ✅ Prompts use clear, natural language
- ✅ No typos or grammar errors

---

## Implementation Notes

**Frontend File Locations (TBD)**:
- Option 1: `frontend/components/chat/ChatInterface.tsx` (if config is inline)
- Option 2: `frontend/lib/chatkit-config.ts` (if config is externalized)
- Option 3: `frontend/app/chat/page.tsx` (if config is at page level)

**Backend Changes**: NONE (greeting and prompts are frontend-only)

**Environment Variables**: NONE (static config, not environment-dependent)

---

## Future Enhancements (Out of Scope)

**Dynamic Prompts**:
- User-specific suggestions based on past behavior
- Time-aware prompts (e.g., "Good morning! Check your tasks for today")
- Onboarding flow for new users (show simpler prompts first)

**Internationalization**:
- Translated greeting and prompts for non-English users
- Locale-aware date formatting in prompts

**Customization**:
- User-defined suggested prompts
- Hiding/reordering prompts via settings

---

**Status**: ✅ Contract complete - Ready for frontend implementation
