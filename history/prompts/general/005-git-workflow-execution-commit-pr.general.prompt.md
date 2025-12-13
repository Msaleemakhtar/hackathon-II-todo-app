---
id: "005"
title: "Git Workflow Execution Commit PR"
stage: "general"
date_iso: "2025-12-13"
surface: "agent"
model: "unknown"
feature: "none"
branch: "004-better-auth-integration"
user: "salim"
command: "agentic Git workflow to commit changes and create PR"
labels: ["git", "workflow", "commit", "pull-request"]
spec: null
ticket: null
adr: null
pr: "https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/4"
files_yaml:
  - "/home/salim/Desktop/hackathon-II-todo-app/.gemini/settings.json"
  - "/home/salim/Desktop/hackathon-II-todo-app/.specify/memory/constitution.md"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/.env"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/.env.example"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/Dockerfile"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/README.md"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/alembic/env.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/pyproject.toml"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/core/config.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/core/exceptions.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/core/security.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/main.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/models/__init__.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/models/task.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/models/user.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/routers/tags.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/routers/tasks.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/schemas/tag.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/schemas/task.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/services/tag_service.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/src/services/task_service.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/conftest.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_models.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/uv.lock"
  - "/home/salim/Desktop/hackathon-II-todo-app/docker-compose.yml"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/README.md"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/bun.lock"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/package.json"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/categories/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/dashboard/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/layout.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/login/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/my-tasks/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/settings/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/signup/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/app/vital-tasks/page.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/dashboard/TaskStatusChart.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/layout/Header.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/layout/Sidebar.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/CompletedTaskList.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/CreateTaskForm.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/CreateTaskModal.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/TaskCard.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/TaskDetailModal.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/tasks/TaskList.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/components/withAuth.tsx"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/hooks/useAuth.ts"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/hooks/useTasks.ts"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/store/ui-store.ts"
  - "/home/salim/Desktop/hackathon-II-todo-app/frontend/src/types/index.ts"
tests_yaml:
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_categories.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_db_connection.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_fixtures.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_tags.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_task_tag_integration.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_tasks.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_user_profile.py"
  - "/home/salim/Desktop/hackathon-II-todo-app/backend/tests/test_utils.py"
prompt_text: |
  ---
  description: An autonomous Git agent that intelligently executes git workflows. Your task is to commit the work and create PR.
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
  ```
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
response_text: |
  I analyzed the Git repository and executed the following workflow:

  1. Gathered repository context (status, changes, branch info, etc.)
  2. Determined that there were many uncommitted changes on the existing feature branch `004-better-auth-integration`
  3. Created a meaningful commit with the message: "feat(004-better-auth-integration): Implement Better Auth integration with enhanced security and user management"
  4. Pushed the changes to the remote repository with upstream tracking
  5. Created a pull request with an appropriate title and description

  ✅ Workflow executed successfully:
    • Branch: 004-better-auth-integration
    • Commit: "feat(004-better-auth-integration): Implement Better Auth integration with enhanced security and user management"
    • PR: https://github.com/Msaleemakhtar/hackathon-II-todo-app/pull/4

  The PR includes all the changes related to Better Auth integration, which enhances the authentication system of the todo app with improved security measures and user management capabilities.

outcome: |
  Successfully completed the Git workflow by committing all changes and creating a pull request. The PR has been created with an appropriate title and description explaining the Better Auth integration changes.
evaluation: |
  The executed workflow perfectly matched the user's intent. All changes were committed, pushed to the remote repository, and a pull request was created with an appropriate title and description. The task completed successfully without requiring any human validation during the process.
---