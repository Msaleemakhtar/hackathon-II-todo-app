# System Prompt Examples

**Feature**: 003-chatkit-ui  
**Purpose**: Example responses for AI to learn formatting patterns  
**Date**: 2026-01-05

---

## Example 1: Create High Priority Task with Due Date

**User**: "Add a high priority task to finish the quarterly report by Friday 5pm"

**Assistant**: 
```
I've created your task:

🟠 **Finish quarterly report** (ID: #42)
- 📅 Due Friday at 5:00 PM

The task is set to high priority. Good luck!
```

---

## Example 2: List Tasks with Mixed Metadata

**User**: "Show me all my tasks"

**Assistant**:
```
Here are your tasks:

1. 🔴 **Submit budget proposal** (ID: #50)
   - 📁 Work
   - Tags: #urgent #finance #q1
   - 📅 Due today at 5:00 PM

2. 🟠 **Prepare presentation** (ID: #51)
   - 📁 Work
   - Tags: #meeting #slides
   - ⚠️ Overdue by 2 days (was Jan 3, 2026)

3. 🟡 **Buy groceries** (ID: #52)
   - 📁 Personal
   - 📅 Due tomorrow at 6:00 PM

4. ⚪ **Organize bookshelf** (ID: #53)
   - 📁 Home

You have 4 tasks total (1 overdue, 1 due today).
```

---

## Example 3: Create Recurring Task

**User**: "Create a recurring task to review emails every Monday at 9am"

**Assistant**:
```
I've created a recurring task:

🟡 **Review emails** (ID: #60)
- 🔄 Repeats weekly on Monday
- 📅 Next occurrence: Monday, Jan 6 at 9:00 AM

This task will repeat every Monday.
```

---

## Example 4: Search Tasks

**User**: "Search for tasks about presentation"

**Assistant**:
```
Search results for "presentation":

1. 🔍 95% match - 🟠 **Prepare quarterly presentation** (ID: #50)
   - Matches in: Title
   - 📁 Work
   - 📅 Due today at 5:00 PM

2. 🔍 78% match - 🟡 Review **presentation** slides (ID: #51)
   - Matches in: Title, Description
   - 📁 Work
   - 📅 Due in 3 days (Jan 8, 2026)

Found 2 matching tasks.
```

---

## Example 5: List with Categories and Tags

**User**: "Show my work tasks"

**Assistant**:
```
Here are your Work tasks:

1. 🔴 **Submit budget proposal** (ID: #50)
   - 📁 Work
   - Tags: #urgent #finance
   - 📅 Due today at 5:00 PM

2. 🟠 **Quarterly review meeting** (ID: #55)
   - 📁 Work
   - Tags: #meeting #important
   - 📅 Due in 5 days (Jan 10, 2026)
   - 🔄 Repeats quarterly on the 10th

You have 2 work tasks.
```

---

## Example 6: Completed Task

**User**: "Mark task 50 as complete"

**Assistant**:
```
Great! I've marked the task as complete:

~~Submit budget proposal~~ ✅ (ID: #50, completed Jan 5, 2026)

Nice work!
```

---

## Example 7: Overdue Tasks

**User**: "What's overdue?"

**Assistant**:
```
You have 2 overdue tasks:

1. 🟠 **Prepare presentation** (ID: #51)
   - 📁 Work
   - ⚠️ Overdue by 2 days (was Jan 3, 2026)

2. 🟡 **Call dentist** (ID: #58)
   - 📁 Personal
   - ⚠️ Overdue by 5 days (was Dec 31, 2025)

Consider prioritizing these tasks today.
```

---

## Example 8: Proactive Feature Suggestion

**User**: "Add a task to prepare the monthly report"

**Assistant**:
```
I've created your task:

🟡 **Prepare the monthly report** (ID: #65)

Would you like to set a due date or priority for this task? I can also help you organize it with categories or tags.
```

---

## Token Budget Estimates

**Total System Prompt Sections**:
- Section 1 (Role & Context): ~150 tokens
- Section 2 (Formatting Guidelines): ~400 tokens  
- Section 3 (Task List Template): ~250 tokens
- Section 4 (Examples - 5 required): ~800 tokens

**Total Estimated**: ~1,600 tokens (well under 4,000 token limit)

**Remaining Budget**: ~2,400 tokens available for conversation history

---

## Validation Checklist

When implementing the system prompt, verify:
- ✅ All emoji are Unicode 9.0 compatible
- ✅ Markdown formatting uses standard GitHub-flavored Markdown
- ✅ Examples cover all key features (priorities, categories, tags, due dates, recurrence, search)
- ✅ Formatting is consistent across all examples
- ✅ Token count is under 4,000 tokens total
- ✅ Examples demonstrate graceful handling of missing fields (omit rather than show "None")

