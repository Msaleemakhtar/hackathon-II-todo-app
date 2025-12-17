# AGENTS.md 

## Spec-Driven Development (SDD) Rules
- No code without completed specification (spec.md)
- Follow workflow: Specify → Plan → Tasks → Implement
- No task = No code (golden rule)

## File Structure
- Constitution: `.specify/memory/constitution.md`
- Specs: `specs/sphaseIII/NNN-feature-name/spec.md`
- Plans: `specs/sphaseIII/NNN-feature-name/plan.md`
- Tasks: `specs/sphaseIII/NNN-feature-name/tasks.md`

## Critical Requirements
- NO imports from Phase II codebase
- Phase III code in `phaseIII/` directory only
- Use separate tables (tasks_phaseiii, not tasks)
- MCP Server with 5 tools required
- Use UV (backend) and Bun (frontend) package managers
- Better Auth for authentication

## Code References
When generating code, include:
```
[Task]: T-001
[From]: spec §2.1, plan §3.4
```

## Failure Modes to Avoid
- Don't freestyle code without specs
- Don't ignore constitutional requirements
- Don't mix Phase II/III code
- Don't create features without specs

## **Technology Stack Requirements (Mandatory for Phase III)**
Agents MUST use these specific technologies for Phase III implementation:
  * **Frontend**: OpenAI ChatKit (https://platform.openai.com/docs/guides/chatkit)
  * **Template for chatkit Integration with Backend**: Managed ChatKit Starter (https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit)
  * **Backend**: Python FastAPI
  * **AI Framework**: OpenAI Agents SDK (https://github.com/openai/openai-agents-python)
  * **MCP Server**: Official MCP SDK (https://github.com/modelcontextprotocol/python-sdk)
  * **ORM**: SQLModel
  * **Database**: Neon Serverless PostgreSQL
  * **Authentication**: Better Auth
  * **Backend Package Manager**: UV (`uv add <package>`)
  * **Frontend Package Manager**: Bun (`bun add <package>`)
  * **Better-Auth**: https://www.better-auth.com/
