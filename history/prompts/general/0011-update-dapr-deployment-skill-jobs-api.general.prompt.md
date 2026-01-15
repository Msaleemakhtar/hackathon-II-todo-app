---
id: 0011
title: Update dapr-deployment skill with Jobs API coverage
stage: general
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: salim
command: skill update
labels: ["skill", "dapr", "jobs-api", "documentation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/dapr-deployment/references/building-blocks.md
tests:
 - none
---

## Prompt

My dapr-deployment skill, does cover the Jobs API.
Update it to include:
1. Jobs API for scheduling future work (vs bindings for external triggers)
2. HTTP pattern: POST /v1.0-alpha1/jobs/{name} with schedule and data
3. Handler pattern: POST /job/{name} endpoint returns {"status": "SUCCESS"}
4. Human-readable schedules: @daily, @hourly, @every 1h30m

## Response snapshot

Updated the Jobs section in `.claude/skills/dapr-deployment/references/building-blocks.md` with comprehensive coverage including:

1. **Jobs vs Bindings comparison** - Clear guidance on when to use Jobs API vs Bindings
2. **HTTP API patterns** - Complete examples for POST/GET/DELETE endpoints at `/v1.0-alpha1/jobs/{name}`
3. **Handler pattern** - Detailed implementation showing `POST /job/{name}` with status codes (SUCCESS, RETRY, FAILED)
4. **Human-readable schedules** - Full syntax reference:
   - Predefined: @daily, @hourly, @weekly, @monthly, @yearly
   - Intervals: @every 1h30m, @every 30s, @every 5m, @every 2h, @every 1d
   - Cron expressions: Standard format with practical examples
5. **One-time vs recurring jobs** - Examples and patterns for all job types
6. **SDK examples** - Python implementation for scheduling and canceling jobs
7. **Complete working example** - Task reminder system demonstrating real-world usage
8. **Job lifecycle management** - Query, update, and delete operations
9. **Best practices** - 6 key guidelines for production use
10. **Use cases** - Dynamic scheduling, recurring tasks, time-based workflows

The section now matches the depth and quality of other building blocks in the skill.

## Outcome

- ✅ Impact: Enhanced dapr-deployment skill with comprehensive Jobs API documentation covering HTTP patterns, handler implementation, schedule syntax, and real-world examples
- 🧪 Tests: No tests required (documentation update)
- 📁 Files: Modified 1 file (.claude/skills/dapr-deployment/references/building-blocks.md)
- 🔁 Next prompts: None - skill update complete
- 🧠 Reflection: Successfully expanded minimal Jobs section (40 lines) into comprehensive reference (400+ lines) with complete API patterns, handler examples, schedule syntax, lifecycle management, best practices, and working examples

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation update)
- Prompt variant (if applicable): Standard skill update request
- Next experiment (smallest change to try): None required
