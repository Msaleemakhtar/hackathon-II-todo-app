---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The `/sp.autopilot` command automates the post-specification workflow by orchestrating `/sp.clarify`, `/sp.plan`, `/sp.adr`, `/sp.tasks`, and `/sp.implement` with user approval gates between each phase.

**Prerequisites:**
- Must be run AFTER `/sp.specify` has created spec.md
- Requires active feature branch (NNN-feature-name format)
- Constitution must exist at `.specify/memory/constitution.md`

**Optional Arguments:**

```bash
/sp.autopilot                    # Start from beginning (validation phase)
/sp.autopilot --resume planning  # Resume from specific phase
/sp.autopilot --skip-adr         # Skip ADR detection phase
```

**Supported Resume Points:**
- `validation` - Start from spec validation
- `clarification` - Start from clarification questions
- `planning` - Start from plan generation
- `adr` - Start from ADR detection
- `tasks` - Start from task breakdown
- `implementation` - Start from implementation

---

## Execution Flow

### Step 1: Parse Arguments and Detect Starting Phase

1. **Check for resume flag:**
   ```bash
   if $ARGUMENTS contains "--resume {phase-name}":
       starting_phase = {phase-name}
   else:
       starting_phase = "validation"
   ```

2. **Check for skip flags:**
   ```bash
   skip_phases = []
   if $ARGUMENTS contains "--skip-adr":
       skip_phases.append("adr")
   ```

3. **Validate starting phase:**
   - Must be one of: validation, clarification, planning, adr, tasks, implementation
   - If invalid, error and show supported phases

### Step 2: Load Feature Context

1. **Run prerequisite check:**
   ```bash
   .specify/scripts/bash/check-prerequisites.sh --json
   ```

2. **Parse JSON output:**
   ```json
   {
     "feature_number": "002",
     "feature_name": "edit-task",
     "spec_file": "/path/to/specs/002-edit-task/spec.md",
     "plan_file": "/path/to/specs/002-edit-task/plan.md",
     "tasks_file": "/path/to/specs/002-edit-task/tasks.md",
     "feature_dir": "/path/to/specs/002-edit-task"
   }
   ```

3. **Validate required artifacts exist:**
   - If starting_phase = "validation": Require spec.md exists
   - If starting_phase = "planning": Require spec.md exists
   - If starting_phase = "tasks": Require spec.md AND plan.md exist
   - If starting_phase = "implementation": Require spec.md AND plan.md AND tasks.md exist

4. **If validation fails:**
   ```
   ❌ Error: Missing required artifact for phase {phase-name}

   Required:
   - {list-of-missing-files}

   Suggestion:
   - Run /sp.autopilot from earlier phase
   - Or run missing command manually: /sp.{command-name}
   ```

### Step 3: Invoke Pipeline Orchestrator Subagent

Launch the `pipeline-orchestrator` subagent using the Task tool:

```markdown
You are the Pipeline Orchestrator for Spec-Driven Development.

**Context:**
- Feature: {feature_number}-{feature_name}
- Starting Phase: {starting_phase}
- Skip Phases: {skip_phases}
- Feature Directory: {feature_dir}
- Spec File: {spec_file}
- Plan File: {plan_file} (if exists)
- Tasks File: {tasks_file} (if exists)

**Your Task:**
Execute the SDD pipeline starting from {starting_phase} phase with the following requirements:

1. **User Approval Required:** Pause at the end of EVERY phase and ask user to approve before proceeding to next phase
2. **Phase Execution Order:**
   - Phase 1: Spec Validation (if starting_phase <= validation)
   - Phase 2: Clarification (if needed, if starting_phase <= clarification)
   - Phase 3: Planning (if starting_phase <= planning)
   - Phase 4: ADR Detection (if starting_phase <= adr AND not in skip_phases)
   - Phase 5: Task Breakdown (if starting_phase <= tasks)
   - Phase 6: Implementation (if starting_phase <= implementation)

3. **Approval Gate Pattern:**
   After each phase completes, use AskUserQuestion tool:
   ```
   question: "Phase {N} complete: {summary}. Proceed to next phase?"
   options:
     - "Yes, continue pipeline"
     - "No, let me review manually"
     - "Skip next phase"
   ```

4. **Error Handling:**
   - On phase failure: Show error, suggest recovery options, exit pipeline
   - On user "No": Save state, provide resume instructions, exit cleanly
   - On user "Skip": Mark phase as skipped, continue to next phase

5. **Scope Boundaries:**
   - DO NOT handle git operations (commit, PR creation)
   - DO NOT auto-create ADRs (suggest only, wait for user consent)
   - DO use SlashCommand tool to invoke: /sp.clarify, /sp.plan, /sp.tasks, /sp.implement
   - DO use AskUserQuestion for all approval gates

6. **Final Output:**
   When pipeline completes (or user exits), generate execution report:
   ```markdown
   # Pipeline Execution Report: {feature-number}

   ## Timeline
   - Started: {timestamp}
   - Completed: {timestamp}
   - Total Duration: {minutes}

   ## Phase Results
   | Phase | Status | Duration | Issues |
   |-------|--------|----------|--------|
   | ... | ... | ... | ... |

   ## Artifacts Generated
   - {list-of-files-created}

   ## Next Steps
   1. Review implementation
   2. Run /sp.git.commit_pr to create PR
   3. Optional: Create {N} suggested ADRs
   ```

7. **Resume State Tracking:**
   If user exits mid-pipeline, output:
   ```
   ⏸️  Pipeline paused at Phase {N}: {phase-name}

   Resume with: /sp.autopilot --resume {next-phase-name}
   ```

**Constraints:**
- Follow the pipeline-orchestrator.md agent instructions exactly
- Never auto-proceed without user approval
- Preserve all existing files (never overwrite without user consent)
- Use Read tool to load spec.md, plan.md, tasks.md
- Use Bash tool for check-prerequisites.sh only
- Use SlashCommand tool to invoke /sp.* commands
- Use AskUserQuestion for all approval gates

**Success Criteria:**
- All phases executed in order (or skipped with user approval)
- All approval gates honored
- All artifacts generated or updated
- User has clear next steps

Begin pipeline execution now.
```

### Step 4: Monitor Pipeline Execution

The pipeline-orchestrator subagent will:

1. Execute each phase sequentially
2. Pause for user approval between phases
3. Handle errors and user interruptions
4. Generate final execution report

You should:
- Wait for the subagent to complete
- Display the final execution report to user
- Provide next step guidance

---

## Error Handling

### No Spec Found
```
❌ Error: No spec.md found for current feature

Please run /sp.specify first to create specification:
  /sp.specify "your feature description"
```

### Invalid Resume Phase
```
❌ Error: Invalid resume phase '{phase-name}'

Supported phases:
  - validation
  - clarification
  - planning
  - adr
  - tasks
  - implementation

Example: /sp.autopilot --resume planning
```

### Missing Artifacts for Resume
```
❌ Error: Cannot resume from '{phase-name}' - missing required artifacts

Required for this phase:
  - specs/{feature}/spec.md
  - specs/{feature}/plan.md

Please run earlier phases first or start from beginning:
  /sp.autopilot
```

### Subagent Failure
```
❌ Pipeline orchestrator failed: {error-message}

Recovery options:
1. Check error details above
2. Fix the issue and retry: /sp.autopilot --resume {last-successful-phase}
3. Continue manually with next command: /sp.{next-command}
```

---

## Examples

### Example 1: Full Pipeline (Happy Path)

```bash
User: /sp.autopilot

Orchestrator: Starting pipeline for feature 002-edit-task...

[Phase 1: Validation]
✅ Spec validation: PASS (all 6 criteria met)
Proceed to planning? → User: Yes

[Phase 2: Clarification]
Skipped (validation passed)

[Phase 3: Planning]
✅ Plan generated: 5 architecture decisions documented
Proceed to ADR detection? → User: Yes

[Phase 4: ADR Detection]
📋 Detected 2 ADR-worthy decisions
Create ADRs now? → User: Create later

[Phase 5: Tasks]
✅ Tasks generated: 8 tasks, dependency-ordered
Proceed to implementation? → User: Yes

[Phase 6: Implementation]
✅ All 8 tasks complete, tests passing (12/12)

✅ Pipeline complete! Next: /sp.git.commit_pr
```

### Example 2: Resume from Specific Phase

```bash
# User completed planning manually, wants to resume
User: /sp.autopilot --resume tasks

Orchestrator: Resuming pipeline from tasks phase...

[Phase 5: Tasks]
✅ Tasks generated: 6 tasks
Proceed to implementation? → User: Yes

[Phase 6: Implementation]
✅ Implementation complete

✅ Pipeline complete!
```

### Example 3: User Pauses for Review

```bash
User: /sp.autopilot

[Phase 1-3: Complete]

[Phase 4: ADR Detection]
📋 Detected 1 ADR-worthy decision: Database schema migration
Create ADR now? → User: Yes, pause for ADR

⏸️  Pipeline paused. Please run:
   /sp.adr database-schema-migration-strategy

Resume with: /sp.autopilot --resume tasks
```

### Example 4: Skip ADR Phase

```bash
User: /sp.autopilot --skip-adr

[Phases 1-3: Complete]

[Phase 4: ADR Detection]
Skipped by user request (--skip-adr flag)

[Phase 5: Tasks]
✅ Tasks generated...
```

---

## PHR Creation

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: misc (pipeline orchestration is meta-workflow)

2) Generate Title and Determine Routing:
   - Generate Title: "pipeline-execution-{feature-number}" or "autopilot-{phase-started}"
   - Route: `history/prompts/<feature-name>/` (feature-specific pipeline run)

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage misc [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding:
     - PROMPT_TEXT: Full user command with arguments
     - RESPONSE_TEXT: Pipeline execution report (summary of phases, decisions, outcomes)
     - FILES_YAML: List artifacts created (plan.md, tasks.md, implementation files)
     - TESTS_YAML: List tests run during implementation
     - OUTCOME_IMPACT: "Pipeline automated {N} phases, {M} artifacts generated"
     - REFLECTION_NOTE: "Approval gates honored, user {paused/completed} at phase {N}"
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md`
     - Allocate an ID; compute the output path; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.

---

## Notes

- This command is the PRIMARY interface for workflow automation
- User MUST approve between phases (no full automation without gates)
- Git operations (commit, PR) remain manual (not handled by pipeline)
- ADR creation remains manual (pipeline only suggests)
- Pipeline state can be saved and resumed at any phase
- Cross-project reusable (relies on constitution + templates)