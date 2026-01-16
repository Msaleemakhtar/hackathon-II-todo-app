---
id: 0015
title: Show Git status
stage: general
date: 2026-01-16
surface: agent
model: gemini-1.5-pro-001
feature: none
branch: main
user: salim
command: .specify/scripts/bash/create-phr.sh --title "Show Git status" --stage general --json
labels: ["git", "status"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files: null
tests: null
---

## Prompt

show me status

## Response snapshot

Current status: On branch `main`, up to date with `origin/main`. Two untracked PHR files present.

## Outcome

- ✅ Impact: Successfully displayed the current Git status as requested by the user.
- 🧪 Tests: null
- 📁 Files: null
- 🔁 Next prompts: null
- 🧠 Reflection: The Git agent accurately reported the repository's status, including untracked files.

## Evaluation notes (flywheel)

- Failure modes observed: null
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
