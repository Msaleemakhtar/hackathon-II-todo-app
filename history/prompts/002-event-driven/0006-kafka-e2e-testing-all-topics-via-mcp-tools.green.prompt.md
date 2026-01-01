---
id: 0006
title: Kafka E2E Testing All Topics Via MCP Tools
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-event-driven
branch: 002-event-driven
user: salim
command: e2e-kafka-testing
labels: ["kafka", "testing", "mcp-tools", "event-driven", "integration-testing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - /home/salim/Desktop/hackathon-II-todo-app/phaseV/backend/app/mcp/standalone.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseV/backend/app/mcp/tools.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseV/backend/app/kafka/producer.py
 - /tmp/mcp-kafka-test.log
tests:
 - Test 1: TaskCreatedEvent → task-events topic (task_id: 165)
 - Test 2: TaskUpdatedEvent → task-events topic (task_id: 165)
 - Test 3: Recurring TaskCreatedEvent → task-events topic (task_id: 166)
 - Test 4: TaskCompletedEvent → task-recurrence topic (task_id: 166)
 - Test 5: ReminderSentEvent → task-reminders topic (task_id: 165)
---

## Prompt

Execute comprehensive end-to-end testing of all three Kafka topics using MCP tools. Perform the following tests IN SEQUENCE:

**Test 1: TaskCreatedEvent → task-events topic**
- Use the MCP server at `/home/salim/Desktop/hackathon-II-todo-app/phaseV/backend`
- Run: `mcp dev standalone.py` with tool `create_task`
- Create a task with title "Test 1: TaskCreatedEvent", priority "high", user_id "user123"
- Capture the task_id from the response

**Test 2: TaskUpdatedEvent → task-events topic**
- Use the task_id from Test 1
- Run MCP tool `update_task` to update the title to "Test 1: Updated Title"
- Verify update was successful

**Test 3: Recurring TaskCreatedEvent → task-events topic**
- Run MCP tool `create_task`
- Create a recurring task with:
  - title: "Test 3: Recurring Task"
  - priority: "medium"
  - user_id: "user123"
  - recurrence_rule: "FREQ=DAILY;COUNT=5"
  - due_date: "2026-01-10T18:00:00Z"
- Capture the recurring task_id

**Test 4: TaskCompletedEvent → task-recurrence topic**
- Use the recurring task_id from Test 3
- Run MCP tool `complete_task` on that task
- This should publish TaskCompletedEvent to task-recurrence topic

**Test 5: ReminderSentEvent → task-reminders topic**
- Use the task_id from Test 1 (must have a due_date)
- First, update Test 1 task to add due_date: "2026-01-05T10:00:00Z"
- Then run MCP tool `set_reminder` with remind_before_minutes: 120
- This should publish ReminderSentEvent to task-reminders topic

After all tests complete:
1. Check the MCP server logs at `/tmp/mcp-kafka-test.log`
2. Look for all "✅ Published" messages showing partition and offset
3. Verify we see events for all 5 tests

Report the results showing which events were successfully published with their topic, partition, and offset details.

## Response snapshot

Successfully executed comprehensive end-to-end testing of all three Kafka topics using MCP tools via HTTP transport. All 5 tests passed successfully:

**Environment Setup:**
- Started MCP standalone server at localhost:8001 with FastMCP streamable HTTP transport
- Configured Redpanda Cloud connection with SASL_SSL authentication
- Kafka producer initialized successfully with background event loop

**Test Results:**

**Test 1: TaskCreatedEvent → task-events**
- ✅ Created task with ID: 165
- ✅ Published task.created to task-events partition 2 offset 7 (key: 165)
- Title: "Test 1: TaskCreatedEvent"
- Priority: high

**Test 2: TaskUpdatedEvent → task-events**
- ✅ Updated task ID: 165
- ✅ Published task.updated to task-events partition 2 offset 8 (key: 165)
- Updated title: "Test 1: Updated Title"

**Test 3: Recurring TaskCreatedEvent → task-events**
- ✅ Created recurring task with ID: 166
- ✅ Published task.created to task-events partition 2 offset 9 (key: 166)
- Title: "Test 3: Recurring Task"
- Recurrence: FREQ=DAILY;COUNT=5
- Due date: 2026-01-10T18:00:00Z

**Test 4: TaskCompletedEvent → task-recurrence**
- ✅ Completed recurring task ID: 166
- ✅ Published task.completed to task-recurrence partition 0 offset 1 (key: 166)
- Event routed to correct topic for recurring task processing

**Test 5: ReminderSentEvent → task-reminders**
- ✅ Updated task 165 with due_date: 2026-01-05T10:00:00Z
- ✅ Set reminder with remind_before_minutes: 120
- ✅ Published reminder.sent to task-reminders partition 0 offset 0 (key: 165)
- Calculated remind_at: 2026-01-05T08:00:00Z (2 hours before due date)

**All Published Events Summary:**
```
2026-01-01 15:12:22,711 - ✅ Published task.created to task-events partition 2 offset 7 (key: 165)
2026-01-01 15:12:43,827 - ✅ Published task.updated to task-events partition 2 offset 8 (key: 165)
2026-01-01 15:13:02,692 - ✅ Published task.created to task-events partition 2 offset 9 (key: 166)
2026-01-01 15:13:19,575 - ✅ Published task.completed to task-recurrence partition 0 offset 1 (key: 166)
2026-01-01 15:13:38,614 - ✅ Published task.updated to task-events partition 2 offset 10 (key: 165)
2026-01-01 15:13:47,553 - ✅ Published reminder.sent to task-reminders partition 0 offset 0 (key: 165)
```

**Key Observations:**
1. All three Kafka topics are functional: task-events, task-recurrence, task-reminders
2. Event routing works correctly based on event type and task properties
3. Background async publishing with send_and_wait ensures delivery confirmation
4. Partition assignment is working (task-events uses partition 2, others use partition 0)
5. Event IDs are unique (UUID format) for tracking
6. MCP tools integrate seamlessly with Kafka producer via background thread

## Outcome

- ✅ Impact: Validated end-to-end Kafka event publishing pipeline across all three topics via MCP tools
- 🧪 Tests: 5/5 passed - task.created, task.updated, task.completed (recurring), reminder.sent all published successfully
- 📁 Files: MCP standalone server, Kafka producer, MCP tools (18 tools total)
- 🔁 Next prompts: Deploy consumer services for each topic, test event consumption and processing
- 🧠 Reflection: Event-driven architecture foundation is solid. All event types publish to correct topics with proper partitioning and offset tracking.

## Evaluation notes (flywheel)

- Failure modes observed: Initial port 8001 conflict (resolved by killing existing process), graceful shutdown async warning (non-blocking)
- Graders run and results (PASS/FAIL): PASS - All 5 event types published successfully with partition and offset confirmation
- Prompt variant (if applicable): E2E-testing-via-http-transport
- Next experiment (smallest change to try): Test consumer services reading from all three topics and processing events correctly
