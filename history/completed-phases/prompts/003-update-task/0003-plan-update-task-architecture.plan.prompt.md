---
id: 0003
title: Plan Update Task Architecture
stage: plan
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-update-task
branch: 003-update-task
user: salim
command: /sp.plan
labels: ["architecture", "planning", "phase-0-research", "phase-1-design", "contracts"]
links:
  spec: /home/salim/Desktop/todo-app/specs/003-update-task/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-update-task/plan.md
  - specs/003-update-task/research.md
  - specs/003-update-task/data-model.md
  - specs/003-update-task/quickstart.md
  - specs/003-update-task/contracts/task_service_interface.py
  - specs/003-update-task/contracts/ui_prompts_interface.py
  - CLAUDE.md (agent context updated)
tests:
  - N/A (planning phase - no tests created)
---

## Prompt

/sp.plan

## Response snapshot

Executed complete planning workflow for Update Task feature (003-update-task) including Phase 0 (Research) and Phase 1 (Design & Contracts).

**Phase 0: Research & Decisions** - Analyzed existing codebase:
- Reviewed TaskService implementation (task_service.py): Identified in-memory storage pattern, ID generation, get_task_by_id() for reuse
- Documented validation patterns from add-task: validate_title(), validate_description() functions with error codes 001-003
- Documented ID validation from view-task: prompt_for_task_id(), get_task_by_id() with error codes 101-103
- Researched Python in-place list modification: Chose direct attribute modification (simplest, preserves identity)
- Analyzed CLI menu patterns: Decided numbered menu (1-3) consistent with main menu

**Technical Decisions Made**:
1. Update strategy: Use get_task_by_id() + direct attribute modification
2. Validation reuse: validate_title(), validate_description(), prompt_for_task_id()
3. Field selection: Numbered menu (1-3) matching main menu pattern
4. New error code: ERROR 104 for invalid field selection
5. Timestamp: Always update updated_at using Task.generate_timestamp()

**Phase 1: Design & Contracts** - Created comprehensive design artifacts:

1. **plan.md** (169 lines):
   - Summary: Enable selective field updates (title/description) via menu-driven CLI
   - Technical context: Python 3.13, pytest, in-memory, <30s performance goal
   - Constitution check: ✅ ALL 7 PRINCIPLES PASS - No violations
   - Project structure: Extends existing src/ layout (no new directories)
   - Complexity tracking: None (no violations to justify)

2. **research.md** (272 lines):
   - 5 research tasks completed with findings and decisions
   - Task location: Reuse get_task_by_id()
   - Modification: Direct attribute assignment (in-place)
   - Validation: Reuse existing functions (DRY principle)
   - UI pattern: Numbered menu (1-3)
   - Dependencies: Python standard library only

3. **data-model.md** (391 lines):
   - Task entity field mutability matrix
   - Validation rules (reused from 001/002)
   - State transition diagram (11-step flow)
   - Field modification matrix (3 options)
   - Data flow across layers (UI → Service → Storage)
   - Performance analysis: O(n) lookup, O(1) update
   - Timestamp management (ISO 8601 format)

4. **contracts/task_service_interface.py** (167 lines):
   - UpdateTaskServiceProtocol with update_task() method
   - Signature: update_task(task_id, new_title=None, new_description=None) -> Task
   - Selective update pattern (None = no change)
   - Detailed docstring with args, returns, raises, behavior, examples
   - 10 contract verification notes

5. **contracts/ui_prompts_interface.py** (354 lines):
   - UpdateTaskUIProtocol with 5 functions
   - display_field_selection_menu()
   - prompt_for_field_choice() → int (1-3)
   - get_new_task_title(current) → str
   - get_new_task_description(current) → str
   - update_task_prompt() (orchestrator)
   - Comprehensive docstrings with error handling flows

6. **quickstart.md** (572 lines):
   - 7-step implementation checklist
   - Step 1: Add constants (ERROR_104, prompts)
   - Step 2: Service layer (update_task function)
   - Step 3: UI functions (5 new functions)
   - Step 4: Main menu integration
   - Step 5: Write tests (20+ test cases)
   - Step 6: Manual testing script
   - Step 7: Code quality checks
   - Common pitfalls & solutions
   - Success criteria checklist

7. **Agent Context Update**:
   - Updated CLAUDE.md with Python 3.13, pytest, in-memory storage
   - Added to Active Technologies section

**Constitution Re-Check (Post-Design)**:
- ✅ Principle I (Spec-Driven): Complete spec, plan, contracts exist
- ✅ Principle II (CLI Only): Menu prompts only, no GUI
- ✅ Principle III (Ephemeral): In-memory operations, no file I/O
- ✅ Principle IV (Python/UV): Python 3.13, standard library, pytest
- ✅ Principle V (Clean Code): Type hints, docstrings, PEP 8 required
- ✅ Principle VI (Testing): 100% coverage requirement documented
- ✅ Principle VII (Scope): Update Task is feature #3 of fixed 5

**Key Design Patterns**:
- Reuse over reinvention: Leverages 001-add-task and 002-view-task patterns
- Selective update: None parameters signal "preserve current value"
- In-place modification: Preserves object identity, simpler than replace
- Layered architecture: UI (validation/display) → Service (business logic) → Data (storage)

## Outcome

- ✅ Impact: Complete architecture plan with research, data model, contracts, and implementation guide ready for /sp.tasks
- 🧪 Tests: Test strategy documented in quickstart.md (20+ test cases identified)
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, quickstart.md, 2 contracts)
- 🔁 Next prompts: Run `/sp.tasks` to generate task breakdown with test cases
- 🧠 Reflection: Excellent reuse of existing patterns from 001-add-task and 002-view-task. Selective update pattern (None values) provides clean API. Constitution compliance maintained across all 7 principles.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL):
  - Constitution Check (7 principles): PASS (all gates)
  - Research completeness: PASS (5 tasks, all decisions documented)
  - Contract quality: PASS (comprehensive docstrings, type hints, examples)
  - Design documentation: PASS (data model, state transitions, performance analysis)
  - Implementation guide: PASS (quickstart with 7-step checklist)
  - Overall: APPROVED FOR TASK GENERATION
- Prompt variant (if applicable): Standard /sp.plan command with no arguments
- Next experiment (smallest change to try): Proceed to /sp.tasks for task breakdown
