# Phase V Feature Testing Guide

## 🚀 Quick Start

### 1. Access the Application
- **URL**: https://todo-app.local
- **Accept Certificate**: Click "Advanced" → "Proceed to todo-app.local (unsafe)"
- **Create Account**: Sign up with email/password
- **Login**: Use your credentials

### 2. API Documentation
- **API Docs**: https://todo-app.local/api/docs
- **Health Check**: https://todo-app.local/api/health

---

## ✅ Feature Testing Scenarios

### Feature 1: Task Prioritization

**Test Priority Levels:**

1. **Create Tasks with Different Priorities:**
   - Go to Chat interface
   - Try these prompts:
   ```
   Create a task "Fix critical bug" with urgent priority
   Add a task "Review documentation" with low priority
   Create task "Implement new feature" with high priority
   Add task "Update dependencies" with medium priority
   ```

2. **List Tasks by Priority:**
   ```
   Show me all urgent tasks
   List high priority tasks
   Show my medium priority tasks
   ```

3. **Update Task Priority:**
   ```
   Change "Review documentation" to high priority
   Update task 1 priority to urgent
   ```

4. **Filter by Priority:**
   ```
   Show only urgent and high priority tasks
   List all tasks sorted by priority
   ```

**Expected Results:**
- ✅ Tasks created with specified priority
- ✅ Tasks displayed with priority badge/color
- ✅ Priority updates reflected immediately
- ✅ Filtering and sorting works correctly

---

### Feature 2: Category Organization

**Test Categories:**

1. **Create Categories:**
   ```
   Create a category called "Work" with color #3B82F6
   Add category "Personal" with color #10B981
   Create category "Shopping" with color #F59E0B
   ```

2. **Assign Tasks to Categories:**
   ```
   Create task "Finish project report" in Work category
   Add task "Buy groceries" to Shopping category
   Move task "Exercise" to Personal category
   ```

3. **List by Category:**
   ```
   Show all Work tasks
   List tasks in Shopping category
   Show me categories with task counts
   ```

4. **Update Categories:**
   ```
   Rename "Work" category to "Office Work"
   Change Shopping category color to #EF4444
   ```

5. **Delete Category (tasks remain):**
   ```
   Delete the Shopping category
   Show all tasks (verify shopping tasks still exist)
   ```

**Expected Results:**
- ✅ Maximum 50 categories allowed
- ✅ Category colors displayed correctly
- ✅ Tasks retain category even after category name change
- ✅ Deleting category keeps tasks (sets category to null)

---

### Feature 3: Flexible Tagging

**Test Tags:**

1. **Create Tags:**
   ```
   Create tag "important" with color #EF4444
   Add tag "quick-win" with color #10B981
   Create tags "meeting", "email", "research"
   ```

2. **Add Multiple Tags to Tasks:**
   ```
   Create task "Prepare presentation" with tags important and meeting
   Add tags quick-win and research to task "Update README"
   Tag task 1 with important, urgent, and meeting
   ```

3. **Search by Tags (OR filtering):**
   ```
   Show tasks tagged with important OR meeting
   List all tasks with quick-win or research tags
   Find tasks tagged urgent
   ```

4. **Manage Tags:**
   ```
   Remove tag "meeting" from task 1
   Update tag color for "important" to #F59E0B
   Delete tag "email"
   ```

**Expected Results:**
- ✅ Maximum 100 tags per user
- ✅ Maximum 10 tags per task
- ✅ OR filtering returns tasks with ANY matching tag
- ✅ Tag operations are idempotent (no errors on duplicate add/remove)

---

### Feature 4: Due Date Management

**Test Due Dates:**

1. **Create Tasks with Due Dates:**
   ```
   Create task "Submit report" due January 15, 2025 at 5pm
   Add task "Team meeting" due tomorrow at 2pm
   Create task "Pay bills" due in 3 days
   ```

2. **Filter by Due Date:**
   ```
   Show tasks due before January 20, 2025
   List tasks due after today
   Show overdue tasks
   ```

3. **Sort by Due Date:**
   ```
   Show all tasks sorted by due date
   List upcoming tasks by deadline
   ```

4. **Update Due Dates:**
   ```
   Change task 1 due date to next Monday
   Remove due date from task "Pay bills"
   ```

**Expected Results:**
- ✅ Dates stored in UTC, displayed in local timezone
- ✅ ISO 8601 format accepted (YYYY-MM-DDTHH:MM:SS)
- ✅ Natural language dates parsed correctly
- ✅ Sorting by due date works (nulls last)

---

### Feature 5: Full-Text Keyword Search

**Test Search:**

1. **Create Searchable Tasks:**
   ```
   Create task "Implement user authentication system"
   Add task "Write documentation for authentication"
   Create task "Review security authentication protocols"
   Add task "Update user profile page"
   ```

2. **Search by Keywords:**
   ```
   Search for "authentication"
   Find tasks about "user"
   Search "security protocols"
   ```

3. **Multi-word Search (all words must match):**
   ```
   Search for "user authentication"
   Find "documentation security"
   ```

**Expected Results:**
- ✅ Search matches title and description
- ✅ Results ranked by relevance (ts_rank)
- ✅ Case-insensitive search
- ✅ All search terms must be present (AND operation)
- ✅ Maximum 50 results returned

---

### Feature 6: Recurring Tasks

**Test Recurrence Rules:**

1. **Daily Recurring Tasks:**
   ```
   Create task "Daily standup" recurring every day
   Add task "Check email" with recurrence FREQ=DAILY
   ```

2. **Weekly Recurring Tasks:**
   ```
   Create task "Team meeting" recurring every Monday and Friday
   Add task "Gym" with recurrence FREQ=WEEKLY;BYDAY=MO,WE,FR
   ```

3. **Monthly Recurring Tasks:**
   ```
   Create task "Pay rent" recurring on the 1st of every month
   Add task "Team retrospective" with recurrence FREQ=MONTHLY;BYMONTHDAY=15
   ```

4. **Yearly Recurring Tasks:**
   ```
   Create task "Renew license" recurring every December 25
   Add task "Birthday reminder" with recurrence FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25
   ```

5. **View and Update Recurrence:**
   ```
   Show recurring tasks
   Update task 1 recurrence rule to every Tuesday
   Remove recurrence from task "Daily standup"
   ```

**Expected Results:**
- ✅ Valid RRULE format accepted (RFC 5545)
- ✅ Invalid RRULE rejected with helpful error
- ✅ Recurrence pattern stored correctly
- ✅ Examples shown in error messages

---

### Feature 7: Reminders

**Test Reminder Setting:**

1. **Set Reminders:**
   ```
   Set reminder for task 1, 30 minutes before due date
   Remind me 1 hour before task "Team meeting"
   Set 24-hour advance reminder for "Submit report"
   ```

2. **Validation Tests:**
   ```
   Set reminder for task without due date (should fail)
   Set reminder with negative minutes (should fail)
   Set reminder that would be in past (should fail)
   ```

**Expected Results:**
- ✅ Reminder requires task to have due_date
- ✅ remind_before_minutes must be positive
- ✅ Calculated remind_at shown in response
- ✅ reminder_sent flag tracked (actual notification in 002-event-streaming)

---

## 🧪 Advanced Testing Scenarios

### Scenario 1: Complex Task Management
```
Create a high priority task "Launch Product V2"
  - Due: February 1, 2025
  - Category: Work
  - Tags: important, urgent, launch
  - Recurrence: None
  - Reminder: 1 day before

Then:
- Search for "product launch"
- Show all urgent tasks in Work category
- List tasks due before February 5
```

### Scenario 2: Category & Tag Combination
```
Create category "Projects" with color #8B5CF6
Create tags "frontend", "backend", "database"

Add task "Redesign homepage"
  - Category: Projects
  - Tags: frontend

Add task "API optimization"
  - Category: Projects
  - Tags: backend, database

Then:
- Show all Projects tasks
- Find tasks with frontend OR backend tags
- List high priority project tasks
```

### Scenario 3: Recurring Task with Reminder
```
Create task "Weekly team sync"
  - Recurrence: Every Monday at 10am
  - Due: Next Monday 10am
  - Priority: High
  - Category: Work
  - Tags: meeting, recurring
  - Reminder: 15 minutes before

Then:
- Verify recurrence rule is stored
- Check reminder time calculated correctly
- Update to every Monday and Wednesday
```

---

## 📊 API Testing (via Swagger UI)

1. **Open API Docs**: https://todo-app.local/api/docs

2. **Authenticate**:
   - Use Better Auth to get JWT token
   - Click "Authorize" in Swagger
   - Enter token

3. **Test MCP Tools** (18 total):
   - `add_task` - Create with all fields
   - `list_tasks` - Test filters (priority, category, tags, due dates, sort)
   - `get_task` - Retrieve single task with full details
   - `update_task` - Modify fields
   - `complete_task` - Mark as done
   - `delete_task` - Remove task
   - `create_category` - Add category
   - `list_categories` - View all with counts
   - `update_category` - Modify category
   - `delete_category` - Remove category
   - `create_tag` - Add tag
   - `list_tags` - View all with counts
   - `update_tag` - Modify tag
   - `delete_tag` - Remove tag
   - `add_tag_to_task` - Assign tag
   - `remove_tag_from_task` - Unassign tag
   - `search_tasks` - Full-text search
   - `set_reminder` - Configure reminder

---

## 🐛 Error Testing

### Test Validation Limits:

1. **Category Limit (50)**:
   ```
   Create 50 categories (should succeed)
   Create 51st category (should fail with limit error)
   ```

2. **Tag Limit (100 total, 10 per task)**:
   ```
   Create 100 tags (should succeed)
   Create 101st tag (should fail)

   Add 10 tags to a task (should succeed)
   Add 11th tag to same task (should fail)
   ```

3. **Invalid Input Tests**:
   ```
   Create task with invalid priority "super-urgent" (should fail)
   Set due_date with invalid format (should fail)
   Create recurring task with invalid RRULE (should fail)
   Set reminder with negative minutes (should fail)
   ```

---

## 📝 Verification Checklist

- [ ] All 6 user stories working (Prioritization, Categories, Tags, Due Dates, Search, Recurring)
- [ ] 18 MCP tools functional
- [ ] HTTPS working without mixed content errors
- [ ] CORS properly configured
- [ ] Data isolation (User A can't see User B's data)
- [ ] Search returns relevant results
- [ ] Filters and sorting work correctly
- [ ] Category/tag limits enforced
- [ ] Recurrence rules validated
- [ ] Reminder validation working
- [ ] PostgreSQL indexes being used (check query performance)
- [ ] All pods healthy and running

---

## 🔍 Database Verification

```bash
# Connect to database (if direct access available)
# Check indexes exist
\d+ tasks_phaseiii

# Verify search performance
EXPLAIN ANALYZE SELECT * FROM tasks_phaseiii
WHERE search_vector @@ to_tsquery('english', 'meeting & important');

# Check CORS configuration
kubectl exec -n todo-phasev deployment/backend -- env | grep CORS

# View pod logs
kubectl logs -n todo-phasev -l app=backend --tail=100
kubectl logs -n todo-phasev -l app=frontend --tail=100
```

---

## ✅ Success Criteria

**Phase V Implementation is Complete if:**
- ✅ All 18 MCP tools work via Chat interface
- ✅ All 6 user stories functional
- ✅ Search returns ranked results
- ✅ Filters combine correctly (priority + category + tags + due dates)
- ✅ Validation errors clear and helpful
- ✅ No HTTPS/CORS errors
- ✅ Multi-user isolation working
- ✅ Performance acceptable (<200ms for search)

**Happy Testing! 🎉**
