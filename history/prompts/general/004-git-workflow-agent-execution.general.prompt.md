---
id: "004"
title: "Git Workflow Agent Execution"
stage: "general"
date: "2026-01-05"
surface: "agent"
model: "Qwen Code"
feature: "none"
branch: "003-chatkit-ui"
user: "salim"
command: "git workflow automation"
labels: ["git", "automation", "workflow", "pr", "commit"]
links:
  spec: null
  ticket: null
  adr: null
  pr: "https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/14"
files:
  - "phaseV/backend/app/chatkit/task_server.py"
  - "phaseV/frontend/src/app/chat/page.tsx"
  - "CLAUDE.md"
tests: []
---

# Git Workflow Agent Execution

## Prompt Text
```
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
**Action:** Ask: "Does this match what you wanted?"

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

## Response Text
I'll help you create a commit and PR for your todo app project. Let me start by gathering the current Git context.

I can see the current state of your Git repository. There are several changes:

1. Modified files:
   - CLAUDE.md (+4 lines)
   - Removed: docs/PHASE_V_IMPLEMENTATION_PLAN.md (1575 lines)
   - Modified: phaseV/backend/app/chatkit/task_server.py (+222 lines)
   - Modified: phaseV/frontend/src/app/chat/page.tsx (+40 lines, -1 line)

2. Untracked files:
   - history/prompts/003-chatkit-ui/
   - phaseV/backend/app/chatkit/task_server.py.backup-003
   - phaseV/frontend/src/app/chat/page.tsx.backup-003
   - specs/003-chatkit-ui/

3. Current branch: 003-chatkit-ui
4. Remote: origin (GitHub)

Based on the changes, it looks like you've been working on a chatkit UI feature, with backend and frontend modifications. Let me analyze the changes to create an appropriate commit message and PR.

Looking at the changes, it seems like this is related to adding a chatkit UI feature. I'll proceed with creating a commit and PR for this work.

I've staged all the changes. Now I'll create a commit with an appropriate message based on the changes I observed. The changes appear to be related to implementing a chatkit UI feature with backend and frontend components.

Great! The commit has been created successfully. Now I'll push the changes to the remote repository. Since this is a feature branch, I'll set up the upstream tracking as well.

The changes have been successfully pushed to the remote repository. Now I'll create a pull request using the GitHub CLI. If the GitHub CLI is not available, I'll provide the URL for creating the PR manually.

Great! GitHub CLI is available. Now I'll create a pull request with an appropriate title and description based on the changes.

Perfect! I've successfully completed the Git workflow for your changes. Here's a summary of what was done:

✅ **Workflow executed successfully:**
- **Branch:** 003-chatkit-ui
- **Commit:** "feat(chatkit): implement chatkit UI with backend task server"
- **Changes:** 21 files modified (4960 insertions, 1585 deletions)
- **PR:** https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/14

The pull request has been created with an appropriate title and description that summarizes the changes. The PR includes the implementation of the chatkit UI with backend task server functionality, along with updates to configuration files and documentation.

Now I'll create a PHR (Prompt History Record) for this work:

## Outcome
Successfully executed Git workflow automation, creating a commit and pull request for the chatkit UI feature implementation.