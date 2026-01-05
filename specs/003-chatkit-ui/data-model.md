# Data Model: ChatKit UI Enhancements

**Feature**: 003-chatkit-ui
**Date**: 2026-01-05
**Status**: Design Phase

---

## Overview

**IMPORTANT**: This feature does NOT introduce new database entities, tables, or columns. All data models already exist from Phase V Features 001 & 002. This document describes **presentation-only enhancements** for how existing data is formatted and displayed in AI responses.

---

## Existing Data Models (Reference Only)

### Task Model (Phase V)

**Table**: `tasks_phaseiii`
**Source**: Implemented in Phase V Feature 001/002

**Schema**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks_phaseiii"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: str | None = None
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Phase V enhanced fields (Feature 002)
    priority: str | None = Field(default="medium")  # urgent, high, medium, low
    due_date: datetime | None = None
    category_id: int | None = Field(default=None, foreign_key="categories.id")
    recurrence_rule: str | None = None  # RFC 5545 RRULE format
    reminder_sent: bool = Field(default=False)
    search_vector: str | None = None  # PostgreSQL tsvector for full-text search
```

**Presentation Enhancements** (NOT stored in DB):
- **Priority Emoji Mapping**: Translate `priority` field to emoji in AI responses
  - `urgent` → 🔴
  - `high` → 🟠
  - `medium` → 🟡
  - `low` → ⚪
- **Relative Due Date Formatting**: Convert `due_date` timestamp to human-readable format
  - Examples: "Due today at 2:00 PM", "Due in 3 days", "Overdue by 2 days"
- **RRULE Humanization**: Translate `recurrence_rule` from RFC 5545 to natural language
  - Examples: "FREQ=DAILY" → "Repeats daily", "FREQ=WEEKLY;BYDAY=MO,WE,FR" → "Repeats weekly on Mon, Wed, Fri"
- **Completion Formatting**: Show `is_completed` tasks with strikethrough
  - ~~Task Title~~ ✅

---

### Category Model (Phase V)

**Table**: `categories`
**Source**: Implemented in Phase V Feature 002

**Schema**:
```python
class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str
    color: str | None = None  # Hex color code (e.g., "#FF5733")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

**Presentation Enhancements** (NOT stored in DB):
- **Category Icon**: Prefix category name with 📁 emoji
  - Example: "📁 Work", "📁 Personal", "📁 Shopping"
- **Color Display**: Color field NOT used in text-based AI responses (reserved for future UI widgets)

---

### Tag Model (Phase V)

**Table**: `tags_phasev`
**Source**: Implemented in Phase V Feature 002

**Schema**:
```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags_phasev"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str
    color: str | None = None  # Hex color code (e.g., "#28A745")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

**Presentation Enhancements** (NOT stored in DB):
- **Tag Prefix**: Display tags with # prefix (hashtag style)
  - Example: "#urgent", "#meeting", "#important"
- **Tag List Formatting**: Concatenate multiple tags with spaces
  - Example: "Tags: #urgent #meeting #work"

---

### TaskTag Junction Table (Phase V)

**Table**: `task_tags`
**Source**: Implemented in Phase V Feature 002

**Schema**:
```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks_phaseiii.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags_phasev.id", primary_key=True)
```

**Presentation Enhancements** (NOT stored in DB):
- No direct presentation changes
- Used to join tasks with their associated tags for display

---

## Presentation-Only Enhancement Mappings

### 1. Priority Emoji Mapping

**Purpose**: Provide instant visual priority indicators in AI responses

**Mapping Table**:
| Priority Value (DB) | Emoji | Description | Hex Color (Reference) |
|---------------------|-------|-------------|----------------------|
| `"urgent"` | 🔴 | Critical, needs immediate attention | #DC3545 (Red) |
| `"high"` | 🟠 | Important, high priority | #FD7E14 (Orange) |
| `"medium"` | 🟡 | Normal priority (default) | #FFC107 (Yellow) |
| `"low"` | ⚪ | Low priority, can wait | #6C757D (Gray) |
| `null` or unset | 🟡 | Default to medium | #FFC107 (Yellow) |

**Usage in AI Responses**:
```markdown
🔴 **Prepare quarterly report** (ID: #42)
🟠 **Review contracts** (ID: #43)
🟡 **Buy groceries** (ID: #44)
⚪ **Organize bookshelf** (ID: #45)
```

**Unicode Compatibility**: All emoji from Unicode 9.0 (2016) with >99% browser support

---

### 2. Due Date Relative Formatting

**Purpose**: Make due dates human-readable and actionable

**Formatting Rules** (based on `due_date` field):

| Condition | Format | Example |
|-----------|--------|---------|
| `due_date < now` | ⚠️ Overdue by X days (was YYYY-MM-DD) | ⚠️ Overdue by 2 days (was 2026-01-03) |
| `due_date.date() == now.date()` | 📅 Due today at HH:MM AM/PM | 📅 Due today at 2:00 PM |
| `due_date.date() == now.date() + 1` | 📅 Due tomorrow at HH:MM AM/PM | 📅 Due tomorrow at 9:00 AM |
| `2 <= days <= 6` | 📅 Due in X days (YYYY-MM-DD) | 📅 Due in 3 days (2026-01-08) |
| `days >= 7` | 📅 Due in X days (YYYY-MM-DD) | 📅 Due in 14 days (2026-01-19) |
| `due_date is null` | (omit field) | No due date displayed |

**Usage in AI Responses**:
```markdown
🔴 **Submit budget proposal** (ID: #50)
- 📅 Due today at 5:00 PM

🟠 **Prepare presentation** (ID: #51)
- ⚠️ Overdue by 3 days (was 2026-01-02)

🟡 **Team meeting** (ID: #52)
- 📅 Due in 5 days (2026-01-10)
```

**Timezone**: All dates use UTC for consistency

---

### 3. RRULE Humanization

**Purpose**: Translate RFC 5545 recurrence rules to natural language

**Common Patterns** (based on `recurrence_rule` field):

| RRULE (DB Value) | Human-Readable Format | Example Context |
|------------------|-----------------------|-----------------|
| `"FREQ=DAILY"` | Repeats daily | "Daily standup meeting" |
| `"FREQ=DAILY;INTERVAL=2"` | Repeats every 2 days | "Water plants" |
| `"FREQ=WEEKLY"` | Repeats weekly | "Team meeting" |
| `"FREQ=WEEKLY;BYDAY=MO,WE,FR"` | Repeats weekly on Mon, Wed, Fri | "Gym schedule" |
| `"FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"` | Repeats weekdays (Mon-Fri) | "Commute" |
| `"FREQ=WEEKLY;INTERVAL=2;BYDAY=MO"` | Repeats every 2 weeks on Monday | "Bi-weekly 1-on-1" |
| `"FREQ=MONTHLY"` | Repeats monthly | "Monthly report" |
| `"FREQ=MONTHLY;BYMONTHDAY=15"` | Repeats monthly on the 15th | "Mid-month check-in" |
| `"FREQ=MONTHLY;BYDAY=1MO"` | Repeats on the 1st Monday of each month | "All-hands meeting" |
| `"FREQ=YEARLY"` | Repeats yearly | "Annual review" |
| `null` | (omit field) | Non-recurring task |

**Usage in AI Responses**:
```markdown
🟡 **Weekly team standup** (ID: #60)
- 🔄 Repeats weekly on Monday
- 📅 Next occurrence: Jan 6, 2026

🟠 **Monthly report** (ID: #61)
- 🔄 Repeats monthly on the 1st
- 📅 Next occurrence: Feb 1, 2026
```

**Fallback**: For complex RRULE patterns not in mapping table, display: "🔄 Repeats (custom schedule)"

---

### 4. Category Display Formatting

**Purpose**: Visually distinguish category organization

**Formatting Rule** (based on `category_id` and `categories.name`):
- Prefix: 📁 (File Folder emoji)
- Format: `📁 {Category Name}`

**Usage in AI Responses**:
```markdown
🔴 **Prepare quarterly report** (ID: #42)
- 📁 Work
- 📅 Due today at 5:00 PM

🟡 **Buy groceries** (ID: #44)
- 📁 Personal
- 📅 Due tomorrow at 6:00 PM
```

**No Category**: If `category_id` is `null`, omit category field entirely

---

### 5. Tag Display Formatting

**Purpose**: Show task classification with hashtag-style tags

**Formatting Rule** (based on `task_tags` join and `tags_phasev.name`):
- Prefix: # (hashtag symbol)
- Format: `Tags: #{tag1} #{tag2} #{tag3}`
- Separator: Single space between tags

**Usage in AI Responses**:
```markdown
🔴 **Prepare quarterly report** (ID: #42)
- 📁 Work
- Tags: #urgent #meeting #q1
- 📅 Due today at 5:00 PM

🟠 **Buy groceries** (ID: #44)
- Tags: #shopping #weekly
- 📅 Due tomorrow at 6:00 PM
```

**No Tags**: If task has no tags, omit tags field entirely

---

### 6. Search Result Relevance Display

**Purpose**: Show search result quality and highlight matching keywords

**Formatting Rule** (based on `search_tasks` tool output):
- Relevance indicator: 🔍 {percentage}% match
- Keyword highlighting: **bold** Markdown for matching terms
- Sort order: Highest relevance first

**Usage in AI Responses**:
```markdown
Search results for "presentation":

1. 🔍 95% match - 🔴 **Prepare quarterly presentation** (ID: #50)
   - Matches in: Title
   - 📁 Work
   - 📅 Due today at 5:00 PM

2. 🔍 78% match - 🟡 Review **presentation** slides (ID: #51)
   - Matches in: Title, Description
   - 📁 Work
   - 📅 Due in 3 days (2026-01-08)

3. 🔍 62% match - 🟠 Send **presentation** to team (ID: #52)
   - Matches in: Description
```

**Relevance Calculation**: Based on PostgreSQL ts_rank() function on `search_vector` field

---

### 7. Task List Formatting Structure

**Purpose**: Consistent, scannable task list display

**Formatting Template**:
```markdown
{number}. {priority_emoji} **{title}** (ID: #{task_id})
   - {📁 Category} (if category_id is set)
   - {Tags: #tag1 #tag2} (if tags exist)
   - {📅 Due date relative format} (if due_date is set)
   - {🔄 Recurrence pattern} (if recurrence_rule is set)
```

**Full Example**:
```markdown
1. 🔴 **Submit budget proposal** (ID: #50)
   - 📁 Work
   - Tags: #urgent #finance #q1
   - 📅 Due today at 5:00 PM
   - 🔄 Repeats quarterly on the 1st

2. 🟠 **Prepare presentation** (ID: #51)
   - 📁 Work
   - Tags: #meeting #slides
   - ⚠️ Overdue by 2 days (was 2026-01-03)

3. 🟡 **Buy groceries** (ID: #52)
   - 📁 Personal
   - 📅 Due tomorrow at 6:00 PM

4. ⚪ **Organize bookshelf** (ID: #53)
   - 📁 Home
```

**Metadata Order** (consistent across all responses):
1. Priority emoji + Title + ID
2. Category (📁)
3. Tags (#)
4. Due date (📅 or ⚠️)
5. Recurrence (🔄)

**Completed Tasks**:
```markdown
~~Submit budget proposal~~ ✅ (ID: #50, completed 2026-01-05)
```

---

## Schema Migration Status

**Database Changes Required**: ❌ NONE

All database tables, columns, and indexes already exist from Phase V Features 001 & 002:
- ✅ `tasks_phaseiii` table with `priority`, `due_date`, `category_id`, `recurrence_rule` fields
- ✅ `categories` table
- ✅ `tags_phasev` table
- ✅ `task_tags` junction table
- ✅ `search_vector` tsvector column with GIN index

**Alembic Migrations**: ❌ NOT REQUIRED

---

## Implementation Notes

**Backend Changes**: ❌ NONE (NO new service logic, NO new database queries)

All formatting logic is implemented in the **AI system prompt** via `task_server.py:_get_system_instructions()`. The AI learns formatting patterns through examples and applies them when generating responses.

**Why prompt-based formatting?**
1. **Flexibility**: AI can adapt formatting based on context (e.g., omit empty fields)
2. **No latency**: No additional backend processing or database queries
3. **Easy iteration**: Update formatting by changing prompt, no code deployment
4. **Natural language**: AI can phrase relative dates naturally ("Due this Friday" vs rigid templates)

**MCP Tool Responses**: ❌ NO CHANGES

MCP tools (`add_task`, `list_tasks`, `search_tasks`, etc.) return raw data from database. The AI transforms this data into formatted responses based on system prompt guidelines.

---

## Testing Strategy

**Unit Tests**: ❌ NOT REQUIRED (no backend logic changes)

**Integration Tests**: ❌ NOT REQUIRED (no API changes)

**Manual Testing**: ✅ REQUIRED
- Create tasks with different priorities → verify emoji indicators
- Create tasks with due dates → verify relative formatting
- Create recurring tasks → verify RRULE humanization
- List tasks with categories/tags → verify consistent formatting
- Search tasks → verify relevance scores and keyword highlighting
- Complete tasks → verify strikethrough formatting

**Browser Testing**: ✅ REQUIRED
- Chrome 120+, Firefox 120+, Safari 17+, Edge 120+
- iOS 17+ Safari, Android 14+ Chrome
- Verify emoji rendering (Unicode 9.0 compatibility)
- Verify Markdown rendering (bold, strikethrough, lists)

---

## Performance Impact

**Database Queries**: ❌ NO CHANGE (no new queries, no schema changes)

**Response Time**: ✅ NEGLIGIBLE
- Formatting done by AI during response generation
- No additional API calls or processing
- Same latency as current implementation

**Token Consumption**: ⚠️ MODERATE INCREASE
- Estimated +10-15% tokens per response (due to emoji/formatting)
- Mitigated by selective formatting (only show relevant fields)
- Monitored via OpenAI API usage dashboard

---

## Future Enhancements (Out of Scope)

**Phase 2 - Widget-Based UI**:
- Interactive priority badges (click to change priority)
- Category dropdown selector
- Due date calendar picker
- Tag autocomplete

**Phase 3 - Advanced Visualizations**:
- Gantt chart for tasks with due dates
- Kanban board for task workflow
- Calendar view for recurring tasks

These enhancements would require:
- New React components in frontend
- WebSocket updates for real-time UI changes
- GraphQL subscriptions for live task updates
- Out of scope for ChatKit conversational interface

---

## Glossary

**Presentation-Only Enhancement**: UI/formatting changes that do NOT modify database schema, API contracts, or backend logic. Data is displayed differently but stored identically.

**RRULE**: RFC 5545 Recurrence Rule format for specifying recurring event patterns (e.g., `FREQ=WEEKLY;BYDAY=MO,WE,FR`).

**Relative Date**: Human-readable date format based on current time (e.g., "Due today", "Due in 3 days", "Overdue by 2 days").

**tsvector**: PostgreSQL full-text search data type that stores lexeme vectors for search indexing.

**Unicode 9.0**: Unicode standard released in June 2016, widely supported across modern browsers (>99% compatibility as of 2026).

---

**Status**: ✅ Data model documented (presentation-only enhancements, NO database changes)

**Next Step**: Generate API contracts (`contracts/system-prompt-schema.md`, `contracts/chatkit-startscreen-config.md`)
