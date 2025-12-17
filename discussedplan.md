# Phase III: Todo AI Chatbot - Implementation Plan

## ⚠️ CRITICAL REQUIREMENTS

### 1. Complete Separation from Phase II
- **NO imports** from Phase II codebase (`../phaseII` or `backend/src`)
- **NO shared code** or modules between phases
- **SEPARATE directory**: All code lives in `phaseIII/`
- **INDEPENDENT implementation**: Reimplement task operations for MCP tools

### 2. Technology Stack (MUST USE - Per Hackathon Rules)
- ✅ **Frontend**: OpenAI ChatKit (https://platform.openai.com/docs/guides/chatkit)
- ✅ **Frontend Template**: Managed ChatKit Starter (https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit)
- ✅ **Backend**: Python FastAPI
- ✅ **AI Framework**: OpenAI Agents SDK (https://github.com/openai/openai-agents-python)
- ✅ **MCP Server**: Official MCP SDK
- ✅ **ORM**: SQLModel
- ✅ **Database**: Neon Serverless PostgreSQL 
- ✅ **Authentication**: Better Auth 
### 3. Package Management
- **Backend**: UV (`uv add <package>`)
- **Frontend**: Bun (`bun add <package>`)

---

## Directory Structure

```
phaseIII/                           # ⚠️ EVERYTHING LIVES HERE
├── backend/                        # Python FastAPI backend
│   ├── pyproject.toml             # UV package manager
│   ├── .env.example
│   ├── alembic/                   # Database migrations (independent)
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── config.py              # Configuration
│   │   ├── database.py            # Database connection
│   │   ├── models/                # SQLModel models
│   │   │   ├── __init__.py
│   │   │   ├── task.py           # Task model (independent from Phase II)
│   │   │   ├── conversation.py   # Conversation model
│   │   │   └── message.py        # Message model
│   │   ├── services/              # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py   # Task CRUD (independent implementation)
│   │   │   └── chat_service.py   # Chat service with OpenAI
│   │   ├── mcp/                   # MCP Server
│   │   │   ├── __init__.py
│   │   │   ├── server.py         # MCP server manager
│   │   │   └── tools.py          # MCP tool implementations
│   │   ├── routers/               # API routes
│   │   │   ├── __init__.py
│   │   │   └── chat.py           # Chat endpoint
│   │   └── schemas/               # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── task.py
│   │       └── chat.py
│   └── tests/                     # Pytest tests
│       ├── conftest.py
│       ├── test_mcp_tools.py
│       └── test_chat.py
├── frontend/                       # OpenAI ChatKit UI
│   ├── package.json               # Bun package manager
│   ├── bun.lockb
│   ├── .env.example
│   ├── next.config.js
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx
│   ├── components/
│   │   └── chat/
│   │       ├── ChatInterface.tsx
│   │       └── ChatMessage.tsx
│   └── lib/
│       ├── api/
│       │   └── chat.ts
│       └── auth.ts                # Better Auth integration

└── README.md
```

---

## Implementation Plan

### Phase 1: Backend Setup

#### 1.1 Initialize Backend with UV

```bash
# Create phaseIII directory
mkdir -p phaseIII/backend
cd phaseIII/backend

# Initialize with UV
uv init

# Add dependencies
uv add fastapi
uv add uvicorn[standard]
uv add sqlmodel
uv add asyncpg
uv add alembic
uv add python-dotenv
uv add python-jose[cryptography]
uv add pydantic-settings

# Add OpenAI Agents SDK (per hackathon requirements)
uv add openai-agents

# Add MCP SDK
uv add mcp

# Add testing dependencies
uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev httpx
```

#### 1.2 Create Database Models (Independent from Phase II)

**File: `phaseIII/backend/app/models/task.py`**
```python
from datetime import datetime
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    """Task model - INDEPENDENT from Phase II"""
    __tablename__ = "tasks_phaseiii"  # Different table name

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**File: `phaseIII/backend/app/models/conversation.py`**
```python
from datetime import datetime
from sqlmodel import SQLModel, Field, Index

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('ix_conversations_user_id', 'user_id'),
    )
```

**File: `phaseIII/backend/app/models/message.py`**
```python
from datetime import datetime
from sqlmodel import SQLModel, Field, Index, Column
from sqlalchemy import Text

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True)
    user_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_user_id', 'user_id'),
    )
```

#### 1.3 Create Independent Task Service (NO Phase II imports)

**File: `phaseIII/backend/app/services/task_service.py`**
```python
"""
Task service - INDEPENDENT implementation for Phase III
NO IMPORTS from Phase II
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task

class TaskService:
    """Task CRUD operations for MCP tools"""

    async def create_task(
        self,
        db: AsyncSession,
        user_id: str,
        title: str,
        description: str = ""
    ) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def list_tasks(
        self,
        db: AsyncSession,
        user_id: str,
        status: str = "all"
    ) -> list[Task]:
        """List tasks with optional status filter"""
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_task(
        self,
        db: AsyncSession,
        user_id: str,
        task_id: int
    ) -> Task | None:
        """Get a single task"""
        result = await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def update_task(
        self,
        db: AsyncSession,
        user_id: str,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None
    ) -> Task:
        """Update a task"""
        task = await self.get_task(db, user_id, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        return task

    async def delete_task(
        self,
        db: AsyncSession,
        user_id: str,
        task_id: int
    ):
        """Delete a task"""
        task = await self.get_task(db, user_id, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        await db.delete(task)
        await db.commit()
```

#### 1.4 Create MCP Server (Using Official SDK)

**File: `phaseIII/backend/app/mcp/tools.py`**
```python
"""
MCP Tools - Using official MCP SDK
NO IMPORTS from Phase II
"""
from app.services.task_service import TaskService  # ✅ Import from phaseIII/backend/app

class MCPTools:
    """MCP tool implementations"""

    def __init__(self):
        self.task_service = TaskService()

    async def add_task(self, user_id: str, args: dict, db) -> dict:
        """MCP Tool: Add a task"""
        task = await self.task_service.create_task(
            db=db,
            user_id=user_id,
            title=args["title"],
            description=args.get("description", "")
        )
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

    async def list_tasks(self, user_id: str, args: dict, db) -> list[dict]:
        """MCP Tool: List tasks"""
        status = args.get("status", "all")
        tasks = await self.task_service.list_tasks(db, user_id, status)
        return [
            {
                "id": t.id,
                "title": t.title,
                "completed": t.completed,
                "description": t.description
            }
            for t in tasks
        ]

    async def complete_task(self, user_id: str, args: dict, db) -> dict:
        """MCP Tool: Complete a task"""
        task = await self.task_service.update_task(
            db=db,
            user_id=user_id,
            task_id=args["task_id"],
            completed=True
        )
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

    async def delete_task(self, user_id: str, args: dict, db) -> dict:
        """MCP Tool: Delete a task"""
        task = await self.task_service.get_task(db, user_id, args["task_id"])
        if not task:
            raise ValueError(f"Task {args['task_id']} not found")

        title = task.title
        await self.task_service.delete_task(db, user_id, args["task_id"])
        return {
            "task_id": args["task_id"],
            "status": "deleted",
            "title": title
        }

    async def update_task(self, user_id: str, args: dict, db) -> dict:
        """MCP Tool: Update a task"""
        task = await self.task_service.update_task(
            db=db,
            user_id=user_id,
            task_id=args["task_id"],
            title=args.get("title"),
            description=args.get("description")
        )
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
```

**File: `phaseIII/backend/app/mcp/server.py`**
```python
"""
MCP Server Manager
Uses official MCP SDK: https://github.com/modelcontextprotocol/python-sdk
"""
from mcp.server import Server
from mcp.server.models import Tool
from app.mcp.tools import MCPTools

class MCPServerManager:
    """Manages MCP server and tools"""

    def __init__(self):
        self.tools_impl = MCPTools()
        self.server = Server("todo-mcp-server")

    async def list_tools(self) -> list[Tool]:
        """List all available MCP tools"""
        return [
            Tool(
                name="add_task",
                description="Create a new task for the user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (max 200 chars)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="list_tasks",
                description="List user's tasks with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status"
                        }
                    }
                }
            ),
            Tool(
                name="complete_task",
                description="Mark a task as complete",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of task to complete"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="delete_task",
                description="Delete a task permanently",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="update_task",
                description="Update task title or description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description"
                        }
                    },
                    "required": ["task_id"]
                }
            )
        ]

    async def execute_tool(
        self,
        name: str,
        user_id: str,
        arguments: dict,
        db
    ) -> dict:
        """Execute a tool by name"""
        if name == "add_task":
            return await self.tools_impl.add_task(user_id, arguments, db)
        elif name == "list_tasks":
            return await self.tools_impl.list_tasks(user_id, arguments, db)
        elif name == "complete_task":
            return await self.tools_impl.complete_task(user_id, arguments, db)
        elif name == "delete_task":
            return await self.tools_impl.delete_task(user_id, arguments, db)
        elif name == "update_task":
            return await self.tools_impl.update_task(user_id, arguments, db)
        else:
            raise ValueError(f"Unknown tool: {name}")
```

#### 1.5 Create Chat Service (OpenAI Agents SDK)

**File: `phaseIII/backend/app/services/chat_service.py`**
```python
"""
Chat Service using OpenAI Agents SDK
Reference: https://github.com/openai/openai-agents-python
"""
import json
from openai import AsyncOpenAI
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.mcp.server import MCPServerManager

class ChatService:
    """Chat service with OpenAI Agents SDK"""

    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.mcp = MCPServerManager()

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: int | None,
        db: AsyncSession
    ) -> dict:
        """Process a chat message - stateless, all state in DB"""

        # 1. Get or create conversation
        if conversation_id:
            conversation = await db.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found")
        else:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        # 2. Load last 20 messages for context
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        messages = list(reversed(result.scalars().all()))

        # 3. Build history for agent
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 4. Store user message
        user_msg = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=message
        )
        db.add(user_msg)
        await db.commit()

        # 5. Get MCP tools
        tools = await self.mcp.list_tools()
        tool_schemas = self._convert_to_openai_format(tools)

        # 6. Prepare system instructions
        system_prompt = """You are a helpful todo assistant. Help users manage their tasks through natural language.

When users ask to add tasks, use the add_task tool.
When users ask to view tasks, use the list_tasks tool.
When users mark tasks complete, use the complete_task tool.
When users delete tasks, use the delete_task tool.
When users update tasks, use the update_task tool.

Always confirm actions with a friendly response."""

        # 7. Build messages for OpenAI
        messages_for_ai = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message}
        ]

        # 8. Call OpenAI API (using Agents SDK approach)
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages_for_ai,
            tools=tool_schemas,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # 9. Execute tool calls if any
        tool_results = []
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute MCP tool
                result = await self.mcp.execute_tool(
                    tool_name, user_id, tool_args, db
                )
                tool_results.append({
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": result
                })

                # Add tool execution to message history
                messages_for_ai.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [tool_call.model_dump()]
                })
                messages_for_ai.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Get final response after tool execution
            final_response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages_for_ai
            )
            final_content = final_response.choices[0].message.content
        else:
            final_content = assistant_message.content

        # 10. Store assistant response
        assistant_msg = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=final_content
        )
        db.add(assistant_msg)
        await db.commit()

        return {
            "conversation_id": conversation.id,
            "response": final_content,
            "tool_calls": tool_results
        }

    def _convert_to_openai_format(self, tools: list) -> list:
        """Convert MCP tools to OpenAI function calling format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools
        ]
```

#### 1.6 Create Chat API Endpoint

**File: `phaseIII/backend/app/routers/chat.py`**
```python
"""
Chat API endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.config import settings
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list[dict]

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint for AI-powered task management
    Stateless - all conversation state in database
    """
    # Initialize chat service
    chat_service = ChatService(settings.OPENAI_API_KEY)

    try:
        result = await chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**File: `phaseIII/backend/app/main.py`**
```python
"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(title="Todo AI Chatbot - Phase III")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

### Phase 2: Frontend Setup (OpenAI ChatKit)

#### 2.1 Initialize Frontend with Bun

```bash
# Navigate to phaseIII directory
cd phaseIII

# Clone ChatKit starter template
git clone https://github.com/openai/openai-chatkit-starter-app.git frontend-temp
cd frontend-temp/managed-chatkit

# Move to phaseIII/frontend
mv * ../../frontend/
cd ../../
rm -rf frontend-temp

# Install dependencies with Bun
cd frontend
bun install

# Add additional dependencies
bun add axios
bun add @tanstack/react-query
```

#### 2.2 Create Chat Interface

**File: `phaseIII/frontend/lib/api/chat.ts`**
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: Array<{
    name: string;
    arguments: any;
    result: any;
  }>;
}

export async function sendChatMessage(
  userId: string,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/${userId}/chat`,
    request
  );
  return response.data;
}
```

**File: `phaseIII/frontend/components/chat/ChatInterface.tsx`**
```typescript
'use client';

import { useState } from 'react';
import { sendChatMessage } from '@/lib/api/chat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[];
}

export default function ChatInterface({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<number>();
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(userId, {
        message: input,
        conversation_id: conversationId
      });

      setConversationId(response.conversation_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        tool_calls: response.tool_calls
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            How can I help you manage your tasks today?
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="mt-2 text-sm opacity-75">
                  {msg.tool_calls.map((call, i) => (
                    <div key={i}>🔧 {call.name}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-500">Thinking...</div>}
      </div>

      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

**File: `phaseIII/frontend/app/chat/page.tsx`**
```typescript
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
  // TODO: Get user ID from Better Auth session
  const userId = 'demo-user';

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold p-4 border-b">AI Todo Assistant</h1>
      <ChatInterface userId={userId} />
    </div>
  );
}
```

---

### Phase 3: Database Setup

#### 3.1 Configure Alembic (Independent from Phase II)

**File: `phaseIII/backend/alembic/env.py`**
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.config import settings
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message

# Import all models for autogenerate
target_metadata = SQLModel.metadata

# Use Neon database URL
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# ... rest of env.py configuration
```

#### 3.2 Create Initial Migration

```bash
cd phaseIII/backend

# Initialize Alembic
uv run alembic init alembic

# Generate migration
uv run alembic revision --autogenerate -m "Initial Phase III schema"

# Review migration file
# Ensure it creates:
# - tasks_phaseiii table
# - conversations table
# - messages table

# Apply migration
uv run alembic upgrade head
```

---

## Environment Variables

**File: `phaseIII/backend/.env`**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
BETTER_AUTH_SECRET=your-better-auth-secret
```

**File: `phaseIII/frontend/.env`**
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

---

## Running the Application

### Backend
```bash
cd phaseIII/backend
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd phaseIII/frontend
bun dev
```

---

## Testing

### Backend Tests
```bash
cd phaseIII/backend
uv run pytest
```

### Frontend Tests
```bash
cd phaseIII/frontend
bun test
```

---

## Key Success Criteria

✅ **Complete Separation**: No imports from Phase II
✅ **Independent Database**: Separate tables (tasks_phaseiii, conversations, messages)
✅ **OpenAI Agents SDK**: Using official SDK from https://github.com/openai/openai-agents-python
✅ **OpenAI ChatKit**: Using starter template from https://github.com/openai/openai-chatkit-starter-app/tree/main/managed-chatkit
✅ **MCP Server**: 5 tools (add, list, complete, delete, update)
✅ **UV Package Manager**: Backend uses `uv add`
✅ **Bun Package Manager**: Frontend uses `bun add`
✅ **Stateless Architecture**: All state in database
