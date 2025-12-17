---
name: openai-stack
description: Expert guidance for OpenAI Agents SDK, ChatKit, and function calling in Phase III AI chatbot implementation. Use when implementing conversational AI with tool invocation, setting up ChatKit UI, configuring OpenAI agents with MCP tools, or converting MCP tools to OpenAI function format. Essential for stateless conversation handling, multi-turn tool execution, and natural language task management using the official OpenAI Agents SDK (agents library) and Managed ChatKit workflow architecture.
---

# OpenAI Stack

Expert guidance for implementing Phase III AI chatbot using **official** OpenAI Agents SDK and Managed ChatKit.

## ⚠️ Critical: Use Official Agents SDK

This skill covers the **official OpenAI Agents SDK** (`from agents import Agent, Runner`), NOT the standard OpenAI API. The two are fundamentally different:

- ❌ **NOT** `from openai import AsyncOpenAI` + `client.chat.completions.create()`
- ✅ **YES** `from agents import Agent, Runner, function_tool`

## Core Technologies

1. **OpenAI Agents SDK** - Official agents library with built-in session management
2. **Managed ChatKit** - Workflow-based React chat interface
3. **Function Tools** - Decorated Python functions as agent tools

---

## 1. OpenAI Agents SDK Integration

### Installation

```bash
cd phaseIII/backend
uv add openai-agents-python
```

### Basic Agent Pattern

```python
from agents import Agent, Runner, function_tool

# Define tools with decorator
@function_tool
def add_task(title: str, description: str = "") -> dict:
    """Create a new task for the user"""
    # Your implementation here
    task = create_task_in_db(title, description)
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }

@function_tool
def list_tasks(status: str = "all") -> list[dict]:
    """List user's tasks"""
    tasks = get_tasks_from_db(status)
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]

# Create agent with tools
agent = Agent(
    name="Todo Assistant",
    instructions="""You are a helpful todo assistant. Help users manage their tasks through natural language.

TOOL USAGE:
- add_task: When user mentions adding, creating, or remembering something
- list_tasks: When user asks to see, show, or list tasks
- complete_task: When user says done, complete, or finished
- delete_task: When user says delete, remove, or cancel
- update_task: When user says change, update, or rename

Always confirm actions with a friendly response.""",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

# Run agent
result = await Runner.run(agent, "Add a task to buy groceries")
print(result.final_output)
```

### Session Management (Database-Backed)

The Agents SDK supports session management. For Phase III stateless architecture with database persistence:

```python
from agents import Agent, Runner, SQLiteSession

# Option 1: SQLite Session (built-in)
session = SQLiteSession(
    user_id="user-123",
    db_path="conversations.db"
)

result = await Runner.run(
    agent=agent,
    prompt="Show me my tasks",
    session=session
)

# Option 2: Custom Session (for Neon PostgreSQL)
# Implement custom session class that inherits from Session
from agents import Session
import json

class PostgreSQLSession(Session):
    """Custom session backed by PostgreSQL"""

    def __init__(self, user_id: str, conversation_id: int, db):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.db = db

    async def load_history(self) -> list[dict]:
        """Load conversation history from database"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == self.conversation_id)
            .order_by(Message.created_at)
            .limit(20)
        )
        messages = result.scalars().all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def save_message(self, role: str, content: str):
        """Save message to database"""
        message = Message(
            conversation_id=self.conversation_id,
            user_id=self.user_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()

# Use custom session
session = PostgreSQLSession(
    user_id="user-123",
    conversation_id=conv_id,
    db=db
)

result = await Runner.run(agent, user_message, session=session)
```

### Integrating MCP Tools with Agents SDK

Convert MCP tool implementations to `@function_tool` decorated functions:

```python
from agents import function_tool
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.task_service import TaskService

# Global service instance (stateless)
task_service = TaskService()

# Global database session (injected via context)
_db_session: AsyncSession = None

def set_db_session(db: AsyncSession):
    """Set database session for current request"""
    global _db_session
    _db_session = db

@function_tool
async def add_task(title: str, description: str = "") -> dict:
    """
    Create a new task for the user.

    Args:
        title: Task title (max 200 chars)
        description: Optional task description

    Returns:
        Dictionary with task_id, status, and title
    """
    if not _db_session:
        raise RuntimeError("Database session not set")

    # Get user_id from context (set per request)
    user_id = get_current_user_id()

    task = await task_service.create_task(
        db=_db_session,
        user_id=user_id,
        title=title,
        description=description
    )

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }

@function_tool
async def list_tasks(status: str = "all") -> list[dict]:
    """
    List user's tasks with optional filtering.

    Args:
        status: Filter by status (all/pending/completed)

    Returns:
        List of task dictionaries
    """
    user_id = get_current_user_id()

    tasks = await task_service.list_tasks(
        db=_db_session,
        user_id=user_id,
        status=status
    )

    return [
        {
            "id": t.id,
            "title": t.title,
            "completed": t.completed,
            "description": t.description
        }
        for t in tasks
    ]

@function_tool
async def complete_task(task_id: int) -> dict:
    """
    Mark a task as complete.

    Args:
        task_id: ID of task to complete

    Returns:
        Dictionary with task_id, status, and title
    """
    user_id = get_current_user_id()

    task = await task_service.update_task(
        db=_db_session,
        user_id=user_id,
        task_id=task_id,
        completed=True
    )

    return {
        "task_id": task.id,
        "status": "completed",
        "title": task.title
    }

@function_tool
async def delete_task(task_id: int) -> dict:
    """
    Delete a task permanently.

    Args:
        task_id: ID of task to delete

    Returns:
        Dictionary with task_id, status, and title
    """
    user_id = get_current_user_id()

    # Get task first to return title
    task = await task_service.get_task(_db_session, user_id, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    title = task.title
    await task_service.delete_task(_db_session, user_id, task_id)

    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }

@function_tool
async def update_task(task_id: int, title: str = None, description: str = None) -> dict:
    """
    Update task title or description.

    Args:
        task_id: ID of task to update
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        Dictionary with task_id, status, and title
    """
    user_id = get_current_user_id()

    task = await task_service.update_task(
        db=_db_session,
        user_id=user_id,
        task_id=task_id,
        title=title,
        description=description
    )

    return {
        "task_id": task.id,
        "status": "updated",
        "title": task.title
    }
```

### FastAPI Integration

```python
# phaseIII/backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from agents import Agent, Runner
from contextvars import ContextVar

from app.database import get_db
from app.config import settings
from app.mcp.tools import (
    add_task, list_tasks, complete_task, delete_task, update_task,
    set_db_session
)

router = APIRouter(prefix="/api/v1", tags=["chat"])

# Context variable for user_id
current_user_id: ContextVar[str] = ContextVar('current_user_id')

def get_current_user_id() -> str:
    return current_user_id.get()

# Create agent once at module level
todo_agent = Agent(
    name="Todo Assistant",
    instructions="""You are a helpful todo assistant. Help users manage their tasks through natural language.

TOOL USAGE:
- add_task: When user mentions adding, creating, or remembering something
- list_tasks: When user asks to see, show, or list tasks
- complete_task: When user says done, complete, or finished
- delete_task: When user says delete, remove, or cancel
- update_task: When user says change, update, or rename

Always confirm actions with a friendly response.""",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint using OpenAI Agents SDK
    Stateless - all conversation state in database
    """
    try:
        # Set context for this request
        current_user_id.set(user_id)
        set_db_session(db)

        # Get or create conversation
        if request.conversation_id:
            conversation = await db.get(Conversation, request.conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        # Create session
        from app.services.chat_session import PostgreSQLSession
        session = PostgreSQLSession(
            user_id=user_id,
            conversation_id=conversation.id,
            db=db
        )

        # Run agent with session
        result = await Runner.run(
            agent=todo_agent,
            prompt=request.message,
            session=session
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=result.final_output
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Error Handling

```python
from agents import Agent, Runner

try:
    result = await Runner.run(agent, user_message, session=session)
    response = result.final_output
except Exception as e:
    # Log error
    logger.error(f"Agent execution error: {e}")

    # Return graceful error message
    response = "I encountered an error processing your request. Please try again."
```

---

## 2. Managed ChatKit Setup

### Prerequisites

**IMPORTANT**: Managed ChatKit uses a workflow-based architecture, NOT custom React components.

1. **Create OpenAI Workflow** on OpenAI platform
2. **Get Workflow ID** (format: `wf_...`)
3. **Configure domain allowlist** (for production)
4. **Get domain key** (for production)

### Installation

```bash
cd phaseIII/frontend

# Clone official starter template
git clone https://github.com/openai/openai-chatkit-starter-app.git chatkit-temp
cd chatkit-temp/managed-chatkit

# Copy to your frontend
cp -r * ../../
cd ../../
rm -rf chatkit-temp

# Install dependencies with Bun
bun install
```

### Project Structure

After setup, your frontend should have:

```
phaseIII/frontend/
├── package.json
├── .env.example
├── backend/                    # FastAPI session backend
│   ├── app/
│   │   └── main.py            # Session creation endpoint
│   └── scripts/
│       └── run.sh
├── frontend/                   # React/Vite UI
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatKitPanel.tsx
│   │   └── App.tsx
│   └── index.html
└── docs/
```

### Environment Configuration

```bash
# phaseIII/frontend/.env
OPENAI_API_KEY=sk-...
VITE_CHATKIT_WORKFLOW_ID=wf_...
VITE_API_URL=http://localhost:8000  # Optional, overrides dev proxy

# Production only:
VITE_CHATKIT_API_BASE=https://api.openai.com  # Optional
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key  # Required for production
```

### Backend Session Endpoint

The Managed ChatKit requires a backend endpoint to create sessions:

```python
# phaseIII/frontend/backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateSessionRequest(BaseModel):
    workflow_id: str

class CreateSessionResponse(BaseModel):
    client_secret: str

@app.post("/api/create-session", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Exchange workflow credentials for ChatKit client secret
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

    # Call OpenAI API to create session
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chatkit/sessions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "workflow_id": request.workflow_id
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create session: {response.text}"
            )

        data = response.json()
        return CreateSessionResponse(client_secret=data["client_secret"])
```

### Frontend Integration

```typescript
// phaseIII/frontend/frontend/src/components/ChatKitPanel.tsx
import { ChatKitPanel } from '@openai/chatkit'
import { useState, useEffect } from 'react'

export default function ChatInterface() {
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const workflowId = import.meta.env.VITE_CHATKIT_WORKFLOW_ID

  useEffect(() => {
    // Create session on mount
    async function createSession() {
      const response = await fetch('/api/create-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_id: workflowId })
      })

      const data = await response.json()
      setClientSecret(data.client_secret)
    }

    createSession()
  }, [workflowId])

  if (!clientSecret) {
    return <div>Loading chat...</div>
  }

  return (
    <div className="chat-container">
      <h1>AI Todo Assistant</h1>
      <ChatKitPanel
        clientSecret={clientSecret}
        apiUrl={import.meta.env.VITE_CHATKIT_API_BASE}
      />
    </div>
  )
}
```

### Running the Application

```bash
# Terminal 1: Start backend session server
cd phaseIII/frontend/backend
chmod +x scripts/run.sh
./scripts/run.sh

# Terminal 2: Start Vite dev server
cd phaseIII/frontend
bun run dev
```

The Vite dev server (port 3000) automatically proxies `/api/*` requests to the FastAPI backend (port 8000).

### Production Deployment

1. **Deploy backend first** to get production URL
2. **Add domain to allowlist**: https://platform.openai.com/settings/organization/security/domain-allowlist
3. **Get domain key** from OpenAI
4. **Set environment variables**:
   ```bash
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
   VITE_API_URL=https://your-backend.com
   ```
5. **Build and deploy**:
   ```bash
   bun run build
   # Deploy dist/ to your hosting platform
   ```

---

## 3. Agent + ChatKit Integration Architecture

### Complete Flow

```
User Message (ChatKit UI)
    ↓
Frontend calls /api/create-session (once)
    ↓
Frontend gets client_secret
    ↓
ChatKit Panel sends message to workflow
    ↓
OpenAI Workflow calls your backend endpoint
    ↓
Backend runs OpenAI Agents SDK
    ↓
Agent invokes tools (@function_tool)
    ↓
Tools query/update database
    ↓
Agent returns response
    ↓
Response sent to ChatKit
    ↓
ChatKit displays in UI
```

### Backend Endpoint for Workflow

Your workflow needs to call your FastAPI backend:

```python
# phaseIII/backend/app/routers/workflow.py
from fastapi import APIRouter, Depends
from agents import Agent, Runner

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])

@router.post("/process")
async def process_workflow_message(
    user_id: str,
    message: str,
    conversation_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint called by OpenAI Workflow
    Runs agent and returns response
    """
    # Set context
    current_user_id.set(user_id)
    set_db_session(db)

    # Get/create conversation
    if not conversation_id:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        conversation_id = conversation.id

    # Create session
    session = PostgreSQLSession(user_id, conversation_id, db)

    # Run agent
    result = await Runner.run(todo_agent, message, session=session)

    return {
        "response": result.final_output,
        "conversation_id": conversation_id
    }
```

---

## 4. Key Patterns & Best Practices

### Pattern 1: Stateless Function Tools

```python
# ✅ CORRECT - Stateless, database-backed
@function_tool
async def add_task(title: str, description: str = "") -> dict:
    user_id = get_current_user_id()
    db = get_db_session()

    task = await task_service.create_task(db, user_id, title, description)
    return {"task_id": task.id, "status": "created", "title": task.title}

# ❌ WRONG - Holds state in memory
tasks_cache = {}  # BAD: In-memory state

@function_tool
def add_task(title: str) -> dict:
    user_id = get_current_user_id()
    tasks_cache[user_id].append(title)  # BAD
    return {"status": "created"}
```

### Pattern 2: Type Hints for Tools

The `@function_tool` decorator uses type hints to generate JSON schemas:

```python
@function_tool
async def update_task(
    task_id: int,           # Required parameter
    title: str = None,      # Optional parameter
    description: str = None # Optional parameter
) -> dict:
    """
    Update task title or description.

    Args:
        task_id: ID of task to update
        title: New task title (optional)
        description: New task description (optional)
    """
    # Implementation
```

The SDK automatically generates:
```json
{
  "type": "function",
  "function": {
    "name": "update_task",
    "description": "Update task title or description.",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string"}
      },
      "required": ["task_id"]
    }
  }
}
```

### Pattern 3: Error Handling in Tools

```python
@function_tool
async def complete_task(task_id: int) -> dict:
    """Mark a task as complete"""
    try:
        user_id = get_current_user_id()
        db = get_db_session()

        task = await task_service.update_task(
            db, user_id, task_id, completed=True
        )

        if not task:
            raise ValueError(f"Task {task_id} not found")

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }
    except ValueError as e:
        # Agent will see this error and can respond appropriately
        raise ValueError(f"Could not complete task: {str(e)}")
```

### Pattern 4: Agent Handoffs (Advanced)

For complex workflows, agents can hand off to specialized agents:

```python
from agents import Agent

# Specialized agents
list_agent = Agent(
    name="Task Lister",
    instructions="You specialize in showing tasks clearly",
    tools=[list_tasks]
)

create_agent = Agent(
    name="Task Creator",
    instructions="You specialize in creating well-structured tasks",
    tools=[add_task]
)

# Main router agent
main_agent = Agent(
    name="Todo Assistant",
    instructions="Route to specialized agents based on user intent",
    handoffs=[list_agent, create_agent]
)
```

---

## 5. Testing Patterns

### Test Function Tools

```python
# tests/test_tools.py
import pytest
from app.mcp.tools import add_task, list_tasks, set_db_session
from app.models import Task

@pytest.mark.asyncio
async def test_add_task(db_session):
    """Test add_task function tool"""
    set_db_session(db_session)

    # Set user context
    from app.mcp.tools import current_user_id
    current_user_id.set("test-user")

    # Call tool
    result = await add_task(
        title="Buy groceries",
        description="Milk, eggs, bread"
    )

    assert result["status"] == "created"
    assert result["title"] == "Buy groceries"
    assert "task_id" in result

    # Verify in database
    task = await db_session.get(Task, result["task_id"])
    assert task.user_id == "test-user"
    assert task.title == "Buy groceries"
```

### Test Agent Execution

```python
@pytest.mark.asyncio
async def test_agent_add_task(db_session):
    """Test agent understanding and tool invocation"""
    from agents import Agent, Runner
    from app.mcp.tools import add_task, set_db_session, current_user_id

    # Setup
    set_db_session(db_session)
    current_user_id.set("test-user")

    # Create agent
    agent = Agent(
        name="Test Agent",
        instructions="You help manage tasks",
        tools=[add_task]
    )

    # Run agent
    result = await Runner.run(
        agent=agent,
        prompt="I need to remember to buy groceries"
    )

    # Verify agent called tool
    assert "created" in result.final_output.lower() or "added" in result.final_output.lower()

    # Verify task in database
    tasks = await db_session.execute(
        select(Task).where(Task.user_id == "test-user")
    )
    tasks_list = tasks.scalars().all()
    assert len(tasks_list) == 1
    assert "groceries" in tasks_list[0].title.lower()
```

---

## 6. Common Pitfalls

### Pitfall 1: Using Standard OpenAI API Instead of Agents SDK

```python
# ❌ WRONG - This is NOT the Agents SDK
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=key)
response = await client.chat.completions.create(...)

# ✅ CORRECT - This IS the Agents SDK
from agents import Agent, Runner
agent = Agent(name="Assistant", instructions="...", tools=[...])
result = await Runner.run(agent, prompt)
```

### Pitfall 2: Not Setting Request Context

```python
# ❌ WRONG - Tools can't access user_id or db
@function_tool
async def add_task(title: str) -> dict:
    # How do we get user_id? How do we access database?
    pass

# ✅ CORRECT - Set context per request
from contextvars import ContextVar

current_user_id: ContextVar[str] = ContextVar('current_user_id')
current_db_session: ContextVar[AsyncSession] = ContextVar('current_db_session')

# In endpoint:
current_user_id.set(user_id)
current_db_session.set(db)

# In tool:
@function_tool
async def add_task(title: str) -> dict:
    user_id = current_user_id.get()
    db = current_db_session.get()
    # Now we have access!
```

### Pitfall 3: Custom ChatKit Components

```typescript
// ❌ WRONG - Building custom chat UI (don't do this with Managed ChatKit)
export function CustomChatInterface() {
  const [messages, setMessages] = useState([])
  // Custom implementation
}

// ✅ CORRECT - Use official ChatKitPanel
import { ChatKitPanel } from '@openai/chatkit'

export function ChatInterface() {
  return <ChatKitPanel clientSecret={secret} />
}
```

### Pitfall 4: Missing Session Backend

```typescript
// ❌ WRONG - ChatKitPanel without session endpoint
<ChatKitPanel workflowId={workflowId} />  // Will fail - needs client_secret

// ✅ CORRECT - Create session first
const [secret, setSecret] = useState(null)

useEffect(() => {
  fetch('/api/create-session', {
    method: 'POST',
    body: JSON.stringify({ workflow_id: workflowId })
  })
  .then(r => r.json())
  .then(data => setSecret(data.client_secret))
}, [])

{secret && <ChatKitPanel clientSecret={secret} />}
```

---

## 7. Phase III Requirements Checklist

### Backend Requirements

✅ Use OpenAI Agents SDK (`from agents import Agent, Runner`)
✅ Define tools with `@function_tool` decorator
✅ Implement stateless tools (no in-memory state)
✅ Store all state in database (Neon PostgreSQL)
✅ Implement all 5 required tools (add, list, complete, delete, update)
✅ User ID scoping for all operations
✅ Session management (PostgreSQL-backed or SQLite)
✅ Error handling in tools

### Frontend Requirements

✅ Use Managed ChatKit Starter template
✅ Implement `/api/create-session` backend endpoint
✅ Use `ChatKitPanel` component (not custom UI)
✅ Configure workflow ID
✅ Set up domain allowlist (production)
✅ Environment variables configured

### Integration Requirements

✅ Agent runs on user messages
✅ Tools query/update database correctly
✅ Conversation history persists across sessions
✅ Server is stateless (no in-memory conversation state)
✅ Natural language understanding works for all 5 task operations

---

## Key Success Metrics

✅ Agent correctly identifies user intent and invokes appropriate tools
✅ All 5 tools work correctly with database
✅ Multi-turn conversations maintain context
✅ ChatKit UI displays messages correctly
✅ Server is stateless - all state in database
✅ Conversation can resume after server restart
✅ User isolation enforced (users can't access others' tasks)

---

## Official Documentation Links

- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **Managed ChatKit Starter**: https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit
- **ChatKit Documentation**: https://platform.openai.com/docs/guides/chatkit
- **Domain Allowlist**: https://platform.openai.com/settings/organization/security/domain-allowlist
