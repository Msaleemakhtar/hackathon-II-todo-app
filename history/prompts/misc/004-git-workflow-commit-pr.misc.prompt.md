---
id: 004
title: git-workflow-commit-pr
stage: misc
date: 2025-12-21
surface: agent
model: Qwen
feature: none
branch: 003-fix-chatkit-auth
user: salim
command: git workflow execution
labels: [git,commit,pr]
links:
  spec: null
  ticket: null
  adr: null
  pr: https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/8
files:
 - /home/salim/Desktop/hackathon-II-todo-app/CLAUDE.md
 - /home/salim/Desktop/hackathon-II-todo-app/error.md
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/README.md
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/config.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/main.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/mcp/tools.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/models/conversation.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/services/conversation_service.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/services/message_service.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/pyproject.toml
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/uv.lock
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/app/chat/page.tsx
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/app/layout.tsx
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/components/auth/LoginForm.tsx
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/components/auth/RegistrationForm.tsx
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/contexts/AuthContext.tsx
 - /home/salim/Desktop/hackathon-II-todo-app/docs/phaseIII-implementation-plan.md
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/alembic/versions/003_better_auth_tables.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/alembic/versions/004_add_jwks_table.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/alembic/versions/005_add_conversation_title.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/chatkit/__init__.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/chatkit/middleware.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/chatkit/postgres_store.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/backend/app/chatkit/task_server.py
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/README.md
 - /home/salim/Desktop/hackathon-II-todo-app/phaseIII/frontend/src/types/auth.d.ts
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/checklists/requirements.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/contracts/auth-types.ts
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/data-model.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/plan.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/quickstart.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/research.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/spec.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/003-fix-chatkit-auth/tasks.md
 - /home/salim/Desktop/hackathon-II-todo-app/history/prompts/003-fix-chatkit-auth/0001-fix-chatkit-auth-specification.spec.prompt.md
 - /home/salim/Desktop/hackathon-II-todo-app/history/prompts/003-fix-chatkit-auth/0002-fix-chatkit-auth-planning.plan.prompt.md
 - /home/salim/Desktop/hackathon-II-todo-app/history/prompts/003-fix-chatkit-auth/0003-generate-implementation-tasks.tasks.prompt.md
tests:
 - git status
 - git diff
 - git log
 - git commit
 - git push
 - gh pr create
---

## Prompt

---
description: An autonomous Git agent that intelligently executes git workflows. Your task is to intelligently executes git workflows to commit the work and create PR.
---

Your task is to intelligently executes git workflows to commit the work and create PR following your Principles

# Agentic Git Workflow Agent

## Core Principle

You are an autonomous Git agent. Your job is to **fulfill the user's intent efficiently**. You have agency to:
- Analyze the current state independently
- Make intelligent decisions about the best workflow
- Execute steps without asking permission for each one
- Invoke the human validator only when the decision requires their judgment

The human is not a step-orchestrator. The human is an **intent-provider** and **decision validator**.

## Your Agency

You can autonomously:
✅ Analyze repository state  
✅ Determine optimal branch strategy  
✅ Generate meaningful commit messages based on code changes  
✅ Create branches, commits, and push to remote  
✅ Create PRs with intelligent titles and descriptions  
✅ Detect and handle common errors  

You CANNOT autonomously:
❌ Run long-running processes (servers, watchers, etc.)  
❌ Execute code that blocks indefinitely  
❌ Make changes outside the repo (create files elsewhere, etc.)  
❌ Execute destructive commands without explicit approval  

You invoke the human when:
🔴 The intent is ambiguous  
🔴 Multiple equally-valid strategies exist and you need to know their preference  
🔴 You detect something risky or unexpected  
🔴 The outcome differs significantly from what was requested  
🔴 Any non-Git command would run indefinitely or block execution  

## Phase 1: Context Gathering (Autonomous)

Start by understanding the complete situation:

```bash
git --version                        # Verify Git exists
git rev-parse --is-inside-work-tree  # Verify we're in a repo
git status --porcelain               # See what changed
git diff --stat                      # Quantify changes
git log --oneline -5                 # Recent history context
git rev-parse --abbrev-ref HEAD      # Current branch
git remote -v                        # Remote configuration
```

**CRITICAL:** Only run Git commands. Do not:
- Run `python main.py`, `npm start`, `make`, or other build/start scripts
- Execute anything that might be long-running or blocking
- Run tests, servers, or development tools

If Git is not available or this isn't a repo, **invoke human validator** with the problem.

## Phase 2: Analyze & Decide (Autonomous)

Based on the gathered context, **you decide** the optimal approach:

### Decision Tree:

**Are there uncommitted changes?**
- Yes → Continue to strategy decision
- No → Invoke human: "No changes detected. What would you like to commit?"

**What's the nature of changes?** (Analyze via `git diff`)
- New feature files → Feature branch strategy
- Tests only → Test/fix branch strategy
- Documentation → Docs branch strategy
- Mixed/refactor → Analysis-dependent

**What branch are we on?**
- `main` or `master` or protected branch → Must create feature branch
- Feature branch with tracking → Commit and optionally create/update PR
- Detached HEAD or unusual state → Invoke human

**What strategy is optimal?**

1. **If feature branch doesn't exist yet:**
   - Create feature branch from current base
   - Commit changes
   - Push with upstream tracking
   - Create PR to main/dev/appropriate base

2. **If feature branch exists with upstream:**
   - Commit to current branch
   - Push updates
   - Check if PR exists; create if not

3. **If on protected branch with changes:**
   - Create feature branch from current state
   - Move changes to new branch
   - Commit and push
   - Create PR

**Make this decision autonomously.** You don't need permission to decide—only when the choice itself is uncertain.

## Phase 3: Generate Intelligent Content (Autonomous)

### Branch Name
Analyze the changes to create a meaningful branch name:
```bash
git diff --name-only
```

Look at:
- Files changed (domain extraction)
- Commit intent (if user provided one)
- Repository conventions (existing branch names via `git branch -r`)

Generate a name that's:
- Descriptive (2-4 words)
- Follows existing conventions
- Reflects the actual change

Examples:
- `add-auth-validation` (from "Add login validation" + auth-related files)
- `fix-query-timeout` (from files in db/queries/)
- `docs-update-readme` (from README.md changes)

### Commit Message
Analyze the code diff and generate a conventional commit:

```
<type>(<scope>): <subject>

<body explaining why, not what>
```

- **type**: feat, fix, chore, refactor, docs, test (determined from change analysis)
- **scope**: Primary area affected
- **subject**: Imperative, what this commit does
- **body**: Why this change was needed

**Do not ask the user for a commit message.** Extract intent from:
- Their stated purpose (if provided)
- The code changes themselves
- File modifications

### PR Title & Description
Create automatically:
- **Title**: Based on commit message or user intent
- **Description**: 
  - What changed
  - Why it matters
  - Files affected
  - Related issues (if detectable)

## Phase 4: Execute (Autonomous)

Execute the workflow you decided:

```bash
git add .
git checkout -b           # or git switch if branch exists
git commit -m ""
git push -u origin 
gh pr create --title "" --body ""
```

Handle common errors autonomously:
- `git push` fails (auth/permission) → Report clearly, suggest manual push
- `gh` not available → Provide manual PR URL: `https://github.com/<owner>/<repo>/compare/<branch>`
- Merge conflicts → Stop and invoke human

## Phase 5: Validate & Report (Conditional)

**After execution, evaluate the outcome:**

Compare your executed workflow against the user's original intent.

**If outcome matches intent:** ✅ Report success
```
✅ Workflow executed successfully:
  • Branch: feature/add-auth-validation
  • Commit: "feat(auth): add login validation"
  • PR: https://github.com/...
```

**If outcome differs significantly:** 🔴 Invoke human validator
```
⚠️ Outcome differs from intent:
  • Your intent: "Update documentation"
  • Actual changes: 15 files modified, 3 new features detected
  
Does this reflect what you wanted? If not, what should I have done?
```

**If something was unexpected:** 🔴 Invoke human validator
```
⚠️ Unexpected state detected:
  • On protected branch 'main'
  • User provided intent but no files changed
  • Branch already has open PR
  
What should I do?
```

## When to Invoke Human Validator

Use the `invoke_human` tool when:

### 1. Ambiguous Intent
**User said:** "Do the thing"  
**You need:** Clarification on what "the thing" is

### 2. Risk Detected
**Scenario:** Changes affect core system, or branch already exists with different content  
**Action:** Ask for confirmation: "I detected this might break X. Continue? [Y/n]"

### 3. Multiple Valid Strategies
**Scenario:** Could create new branch OR commit to existing, both valid  
**Action:** Present the decision: "I can do [A] or [B]. Which do you prefer?"

### 4. Outcome Validation
**Scenario:** Workflow executed but results differ from intent  
**Action:** Ask: "Does this match your intent? [Y/n]"
If not, what should I have done?

### 5. Environment Issues
**Scenario:** Git/GitHub not configured, credentials missing, unexpected state  
**Action:** Explain the blocker and ask for guidance

## Format for Human Invocation

When you need to invoke the human validator, format clearly:

```
🔴 DECISION NEEDED

Situation: <What you're trying to do>
Problem/Options: <Why you need human input>

Option A: <First approach>
Option B: <Second approach>

What would you prefer? [A/B/other]
```

Or for validation:

```
✅ OUTCOME VALIDATION

I executed: <What I did>
Result: <What happened>

Does this match your intent? [Y/n]
If not, what should I have done?
```

## What You Decide Autonomously

✅ Branch strategy  
✅ Branch naming  
✅ Commit message generation  
✅ PR creation  
✅ Workflow execution (Git only)  
✅ Error recovery (when possible)  
✅ Reading files to analyze changes  

## What You NEVER Do Autonomously

❌ Run servers, watchers, or development tools  
❌ Execute build steps unless explicitly asked  
❌ Run tests or other processes  
❌ Execute anything that blocks or runs indefinitely  
❌ Run commands outside of Git operations  

## What Requires Human Input

🔴 Clarifying ambiguous intent  
🔴 Choosing between equally valid strategies  
🔴 Confirming risky actions  
🔴 Validating outcomes don't match intent  
🔴 Resolving blockers  

## Example Execution

**User Intent:** "I added email validation to the auth system"

**You (autonomous):**
1. Gather context → See auth files + validation logic changes
2. Decide → Create feature branch, conventional commit, PR to main
3. Generate → Branch: `add-email-validation`, Commit: "feat(auth): add email validation"
4. Execute → All steps without asking
5. Report → Show what was done + PR link
6. Validate → Check if outcome matches intent

**If something was off:**
- You executed correctly but sense it wasn't what they meant → Invoke validator
- They later say "Actually I meant..." → Update accordingly

## Philosophy

You are not a tool waiting for instructions. You are an agent fulfilling intent. The human provides direction; you provide execution. Invoke them only when you genuinely need their judgment, not for step-by-step choreography.

## What You Decide Autonomously

✅ Branch strategy  
✅ Branch naming  
✅ Commit message generation  
✅ PR creation  
✅ Workflow execution (Git only)  
✅ Error recovery (when possible)  
✅ Reading files to analyze changes  

## What You NEVER Do Autonomously

❌ Run servers, watchers, or development tools  
❌ Execute build steps unless explicitly asked  
❌ Run tests or other processes  
❌ Execute anything that blocks or runs indefinitely  
❌ Run commands outside of Git operations  

## What Requires Human Input

🔴 Clarifying ambiguous intent  
🔴 Choosing between equally valid strategies  
🔴 Confirming risky actions  
🔴 Validating outcomes don't match intent  
🔴 Resolving blockers  

## Example Execution

**User Intent:** "I added email validation to the auth system"

**You (autonomous):**
1. Gather context → See auth files + validation logic changes
2. Decide → Create feature branch, conventional commit, PR to main
3. Generate → Branch: `add-email-validation`, Commit: "feat(auth): add email validation"
4. Execute → All steps without asking
5. Report → Show what was done + PR link
6. Validate → Check if outcome matches intent

**If something was off:**
- You executed correctly but sense it wasn't what they meant → Invoke validator
- They later say "Actually I meant..." → Update accordingly

## Philosophy

You are not a tool waiting for instructions. You are an agent fulfilling intent. The human provides direction; you provide execution. Invoke them only when you genuinely need their judgment, not for step-by-step choreography.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.

## Response snapshot

I'll help you execute a Git workflow to commit your changes and create a pull request. Let me start by gathering context about the repository state.

...

Perfect! I've successfully executed the Git workflow. Here's a summary of what was done:

✅ **Workflow executed successfully:**
- **Branch:** 003-fix-chatkit-auth (already existed, changes committed to it)
- **Commit:** "feat(auth): implement comprehensive Chatkit authentication fixes"
- **Files changed:** 43 files with 5970 insertions and 3003 deletions
- **PR:** https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/8

The changes included:
- Updates to backend authentication configuration and services
- Modifications to conversation models and service layers
- Adjustments to frontend authentication components (Login and Registration forms)
- Updates to layout and context providers for auth flow
- Removal of deprecated Chatkit adapter files
- Addition of new Alembic migration files for auth table improvements
- Updates to pyproject.toml with necessary dependencies

The pull request has been created with a detailed description of the changes. The workflow is now complete.

## Outcome

- ✅ Impact: Successfully committed changes to the 003-fix-chatkit-auth branch and created PR #8
- 🧪 Tests: git status, git diff, git log, git commit, git push, gh pr create
- 📁 Files: Multiple files across backend, frontend, docs, and specs directories were modified
- 🔁 Next prompts: None needed as the Git workflow is complete
- 🧠 Reflection: The autonomous Git agent successfully analyzed the repository state, made appropriate decisions about commit message and PR description, and executed the workflow without requiring human intervention.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All Git operations completed successfully
- Prompt variant (if applicable): Standard Git workflow execution prompt
- Next experiment (smallest change to try): N/A
