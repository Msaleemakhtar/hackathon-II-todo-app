---
id: "0003"
title: "Constitution v2.2.0 Refinements"
stage: constitution
date: 2025-12-09
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: none
user: Msaleemakhtar
command: /sp.constitution
labels: ["constitution", "governance", "phase-ii", "jwt-security", "ci-cd", "sdd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitutional document; validation via 4 self-checks)
---

## Prompt

You are updating the project constitution at `.specify/memory/constitution.md` based on specific enhancement requirements.

## Context
The current constitution is at version 2.1.1 and needs refinement to improve clarity, practicality, and technical precision while maintaining quality standards.

## Required Changes

### 1. Make "No Manual Coding" Exception More Flexible (Section I)
- **Current Issue**: "three refinement cycles" rule is too rigid
- **Action**: Replace the rigid three-cycle limit with more flexible language such as "reasonable refinement efforts" while keeping strict documentation and review requirements
- **Location**: Section I "Spec-Driven Development" - the "Exception for AI Limitations" paragraph

### 2. Clarify "Optional" Security Features (Section IV)
- **Current Issue**: "Refresh token rotation" and "Token blacklisting" marked as "optional" creates ambiguity
- **Action**: Remove "optional" status and explicitly state these features are out of scope for Phase II, targeted for future implementation
- **Location**: Section IV "User Authentication & JWT Security" - the "Security Standards" subsection

### 3. Refine CI/CD Quality Gates for Practicality (Section IX)
- **Current Issue**: Expensive performance and strict coverage checks on every PR slow development
- **Action**:
  - Modify "PR Checks" to mandate PRs must not decrease overall coverage percentage
  - Move strict threshold checks (coverage >= 80%, Lighthouse >= 90) to a separate non-blocking "Nightly Pipeline" for main branch health reporting
- **Location**: Section IX "CI/CD Pipeline" - the "GitHub Actions Workflows" subsection

### 4. Specify JWT Issuance Roles (Section IV)
- **Current Issue**: Ambiguity about whether frontend or backend issues JWT
- **Action**: Clarify that frontend sends credentials but backend is solely responsible for authenticating users and issuing JWTs. Frontend only receives and manages tokens.
- **Location**: Section IV "User Authentication & JWT Security" - the "Authentication Flow" subsection

### 5. Mandate Explicit User ID Matching in APIs (Section IV)
- **Current Issue**: Data isolation rule can be more specific
- **Action**: Enhance "Data Scoping" requirement to add rule that when user ID is in API path (e.g., /users/{user_id}/tasks), the user ID from validated JWT must be compared against the path parameter
- **Location**: Section IV "User Authentication & JWT Security" - add to "Backend Validation" or "Data Scoping" points

### 6. Update Document Version
- Increment version to 2.2.0
- Update "Last Amended" date to 2025-12-09
- Create a Sync Impact Report as HTML comment at top documenting all changes

## Execution Steps

1. Read the current constitution at `.specify/memory/constitution.md`
2. Apply each of the 6 required changes precisely
3. Update the version from 2.1.1 to 2.2.0 (MINOR bump - material expansions and clarifications)
4. Update "Last Amended" date to 2025-12-09
5. Create a comprehensive Sync Impact Report as HTML comment prepended to the file showing:
   - Version change: 2.1.1 -> 2.2.0
   - Modified principles/sections with descriptions
   - Templates requiring updates (if any)
   - Follow-up TODOs (if any)
6. Validate no unresolved placeholders remain
7. Write the updated constitution back to `.specify/memory/constitution.md`
8. Return a summary with:
   - Version bump rationale
   - List of all changes made
   - Any files flagged for follow-up
   - Suggested commit message

## Critical Requirements
- Maintain all existing structure and formatting
- Keep all other sections unchanged unless specified above
- Ensure changes improve clarity without reducing quality standards
- Use precise, testable language (MUST/SHOULD with clear rationale)
- Preserve all heading hierarchy
- Keep rationale statements for each change

Please proceed with these updates systematically.

## Response snapshot

Successfully updated the constitution from version 2.1.1 to 2.2.0 with six targeted refinements:

1. **Section I** - Replaced rigid "three refinement cycles" with flexible "reasonable refinement efforts" language
2. **Section IV** - Clarified JWT issuance: backend solely responsible, frontend only receives/manages tokens
3. **Section IV** - Added explicit path parameter user ID matching requirement (SEC-004)
4. **Section IV** - Moved refresh token rotation and token blacklisting from "optional" to "Phase II Scope Boundaries" (out of scope, Phase III target)
5. **Section IX** - Restructured CI/CD: PR checks now require "no coverage decrease", strict thresholds moved to non-blocking Nightly Pipeline
6. **Version/Metadata** - Updated to 2.2.0, amended date 2025-12-09, comprehensive Sync Impact Report added

All four constitutional self-checks pass. No unresolved placeholders detected.

## Outcome

- Impact: Constitution upgraded from v2.1.1 to v2.2.0 with improved flexibility, clarity, and practicality. Added SEC-004 security requirement for path parameter validation. CI/CD pipeline optimized for developer velocity.
- Tests: None (constitutional document; validation via 4 self-checks: Alignment PASS, Coverage PASS, Conflict-Free PASS, Completeness PASS)
- Files: Modified .specify/memory/constitution.md
- Next prompts: Create GitHub Actions workflow for Nightly Pipeline, consider ADR for CI/CD restructuring decision, update spec files if they reference "three refinement cycles"
- Reflection: Separating blocking PR checks from comprehensive nightly audits balances quality enforcement with developer velocity - a pattern applicable to other governance constraints.

## Evaluation notes (flywheel)

- Failure modes observed: None - all changes applied cleanly with consistent formatting preserved
- Graders run and results (PASS/FAIL): Alignment PASS, Coverage PASS, Conflict-Free PASS, Completeness PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
