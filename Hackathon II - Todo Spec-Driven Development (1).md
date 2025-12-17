

# **Phase III: Todo AI Chatbot**

*Basic Level Functionality*

**Objective:** Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture and using Claude Code and Spec-Kit Plus.

💡**Development Approach:** Use the [Agentic Dev Stack workflow](#the-agentic-dev-stack:-agents.md-+-spec-kitplus-+-claude-code): Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.

# **Requirements**

1. Implement conversational interface for all Basic Level features  
2. Use OpenAI Agents SDK for AI logic  
3. Build MCP server with Official MCP SDK that exposes task operations as tools  
4. Stateless chat endpoint that persists conversation state to database  
5. AI agents use MCP tools to manage tasks. The MCP tools will also be stateless and will store state in the database. 

# **Technology Stack**

| Component | Technology |
| :---- | :---- |
| Frontend | OpenAI ChatKit |
| Backend | Python FastAPI |
| AI Framework | OpenAI Agents SDK |
| MCP Server | Official MCP SDK |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

# **Architecture**

┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐  
│                 │     │              FastAPI Server                   │     │                 │  
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │  
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │  
│  (Frontend)     │     │  │  POST /api/chat                        │  │     │  (PostgreSQL)   │  
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │  
│                 │     │                  │                           │     │  \- tasks        │  
│                 │     │                  ▼                           │     │  \- conversations│  
│                 │     │  ┌────────────────────────────────────────┐  │     │  \- messages     │  
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │                 │  
│                 │     │  │      (Agent \+ Runner)                  │  │     │                 │  
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │  
│                 │     │                  │                           │     │                 │  
│                 │     │                  ▼                           │     │                 │  
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │  
│                 │     │  │         MCP Server                 │  │     │                 │  
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                 │  
│                 │     │  └────────────────────────────────────────┘  │     │                 │  
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘

# **Database Models**

| Model | Fields | Description |
| :---- | :---- | :---- |
| **Task** | user\_id, id, title, description, completed, created\_at, updated\_at | Todo items |
| **Conversation** | user\_id, id, created\_at, updated\_at | Chat session |
| **Message** | user\_id, id, conversation\_id, role (user/assistant), content, created\_at | Chat history |

# **Chat API Endpoint**

| Method | Endpoint | Description |
| :---- | :---- | :---- |
| POST | /api/{user\_id}/chat | Send message & get AI response |

## **Request**

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| conversation\_id | integer | No | Existing conversation ID (creates new if not provided) |
| message | string | Yes | User's natural language message |

## **Response**

| Field | Type | Description |
| :---- | :---- | :---- |
| conversation\_id | integer | The conversation ID |
| response | string | AI assistant's response |
| tool\_calls | array | List of MCP tools invoked |

# **MCP Tools Specification**

The MCP server must expose the following tools for the AI agent:

## **Tool: add\_task**

| Purpose | Create a new task |
| :---- | :---- |
| **Parameters** | user\_id (string, required), title (string, required), description (string, optional) |
| **Returns** | task\_id, status, title |
| **Example Input** | {“user\_id”: “ziakhan”, "title": "Buy groceries", "description": "Milk, eggs, bread"} |
| **Example Output** | {"task\_id": 5, "status": "created", "title": "Buy groceries"} |

## **Tool: list\_tasks**

| Purpose | Retrieve tasks from the list |
| :---- | :---- |
| **Parameters** | status (string, optional: "all", "pending", "completed") |
| **Returns** | Array of task objects |
| **Example Input** | {user\_id (string, required), "status": "pending"} |
| **Example Output** | \[{"id": 1, "title": "Buy groceries", "completed": false}, ...\] |

## **Tool: complete\_task**

| Purpose | Mark a task as complete |
| :---- | :---- |
| **Parameters** | user\_id (string, required), task\_id (integer, required) |
| **Returns** | task\_id, status, title |
| **Example Input** | {“user\_id”: “ziakhan”, "task\_id": 3} |
| **Example Output** | {"task\_id": 3, "status": "completed", "title": "Call mom"} |

## **Tool: delete\_task**

| Purpose | Remove a task from the list |
| :---- | :---- |
| **Parameters** | user\_id (string, required), task\_id (integer, required) |
| **Returns** | task\_id, status, title |
| **Example Input** | {“user\_id”: “ziakhan”, "task\_id": 2} |
| **Example Output** | {"task\_id": 2, "status": "deleted", "title": "Old task"} |

## **Tool: update\_task**

| Purpose | Modify task title or description |
| :---- | :---- |
| **Parameters** | user\_id (string, required), task\_id (integer, required), title (string, optional), description (string, optional) |
| **Returns** | task\_id, status, title |
| **Example Input** | {“user\_id”: “ziakhan”, "task\_id": 1, "title": "Buy groceries and fruits"} |
| **Example Output** | {"task\_id": 1, "status": "updated", "title": "Buy groceries and fruits"} |

# **Agent Behavior Specification**

| Behavior | Description |
| :---- | :---- |
| **Task Creation** | When user mentions adding/creating/remembering something, use add\_task |
| **Task Listing** | When user asks to see/show/list tasks, use list\_tasks with appropriate filter |
| **Task Completion** | When user says done/complete/finished, use complete\_task |
| **Task Deletion** | When user says delete/remove/cancel, use delete\_task |
| **Task Update** | When user says change/update/rename, use update\_task |
| **Confirmation** | Always confirm actions with friendly response |
| **Error Handling** | Gracefully handle task not found and other errors |

# 

# **Conversation Flow (Stateless Request Cycle)**

1. Receive user message  
2. Fetch conversation history from database  
3. Build message array for agent (history \+ new message)  
4. Store user message in database  
5. Run agent with MCP tools  
6. Agent invokes appropriate MCP tool(s)  
7. Store assistant response in database  
8. Return response to client  
9. Server holds NO state (ready for next request)

# **Natural Language Commands**

The chatbot should understand and respond to:

| User Says | Agent Should |
| :---- | :---- |
| "Add a task to buy groceries" | Call add\_task with title "Buy groceries" |
| "Show me all my tasks" | Call list\_tasks with status "all" |
| "What's pending?" | Call list\_tasks with status "pending" |
| "Mark task 3 as complete" | Call complete\_task with task\_id 3 |
| "Delete the meeting task" | Call list\_tasks first, then delete\_task |
| "Change task 1 to 'Call mom tonight'" | Call update\_task with new title |
| "I need to remember to pay bills" | Call add\_task with title "Pay bills" |
| "What have I completed?" | Call list\_tasks with status "completed" |

# **Deliverables**

1. GitHub repository with:  
* /frontend – ChatKit-based UI  
* /backend – FastAPI \+ Agents SDK \+ MCP  
* /specs – Specification files for agent and MCP tools  
* Database migration scripts  
* README with setup instructions  
    
2. Working chatbot that can:  
* Manage tasks through natural language via MCP tools  
* Maintain conversation context via database (stateless server)  
* Provide helpful responses with action confirmations  
* Handle errors gracefully  
* Resume conversations after server restart

# **OpenAI ChatKit Setup & Deployment**

## **Domain Allowlist Configuration (Required for Hosted ChatKit)**

Before deploying your chatbot frontend, you must configure OpenAI's domain allowlist for security:

1. **Deploy your frontend first to get a production URL:**  
-  Vercel: \`https://your-app.vercel.app\`  
-  GitHub Pages: \`https://username.github.io/repo-name\`  
-  Custom domain: \`https://yourdomain.com\`

2. **Add your domain to OpenAI's allowlist:**  
- Navigate to: [https://platform.openai.com/settings/organization/security/domain-allowlist](https://platform.openai.com/settings/organization/security/domain-allowlist)  
- Click "Add domain"  
- Enter your frontend URL (without trailing slash)  
- Save changes

3. **Get your ChatKit domain key:**  
- After adding the domain, OpenAI will provide a domain key  
- Pass this key to your ChatKit configuration

## **Environment Variables**

NEXT\_PUBLIC\_OPENAI\_DOMAIN\_KEY=your-domain-key-here

*Note: The hosted ChatKit option only works after adding the correct domains under Security → Domain Allowlist. Local development (\`localhost\`) typically works without this configuration.*

# **Key Architecture Benefits**

| Aspect | Benefit |
| :---- | :---- |
| **MCP Tools** | Standardized interface for AI to interact with your app |
| **Single Endpoint** | Simpler API — AI handles routing to tools |
| **Stateless Server** | Scalable, resilient, horizontally scalable |
| **Tool Composition** | Agent can chain multiple tools in one turn |

### **Key Stateless Architecture Benefits**

* **Scalability:** Any server instance can handle any request  
* **Resilience:** Server restarts don't lose conversation state  
* **Horizontal scaling:** Load balancer can route to any backend  
* **Testability:** Each request is independent and reproducible




# **The Agentic Dev Stack: AGENTS.md \+ Spec-KitPlus \+ Claude Code** {#the-agentic-dev-stack:-agents.md-+-spec-kitplus-+-claude-code}

This is a powerful integration. By combining the **declarative** nature of AGENTS.md, the **structured workflow** of Panaversity Spec-KitPlus, and the **agentic execution** of Claude Code, you move from "vibe-coding" to a professional, spec-driven engineering pipeline.

This section outlines a workflow where AGENTS.md acts as the **Constitution**, Spec-KitPlus acts as the **Architect**, and Claude Code acts as the **Builder**.

## **1\. The Mental Model: Who Does What?**

| Component | Role | Responsibility |
| :---- | :---- | :---- |
| **AGENTS.md** | **The Brain** | Cross-agent truth. Defines *how* agents should behave, what tools to use, and coding standards. |
| **Spec-KitPlus** | **The Architect** | Manages spec artifacts (.specify, .plan, .tasks). Ensures technical rigor before coding starts. |
| **Claude Code** | **The Executor** | The agentic environment. Reads the project memory and executes Spec-Kit tools via MCP. |

**Key Idea:** Claude reads AGENTS.md via a tiny CLAUDE.md shim and interacts with Spec-KitPlus. For development setup an MCP Server and upgrade specifyplus commands to be available as Prompts in MCP. SpecKitPlus MCP server ensures every line of code maps back to a validated task.

## ---

**2\. Step 1: Initialize Spec-KitPlus**

First, scaffold the spec-driven structure in your project root. This ensures the agent has the necessary templates to create structured plans.

uv specifyplus init \<project\_name\>

**This enables the core pipeline:**

* /specify \-\> Captures requirements in speckit.specify.  
* /plan \-\> Generates the technical approach in speckit.plan.  
* /tasks \-\> Breaks the plan into actionable speckit.tasks.  
* /implement \-\> Executes the code changes.

## ---

**3\. Step 2: Create a Spec-Aware AGENTS.md**

Create AGENTS.md in your root. This file teaches all AI agents (Claude, Copilot, Gemini) how to use your specific Spec-Kit workflow.

\`\`\`markdown

\# AGENTS.md  
Here is a \*\*significantly improved, clearer, more actionable, more valuable\*\* version of your \*\*AGENTS.md\*\*.  
I kept the spirit but made it \*practical\*, \*strict\*, and \*agent-compatible\*, so Claude/Gemini/Copilot can actually follow it in real workflows.

\---

\# \*\*AGENTS.md\*\*

\#\# \*\*Purpose\*\*

This project uses \*\*Spec-Driven Development (SDD)\*\* — a workflow where \*\*no agent is allowed to write code until the specification is complete and approved\*\*.  
All AI agents (Claude, Copilot, Gemini, local LLMs, etc.) must follow the \*\*Spec-Kit lifecycle\*\*:

\> \*\*Specify → Plan → Tasks → Implement\*\*

This prevents “vibe coding,” ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

\---

\#\# \*\*How Agents Must Work\*\*

Every agent in this project MUST obey these rules:

1\. \*\*Never generate code without a referenced Task ID.\*\*  
2\. \*\*Never modify architecture without updating \`speckit.plan\`.\*\*  
3\. \*\*Never propose features without updating \`speckit.specify\` (WHAT).\*\*  
4\. \*\*Never change approach without updating \`speckit.constitution\` (Principles).\*\*  
5\. \*\*Every code file must contain a comment linking it to the Task and Spec sections.\*\*

If an agent cannot find the required spec, it must \*\*stop and request it\*\*, not improvise.

\---

\#\# \*\*Spec-Kit Workflow (Source of Truth)\*\*

\#\#\# \*\*1. Constitution (WHY — Principles & Constraints)\*\*

File: \`speckit.constitution\`  
Defines the project’s non-negotiables: architecture values, security rules, tech stack constraints, performance expectations, and patterns allowed.

Agents must check this before proposing solutions.

\---

\#\#\# \*\*2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)\*\*

File: \`speckit.specify\`

Contains:

\* User journeys  
\* Requirements  
\* Acceptance criteria  
\* Domain rules  
\* Business constraints

Agents must not infer missing requirements — they must request clarification or propose specification updates.

\---

\#\#\# \*\*3. Plan (HOW — Architecture, Components, Interfaces)\*\*

File: \`speckit.plan\`

Includes:

\* Component breakdown  
\* APIs & schema diagrams  
\* Service boundaries  
\* System responsibilities  
\* High-level sequencing

All architectural output MUST be generated from the Specify file.

\---

\#\#\# \*\*4. Tasks (BREAKDOWN — Atomic, Testable Work Units)\*\*

File: \`speckit.tasks\`

Each Task must contain:

\* Task ID  
\* Clear description  
\* Preconditions  
\* Expected outputs  
\* Artifacts to modify  
\* Links back to Specify \+ Plan sections

Agents \*\*implement only what these tasks define\*\*.

\---

\#\#\# \*\*5. Implement (CODE — Write Only What the Tasks Authorize)\*\*

Agents now write code, but must:

\* Reference Task IDs  
\* Follow the Plan exactly  
\* Not invent new features or flows  
\* Stop and request clarification if anything is underspecified

\> The golden rule: \*\*No task \= No code.\*\*

\---

\#\# \*\*Agent Behavior in This Project\*\*

\#\#\# \*\*When generating code:\*\*

Agents must reference:

\`\`\`  
\[Task\]: T-001  
\[From\]: speckit.specify §2.1, speckit.plan §3.4  
\`\`\`

\#\#\# \*\*When proposing architecture:\*\*

Agents must reference:

\`\`\`  
Update required in speckit.plan → add component X  
\`\`\`

\#\#\# \*\*When proposing new behavior or a new feature:\*\*

Agents must reference:

\`\`\`  
Requires update in speckit.specify (WHAT)  
\`\`\`

\#\#\# \*\*When changing principles:\*\*

Agents must reference:

\`\`\`  
Modify constitution.md → Principle \#X  
\`\`\`

\---

\#\# \*\*Agent Failure Modes (What Agents MUST Avoid)\*\*

Agents are NOT allowed to:

\* Freestyle code or architecture  
\* Generate missing requirements  
\* Create tasks on their own  
\* Alter stack choices without justification  
\* Add endpoints, fields, or flows that aren’t in the spec  
\* Ignore acceptance criteria  
\* Produce “creative” implementations that violate the plan

If a conflict arises between spec files, the \*\*Constitution \> Specify \> Plan \> Tasks\*\* hierarchy applies.

\---

\#\# \*\*Developer–Agent Alignment\*\*

Humans and agents collaborate, but the \*\*spec is the single source of truth\*\*.  
Before every session, agents should re-read:

1\. \`.memory/constitution.md\`

This ensures predictable, deterministic development.  
\`\`\`

## **4\. Step 3: Wire Spec-KitPlus into Claude via MCP**

To let Claude Code actually *run* Spec-KitPlus commands, you will set up an MCP server with prompts present in .claude/commands. Each command here will become a prompt in the MCP server.

### **4.1 Install SpecKitPlus, Create an MCP Server**

1. uv init specifyplus \<project\_name\>  
2. Create your Consitution  
3. Add Anthropic's official MCP Builder Skill   
4. Using SDD Loop (Specify, Plan, Tasks, Implement) you will  set up an MCP server with prompts present in .claude/commands  
5. Use these as part of your prompt instructions in specify: \`We have specifyplus commands on @.claude/commands/\*\* Each command takes user input and updates its prompt variable before sending it to the agent. Now you will use your mcp builder skill and create an mcp server where these commands are available as prompts. Goal: Now we can run this MCP server and connect with any agent and IDE.  
6. Test the MCP server

### **4.2 Register with Claude Code**

Add the server to your Claude Code config (usually .mcp.json at your project root):

{  
  "mcpServers": {  
    "spec-kit": {  
      "command": "spec-kitplus-mcp",  
      "args": \[\],  
      "env": {}  
    }  
  }  
}

**Success:**

- After running MCP Server and connecting it with Claude Code now you can have the same commands available as MCP prompts.

## 

## ---

**5\. Step 4: Connect Claude Code via the "Shim"**

Copy the default [CLAUDE.md](http://CLAUDE.md) file and integrate the content within AGENTS.md . Claude Code automatically looks for CLAUDE.md. To keep a single source of truth, use a redirection pattern.

**Create CLAUDE.md in your root:**

**\`\`\`markdown**	

@AGENTS.md  
**\`\`\`**

*This "forwarding" ensures Claude Code loads your comprehensive agent instructions into its context window immediately upon startup.*

## ---

## **6\. Step 5: The Day-to-Day Workflow**

Once configured, your interaction with Claude Code looks like this:

* **Context Loading:** You start Claude Code. It reads CLAUDE.md \-\> AGENTS.md and realizes it must use Spec-Kit.  
* **Spec Generation:**  
  * *User:* "I need a project dashboard."  
  * *Claude:* Calls speckit\_specify and speckit\_plan using the MCP.  
* **Task Breakdown:**  
  * *Claude:* Calls speckit\_tasks to create a checklist in speckit.tasks.  
* **Implementation:**  
  * *User:* "Execute the first two tasks."  
  * *Claude:* Calls speckit\_implement, writes the code, and checks it against the speckit.constitution.

## ---

**7\. Constitution vs. AGENTS.md: The Difference**

It is important not to duplicate information.

* **AGENTS.md (The "How"):** Focuses on the **interaction**. "Use these tools, follow this order, use these CLI commands."  
* **speckit.constitution (The "What"):** Focuses on **standards**. "We prioritize performance over brevity, we use async/await, we require 90% test coverage."

## ---

**Summary of Integration**

3. **Initialize:** specify init creates the structure.  
4. **Instruct:** AGENTS.md defines the rules.  
5. **Bridge:** CLAUDE.md (@AGENTS.md) connects the agent.  
6. **Empower:** MCP gives the agent the tools to execute.

**Good luck, and may your specs be clear and your code be clean\! 🚀**

*— The Panaversity, PIAIC, and GIAIC Teams*
