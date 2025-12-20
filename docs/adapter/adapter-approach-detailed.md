# ChatKit Adapter Approach - Detailed Technical Discussion

## ⚠️ IMPORTANT: Unofficial Approach

**This document describes an UNOFFICIAL integration pattern.** This is NOT the official ChatKit integration method recommended by OpenAI.

### Official vs This Approach

| Aspect | Official ChatKit SDK | This Adapter (Unofficial) |
|--------|---------------------|--------------------------|
| **Method** | Use ChatKit Python SDK (`openai-chatkit`) | Custom protocol translation layer |
| **Implementation** | Implement `ChatKitServer` class, override `respond()` | Create custom `/chatkit` endpoint with SSE |
| **Support** | Official OpenAI documentation & support | Community/self-support only |
| **Backend Changes** | Significant refactoring required | Minimal changes (~200 lines) |
| **Features** | Full ChatKit features (widgets, workflows, uploads) | Basic chat only |
| **Time Estimate** | 20-30 hours | 6-8 hours |
| **Best For** | Production applications | Hackathons, POCs, quick demos |

### Why This Approach Exists

The official ChatKit integration requires using the ChatKit Python SDK and implementing the `ChatKitServer` class, which means:
- Rewriting significant portions of your backend
- Replacing your existing agent orchestration
- 20-30 hours of development time

**For hackathons with tight deadlines**, this adapter approach offers:
- ✅ Keep your existing agent_service and MCP tools intact
- ✅ Minimal code changes (~200 lines in one new file)
- ✅ 6-8 hours instead of 20-30 hours
- ✅ Proof of concept for ChatKit.js UI
- ⚠️ Limited to basic chat (no widgets, workflows, or advanced features)
- ⚠️ No official support (debugging on your own)

### Decision: Proceed with Unofficial Approach

**Status**: ✅ **APPROVED for hackathon deadline**

This adapter approach is a **pragmatic compromise** that prioritizes:
1. Meeting the hackathon deadline
2. Preserving working backend code
3. Demonstrating ChatKit.js integration
4. Minimizing risk of breaking existing functionality

**Future Migration Path**: After the hackathon, you can migrate to the official ChatKit Python SDK if needed.

---

## Executive Summary

The adapter approach creates a translation layer between ChatKit.js (frontend) and your existing FastAPI backend. It provides the `/chatkit` endpoint that ChatKit.js expects while preserving all your existing backend code.

**Key Insight**: This is a **facade pattern** - the `/chatkit` endpoint acts as a facade that translates ChatKit's protocol to your existing API format.

**Trade-off**: This is faster to implement but lacks official support and advanced features.

---

## What is the Adapter?

The adapter is a **protocol translator** that:
1. Accepts ChatKit.js requests (ChatKit protocol)
2. Extracts the user's message and context
3. Calls your existing backend endpoints
4. Converts responses back to ChatKit protocol
5. Streams events to ChatKit.js frontend

**Think of it like a language translator**: ChatKit.js speaks "ChatKit language", your backend speaks "FastAPI language", and the adapter translates between them.

---

## Why You Need an Adapter

### The Problem: Protocol Mismatch

**ChatKit.js expects:**
```javascript
// ChatKit.js sends this format to POST /chatkit
{
  "thread": {
    "id": "thread_123"
  },
  "messages": [
    {
      "role": "user",
      "content": "Add task to buy milk"
    }
  ],
  "metadata": {
    "user_id": "user_456"
  }
}
```

**Your backend expects:**
```python
# Your current POST /api/{user_id}/chat expects this
{
  "message": "Add task to buy milk",
  "conversation_id": 123,  # Optional
  "user_id": "user_456"    # From JWT
}
```

**The adapter bridges this gap!**

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js with ChatKit.js)                      │
│                                                         │
│  User types: "Add task to buy milk"                    │
│         ↓                                              │
│  ChatKit.js component formats request                   │
│         ↓                                              │
│  POST /chatkit                                          │
│  {                                                      │
│    "thread": {"id": "thread_123"},                     │
│    "messages": [{"role": "user", "content": "..."}]    │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
                        │
                        │ HTTP POST
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Adapter Layer (NEW CODE - ~200 lines)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ POST /chatkit endpoint                           │ │
│  │  1. Parse ChatKit request                        │ │
│  │  2. Extract: thread_id, user_message            │ │
│  │  3. Validate JWT token                           │ │
│  │  4. Extract user_id from JWT                     │ │
│  └──────────────────────────────────────────────────┘ │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Format Converter                                 │ │
│  │  ChatKit format → Your API format                │ │
│  │  {                                               │ │
│  │    message: "Add task...",                       │ │
│  │    conversation_id: 123,                         │ │
│  │    user_id: "user_456"                           │ │
│  │  }                                               │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Call existing backend
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Existing Backend (NO CHANGES!)                          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ agent_service.process_message()                  │ │
│  │  - OpenAI Agents SDK                             │ │
│  │  - MCP tool discovery                            │ │
│  │  - Natural language processing                   │ │
│  └──────────────────────────────────────────────────┘ │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐ │
│  │ MCP Server (5 tools)                             │ │
│  │  - add_task                                      │ │
│  │  - list_tasks                                    │ │
│  │  - complete_task                                 │ │
│  │  - delete_task                                   │ │
│  │  - update_task                                   │ │
│  └──────────────────────────────────────────────────┘ │
│                        │                                │
│                        ▼                                │
│  Returns: {                                             │
│    "content": "I've added 'Buy milk' to your tasks",   │
│    "tool_calls": [...]                                 │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Response
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Adapter Layer (Response Converter)                      │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Convert to ChatKit SSE format:                   │ │
│  │  event: thread.item.done                         │ │
│  │  data: {                                         │ │
│  │    "item": {                                     │ │
│  │      "role": "assistant",                        │ │
│  │      "content": "I've added 'Buy milk'..."       │ │
│  │    }                                             │ │
│  │  }                                               │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Server-Sent Events (SSE)
                        ▼
┌─────────────────────────────────────────────────────────┐
│ ChatKit.js receives and displays response               │
└─────────────────────────────────────────────────────────┘
```

---

## Compatibility Analysis for This Codebase

### ✅ What's Already Compatible

Your existing backend structure is **well-suited** for this adapter approach:

1. **Agent Service** ✅
   - `agent_service.process_message()` at `phaseIII/backend/app/services/agent_service.py:68-159`
   - OpenAI Agents SDK with MCP tools already implemented
   - Returns structured response with `content` and `tool_calls`
   - **NO CHANGES NEEDED**

2. **MCP Tools** ✅
   - Standalone MCP server at port 8001
   - 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
   - **NO CHANGES NEEDED**

3. **Authentication** ✅
   - Better Auth JWT validation at `phaseIII/backend/app/dependencies/auth.py:13-57`
   - `verify_jwt()` function exists (needs small wrapper)
   - **MINOR WRAPPER NEEDED**

4. **Database Services** ✅
   - conversation_service with create/get methods
   - message_service for storing messages
   - SQLModel + Alembic migrations ready
   - **MINOR ADDITIONS NEEDED**

5. **CORS & FastAPI** ✅
   - Already configured in `main.py:96-103`
   - localhost:3000 allowed
   - **NO CHANGES NEEDED**

### ⚠️ Required Modifications

These 4 items need to be added before the adapter will work:

#### 1. Database Schema - Missing `external_id` Field

**Current State**: `phaseIII/backend/app/models/conversation.py:10-24`
```python
class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Needs**:
```python
external_id: str | None = Field(default=None, index=True)  # Maps to ChatKit thread_id
```

**Action**: Add field + create Alembic migration

---

#### 2. Conversation Service - Missing Method

**Current State**: `conversation_service.py` has `get_conversation()` but not by external_id

**Needs**: Add this method:
```python
async def get_conversation_by_external_id(
    db: AsyncSession,
    external_id: str,
    user_id: str
) -> Conversation | None:
    """Get conversation by ChatKit thread ID."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.external_id == external_id,
            Conversation.user_id == user_id
        )
    )
    return result.scalar_one_or_none()
```

**Action**: Add method to `conversation_service.py`

---

#### 3. Auth Helper - JWT from Raw Header

**Current State**: `auth.py:13-57` has `verify_jwt(credentials: HTTPAuthorizationCredentials)`

**Needs**: Function that accepts raw "Bearer <token>" string:
```python
async def verify_jwt_from_header(auth_header: str) -> str:
    """Extract and validate JWT from Authorization header string."""
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header format")

    token = auth_header.replace("Bearer ", "")
    payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    return user_id
```

**Action**: Add helper function to `auth.py`

---

#### 4. ChatKit Type Definitions

**Option A (Lightweight)**: Define types manually in adapter file
```python
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class AssistantMessageItem(BaseModel):
    id: str
    role: MessageRole
    content: str
    created_at: datetime

# etc...
```

**Option B (Full SDK)**: Install ChatKit types
```bash
uv add openai-chatkit  # Just for types, not full SDK
```

**Action**: Choose approach and implement

---

### Implementation Checklist

Before implementing the adapter, complete these prerequisites:

- [ ] **Database Migration** (~1 hour)
  - Add `external_id` field to Conversation model
  - Create Alembic migration: `alembic revision --autogenerate -m "Add external_id to conversations"`
  - Run migration: `alembic upgrade head`
  - Verify migration succeeded

- [ ] **Service Layer Updates** (~30 minutes)
  - Add `get_conversation_by_external_id()` to conversation_service.py
  - Update `create_conversation()` to accept optional `external_id` parameter
  - Test service methods work correctly

- [ ] **Auth Helper** (~30 minutes)
  - Add `verify_jwt_from_header()` function to auth.py
  - Test JWT extraction and validation
  - Ensure consistent error handling with existing auth

- [ ] **Type Definitions** (~30 minutes)
  - Choose manual types or install package
  - Define required ChatKit types (if manual)
  - Test type validation works

**Total Prerequisites Time**: ~2.5 hours

Once these are complete, the adapter implementation can proceed smoothly.

---

## Detailed Implementation

### Step 0: Complete Prerequisites

**BEFORE starting the adapter implementation, ensure all items in the "Implementation Checklist" above are completed.**

The adapter code assumes these modifications are in place. If you skip them, you'll encounter runtime errors.

---

### Step 1: Install Dependencies

```bash
cd phaseIII/backend
uv add openai-chatkit  # Only for ChatKit types, not full SDK
```

**Why only types?** We're not using the full ChatKitServer - we just need the type definitions for request/response format.

---

### Step 2: Create Adapter Endpoint

Create `phaseIII/backend/app/routers/chatkit_adapter.py`:

```python
"""
ChatKit Protocol Adapter

This module provides a translation layer between ChatKit.js (frontend)
and the existing FastAPI backend. It implements the /chatkit endpoint
that ChatKit.js expects while preserving all existing backend logic.

Architecture:
  ChatKit.js → Adapter (this file) → Existing Backend → MCP Tools

Key Responsibilities:
  1. Parse ChatKit protocol requests
  2. Validate JWT authentication
  3. Convert to internal API format
  4. Call existing agent_service
  5. Convert responses to ChatKit SSE format
  6. Stream events back to frontend
"""

from typing import AsyncGenerator
import json
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

# ChatKit type imports (for request/response structure)
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadStreamEvent,
    MessageRole
)

# Your existing backend imports
from app.database import get_session
from app.services.agent_service import agent_service
from app.services.conversation_service import conversation_service
from app.services.message_service import message_service
from app.dependencies.auth import verify_jwt_from_header

router = APIRouter(prefix="", tags=["chatkit-adapter"])


async def parse_chatkit_request(request: Request) -> dict:
    """
    Parse incoming ChatKit.js request.

    ChatKit.js sends requests in this format:
    {
      "thread": {"id": "thread_123"},
      "messages": [
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Previous response"}
      ],
      "metadata": {...}
    }

    Returns:
      dict with extracted thread_id, user_message, message_history
    """
    body = await request.json()

    # Extract thread ID (ChatKit's conversation identifier)
    thread = body.get("thread", {})
    thread_id = thread.get("id")

    # Extract messages array
    messages = body.get("messages", [])

    # Find the latest user message (the current input)
    user_message = None
    message_history = []

    for msg in reversed(messages):
        if msg.get("role") == "user" and user_message is None:
            # This is the current user input
            user_message = msg.get("content", "")
        else:
            # This is conversation history
            message_history.insert(0, {
                "role": msg.get("role"),
                "content": msg.get("content", "")
            })

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="No user message found in request"
        )

    return {
        "thread_id": thread_id,
        "user_message": user_message,
        "message_history": message_history
    }


async def event_generator(
    db: AsyncSession,
    user_id: str,
    thread_id: str | None,
    user_message: str,
    message_history: list[dict]
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events (SSE) for ChatKit.js.

    This is the core translation function that:
    1. Calls your existing backend
    2. Converts responses to ChatKit SSE format
    3. Yields events that ChatKit.js understands

    ChatKit SSE format:
      event: thread.item.done
      data: {"item": {"role": "assistant", "content": "..."}}
    """
    try:
        # Map thread_id to conversation_id in your database
        conversation_id = None
        if thread_id:
            # Try to find existing conversation by external_id
            conversation = await conversation_service.get_conversation_by_external_id(
                db,
                external_id=thread_id,
                user_id=user_id
            )
            if conversation:
                conversation_id = conversation.id

        # Call your existing agent service
        # NO CHANGES to agent_service needed!
        agent_response = await agent_service.process_message(
            user_message=user_message,
            conversation_history=message_history,
            user_id=user_id
        )

        # Save conversation if it doesn't exist
        if not conversation_id:
            conversation = await conversation_service.create_conversation(
                db,
                user_id=user_id,
                external_id=thread_id  # Link to ChatKit thread ID
            )
            conversation_id = conversation.id

        # Save user message to database
        await message_service.create_user_message(
            db,
            conversation_id=conversation_id,
            user_id=user_id,
            content=user_message
        )

        # Save assistant response to database
        await message_service.create_assistant_message(
            db,
            conversation_id=conversation_id,
            user_id=user_id,
            content=agent_response["content"]
        )

        # Convert to ChatKit event format
        assistant_item = AssistantMessageItem(
            id=f"msg_{conversation_id}_{datetime.utcnow().timestamp()}",
            role=MessageRole.ASSISTANT,
            content=agent_response["content"],
            created_at=datetime.utcnow()
        )

        event = ThreadItemDoneEvent(
            item=assistant_item
        )

        # Yield SSE format that ChatKit.js expects
        # Format: "event: <event_type>\ndata: <json_data>\n\n"
        yield f"event: thread.item.done\n"
        yield f"data: {event.model_dump_json()}\n\n"

    except Exception as e:
        # Error handling - send error event to ChatKit.js
        error_event = {
            "error": {
                "type": "agent_error",
                "message": str(e)
            }
        }
        yield f"event: error\n"
        yield f"data: {json.dumps(error_event)}\n\n"


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """
    ChatKit protocol endpoint.

    This is the ONLY endpoint ChatKit.js will call. It must:
    1. Accept ChatKit protocol requests
    2. Validate authentication
    3. Call existing backend
    4. Return SSE stream

    Authentication:
      ChatKit.js sends JWT in Authorization header.
      We extract and validate it using existing auth system.
    """
    # Extract JWT from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    # Validate JWT and extract user_id
    # Uses your existing Better Auth validation!
    user_id = await verify_jwt_from_header(auth_header)

    # Parse ChatKit request
    parsed = await parse_chatkit_request(request)
    thread_id = parsed["thread_id"]
    user_message = parsed["user_message"]
    message_history = parsed["message_history"]

    # Return SSE stream
    # media_type="text/event-stream" tells ChatKit.js to listen for events
    return StreamingResponse(
        event_generator(
            db=db,
            user_id=user_id,
            thread_id=thread_id,
            user_message=user_message,
            message_history=message_history
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

---

### Step 3: Register Adapter in main.py

```python
# phaseIII/backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, chatkit_adapter  # Add chatkit_adapter
from app.config import settings

app = FastAPI(title="Phase III Task Manager")

# CORS Configuration (CRITICAL for ChatKit.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        settings.frontend_url      # Production URL
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register existing routers
app.include_router(chat.router)

# Register NEW ChatKit adapter
app.include_router(chatkit_adapter.router)

@app.get("/health")
async def health():
    return {"status": "ok", "adapters": ["chatkit"]}
```

---

### Step 4: Add Helper Method to conversation_service.py

```python
# phaseIII/backend/app/services/conversation_service.py

async def get_conversation_by_external_id(
    db: AsyncSession,
    external_id: str,
    user_id: str
) -> Conversation | None:
    """
    Get conversation by ChatKit thread ID.

    This links ChatKit threads to your internal conversations.
    """
    from sqlalchemy import select

    result = await db.execute(
        select(Conversation).where(
            Conversation.external_id == external_id,
            Conversation.user_id == user_id
        )
    )

    return result.scalar_one_or_none()
```

---

### Step 5: Update Conversation Model (Database)

```python
# phaseIII/backend/app/models/conversation.py

from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(primary_key=True)
    user_id: str = Field(index=True)
    external_id: str | None = Field(default=None, index=True)  # NEW: ChatKit thread ID
    created_at: datetime
    updated_at: datetime

    messages: list["Message"] = Relationship(back_populates="conversation")
```

**Create migration**:
```bash
cd phaseIII/backend
alembic revision --autogenerate -m "Add external_id to conversations"
alembic upgrade head
```

---

### Step 6: Frontend Integration

```typescript
// phaseIII/frontend/app/chat/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit-js';
import { useAuth } from '@/lib/auth';

export default function ChatPage() {
  const { session } = useAuth();

  if (!session) {
    return <div>Please login to access chat</div>;
  }

  return (
    <div className="h-screen p-4">
      <ChatKit
        baseURL="http://localhost:8000"  // Your backend URL
        auth={{
          type: "custom",
          getAuthToken: async () => {
            // Return JWT token
            return session.token;
          }
        }}
        onError={(error) => {
          console.error("ChatKit error:", error);
          alert(`Chat error: ${error.message}`);
        }}
        onMessage={(message) => {
          console.log("Message received:", message);
        }}
      />
    </div>
  );
}
```

---

## Request/Response Flow (Step-by-Step)

### User Action: "Add task to buy milk"

**Step 1: User types in ChatKit.js**
```
User input: "Add task to buy milk"
```

**Step 2: ChatKit.js formats request**
```javascript
// ChatKit.js creates this request internally
POST http://localhost:8000/chatkit
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json

Body:
{
  "thread": {
    "id": "thread_abc123"  // ChatKit auto-generates this
  },
  "messages": [
    {
      "role": "user",
      "content": "Add task to buy milk"
    }
  ],
  "metadata": {}
}
```

**Step 3: Adapter receives and parses**
```python
# chatkit_adapter.py: chatkit_endpoint()
# 1. Extract JWT from Authorization header
user_id = await verify_jwt_from_header("Bearer eyJhbGc...")
# Returns: "user_456"

# 2. Parse ChatKit request
parsed = await parse_chatkit_request(request)
# Returns:
# {
#   "thread_id": "thread_abc123",
#   "user_message": "Add task to buy milk",
#   "message_history": []
# }
```

**Step 4: Adapter calls existing backend**
```python
# chatkit_adapter.py: event_generator()
agent_response = await agent_service.process_message(
    user_message="Add task to buy milk",
    conversation_history=[],
    user_id="user_456"
)

# Your existing agent_service processes this:
# 1. Creates OpenAI Agent with MCP tools
# 2. LLM decides to call add_task tool
# 3. MCPServerStreamableHttp calls your MCP server
# 4. MCP tool executes: create task in database
# 5. Returns response
```

**Step 5: MCP tool executes**
```python
# phaseIII/backend/app/mcp/tools.py: add_task()
@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str | None):
    # Create task in database
    task = TaskPhaseIII(
        user_id="user_456",
        title="Buy milk",
        description=None,
        completed=False
    )
    db.add(task)
    await db.commit()

    return {
        "task_id": 5,
        "status": "created",
        "title": "Buy milk"
    }
```

**Step 6: agent_service returns response**
```python
# agent_service.py returns:
{
    "content": "I've added 'Buy milk' to your tasks.",
    "tool_calls": [
        {
            "name": "add_task",
            "arguments": {"user_id": "user_456", "title": "Buy milk"},
            "result": {"task_id": 5, "status": "created"}
        }
    ],
    "finish_reason": "stop"
}
```

**Step 7: Adapter converts to ChatKit format**
```python
# chatkit_adapter.py: event_generator()
assistant_item = AssistantMessageItem(
    id="msg_123_1234567890",
    role=MessageRole.ASSISTANT,
    content="I've added 'Buy milk' to your tasks.",
    created_at=datetime.utcnow()
)

event = ThreadItemDoneEvent(item=assistant_item)

# Yield SSE format
yield f"event: thread.item.done\n"
yield f"data: {event.model_dump_json()}\n\n"
```

**Step 8: ChatKit.js receives SSE event**
```javascript
// ChatKit.js automatically handles this event
// and displays the message in the UI

event: thread.item.done
data: {
  "item": {
    "id": "msg_123_1234567890",
    "role": "assistant",
    "content": "I've added 'Buy milk' to your tasks.",
    "created_at": "2025-01-15T10:30:45.123Z"
  }
}
```

**Step 9: User sees response**
```
ChatKit UI displays:
"I've added 'Buy milk' to your tasks."
```

---

## Common Pitfalls and Solutions

### Pitfall 1: SSE Stream Not Working

**Symptom**: ChatKit.js shows "Connecting..." but never receives response

**Cause**: Incorrect SSE format or headers

**Solution**:
```python
# CORRECT SSE format (note the \n\n at the end!)
yield f"event: thread.item.done\n"
yield f"data: {json_data}\n\n"  # Two newlines!

# WRONG (missing final newline)
yield f"event: thread.item.done\n"
yield f"data: {json_data}\n"  # Only one newline - won't work!

# Ensure proper headers
return StreamingResponse(
    event_generator(...),
    media_type="text/event-stream",  # REQUIRED
    headers={
        "Cache-Control": "no-cache",     # Disable caching
        "Connection": "keep-alive",       # Keep connection open
        "X-Accel-Buffering": "no"        # Disable nginx buffering
    }
)
```

---

### Pitfall 2: CORS Errors

**Symptom**: Browser console shows CORS policy error

**Cause**: Backend not allowing frontend origin

**Solution**:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # MUST match frontend URL exactly
    ],
    allow_credentials=True,       # REQUIRED for JWT in headers
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Test CORS**:
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Authorization,Content-Type" \
     -X OPTIONS \
     http://localhost:8000/chatkit

# Should return Access-Control-Allow-Origin header
```

---

### Pitfall 3: Authentication Fails

**Symptom**: 401 Unauthorized errors

**Cause**: JWT not being passed or validated correctly

**Solution**:
```python
# Ensure ChatKit.js sends JWT
// frontend/app/chat/page.tsx
<ChatKit
  auth={{
    type: "custom",
    getAuthToken: async () => {
      const session = await authClient.getSession();
      if (!session?.token) {
        throw new Error("No auth token available");
      }
      console.log("Sending token:", session.token.substring(0, 20) + "...");
      return session.token;
    }
  }}
/>

# Backend: Extract and validate
# chatkit_adapter.py
auth_header = request.headers.get("Authorization")
if not auth_header:
    raise HTTPException(401, "Missing Authorization header")

if not auth_header.startswith("Bearer "):
    raise HTTPException(401, "Invalid Authorization header format")

token = auth_header.replace("Bearer ", "")
user_id = await verify_jwt_token(token)  # Your existing validation
```

---

### Pitfall 4: Message History Not Loading

**Symptom**: Each message starts fresh conversation

**Cause**: thread_id not being stored or retrieved

**Solution**:
```python
# Ensure thread_id maps to conversation
async def event_generator(..., thread_id: str | None, ...):
    conversation_id = None

    if thread_id:
        # Try to find existing conversation
        conversation = await conversation_service.get_conversation_by_external_id(
            db,
            external_id=thread_id,
            user_id=user_id
        )
        if conversation:
            conversation_id = conversation.id

            # Load message history
            messages = await message_service.get_messages_by_conversation(
                db,
                conversation_id=conversation_id,
                user_id=user_id
            )
            message_history = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]

    # Create new conversation if doesn't exist
    if not conversation_id:
        conversation = await conversation_service.create_conversation(
            db,
            user_id=user_id,
            external_id=thread_id  # CRITICAL: Link to ChatKit thread
        )
```

---

### Pitfall 5: MCP Tools Not Being Called

**Symptom**: Messages work but no tasks are created

**Cause**: User ID not being passed to tools

**Solution**:
```python
# Ensure user_id is in context for agent
agent_response = await agent_service.process_message(
    user_message=user_message,
    conversation_history=message_history,
    user_id=user_id  # CRITICAL: Pass user_id
)

# agent_service.py should inject user_id in prompt
message = f"""Context:
- User ID: {user_id} (IMPORTANT: Use this user_id for ALL tool calls)

User message: {user_message}"""
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_chatkit_adapter.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_header():
    # Generate test JWT
    return "Bearer <test_token>"

def test_chatkit_endpoint_accepts_request(client, auth_header):
    """Test that /chatkit endpoint accepts ChatKit format"""
    response = client.post(
        "/chatkit",
        json={
            "thread": {"id": "test_thread_123"},
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        },
        headers={"Authorization": auth_header}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

def test_chatkit_requires_auth(client):
    """Test that /chatkit requires authentication"""
    response = client.post(
        "/chatkit",
        json={
            "thread": {"id": "test_thread_123"},
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )

    assert response.status_code == 401

def test_chatkit_validates_request_format(client, auth_header):
    """Test that invalid requests are rejected"""
    # Missing messages
    response = client.post(
        "/chatkit",
        json={"thread": {"id": "test_thread_123"}},
        headers={"Authorization": auth_header}
    )

    assert response.status_code == 400
```

### Integration Tests

```python
# tests/integration/test_chatkit_flow.py

async def test_full_chatkit_flow(db_session, test_user):
    """Test complete flow: ChatKit → Adapter → Agent → MCP → Response"""

    # Setup
    client = TestClient(app)
    auth_token = create_test_jwt(test_user.id)

    # Send ChatKit request
    response = client.post(
        "/chatkit",
        json={
            "thread": {"id": "test_thread_001"},
            "messages": [
                {"role": "user", "content": "Add task to test adapter"}
            ]
        },
        headers={"Authorization": f"Bearer {auth_token}"},
        stream=True
    )

    # Verify SSE response
    events = []
    for line in response.iter_lines():
        if line.startswith(b"data:"):
            data = json.loads(line[5:])
            events.append(data)

    # Verify agent response
    assert len(events) > 0
    assert "item" in events[0]
    assert events[0]["item"]["role"] == "assistant"
    assert "test adapter" in events[0]["item"]["content"].lower()

    # Verify task was created in database
    tasks = await db_session.execute(
        select(TaskPhaseIII).where(TaskPhaseIII.user_id == test_user.id)
    )
    task = tasks.scalar_one()
    assert task.title == "Test adapter"
```

### Frontend Tests

```typescript
// tests/chatkit-integration.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatPage from '@/app/chat/page';

describe('ChatKit Integration', () => {
  it('should send message and receive response', async () => {
    // Mock auth
    jest.mock('@/lib/auth', () => ({
      useAuth: () => ({ session: { token: 'test_token' } })
    }));

    render(<ChatPage />);

    // Type message
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'Add task to buy milk');
    await userEvent.keyboard('{Enter}');

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText(/I've added 'Buy milk'/i)).toBeInTheDocument();
    });
  });
});
```

---

## Debugging Checklist

When ChatKit.js isn't working:

- [ ] **Check browser console**: Look for CORS, network, or JavaScript errors
- [ ] **Check backend logs**: FastAPI should log all requests
- [ ] **Verify /chatkit endpoint**: `curl -X POST http://localhost:8000/chatkit` should return 401
- [ ] **Test JWT extraction**: Log `auth_header` in adapter to verify it's received
- [ ] **Test SSE format**: Use curl to verify events are sent correctly:
  ```bash
  curl -N -H "Authorization: Bearer $TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"thread":{"id":"test"},"messages":[{"role":"user","content":"test"}]}' \
       http://localhost:8000/chatkit
  ```
- [ ] **Check conversation persistence**: Query database to verify conversations are created
- [ ] **Test MCP tools separately**: Call MCP tools directly to verify they work
- [ ] **Enable debug logging**: Add `logging.basicConfig(level=logging.DEBUG)` in main.py

---

## Pros and Cons Summary

### Pros ✅

1. **Minimal Code Changes**: ~200 lines, no modifications to existing backend
2. **Risk Mitigation**: Existing agent/MCP logic untouched (lower chance of breaking)
3. **Fast Implementation**: 6-8 hours vs 20-30 hours
4. **Incremental Approach**: Can test adapter without committing to full rebuild
5. **Preservation of Work**: All your agent_service.py and MCP code stays intact

### Cons ❌

1. **Not Official Architecture**: Deviates from ChatKit's recommended patterns
2. **Limited Features**: May not support advanced ChatKit features (widgets, workflows)
3. **Adapter Complexity**: Additional translation layer to maintain
4. **Potential Edge Cases**: Custom protocol translation may have bugs
5. **Debugging Difficulty**: Errors could be in adapter OR existing backend

---

## When to Use Adapter vs Full Rebuild

### Use Adapter If:
- ✅ You need ChatKit.js working ASAP (hackathon deadline!)
- ✅ You want to prove concept before committing
- ✅ Your existing backend is working well
- ✅ You don't need advanced ChatKit features (widgets, workflows)
- ✅ You want to minimize risk

### Use Full Rebuild If:
- ✅ You want official ChatKit architecture
- ✅ You need full ChatKit feature support
- ✅ You have 20-30 hours available
- ✅ You want better long-term maintainability
- ✅ You're comfortable with larger refactor

---

## Conclusion

The adapter approach is a **pragmatic, unofficial solution** that gets ChatKit.js working with minimal changes. It's ideal for:
- Hackathon timelines
- Proof of concept
- Risk mitigation
- Incremental migration (you can rebuild later if needed)

### ⚠️ Important Reminders

1. **This is NOT the official integration method** - You're implementing a custom workaround
2. **Limited features** - Advanced ChatKit features (widgets, workflows, file uploads) may not work
3. **Self-support** - Debugging issues is on you, no official OpenAI support
4. **Migration path exists** - Can switch to official ChatKit Python SDK post-hackathon

### Updated Implementation Timeline

**Prerequisites** (~2.5 hours):
1. Database migration for `external_id` (~1 hour)
2. Service layer additions (~30 minutes)
3. Auth helper function (~30 minutes)
4. Type definitions (~30 minutes)

**Adapter Implementation** (~3.5 hours):
1. Implement adapter endpoint (~2 hours)
2. Test with ChatKit.js frontend (~1.5 hours)

**Testing & Debugging** (~2 hours):
1. Fix CORS/SSE issues
2. Verify conversation persistence
3. Test tool execution flow

**Total: 8 hours** (6-10 hours with buffer)

### Next Steps

**Status**: ✅ **APPROVED - Ready to Proceed**

**Phase 1: Prerequisites** (Complete first)
- [ ] Add `external_id` to Conversation model
- [ ] Create and run Alembic migration
- [ ] Add `get_conversation_by_external_id()` service method
- [ ] Add `verify_jwt_from_header()` auth helper
- [ ] Define ChatKit types (manual or package)

**Phase 2: Adapter Implementation**
- [ ] Create `chatkit_adapter.py` router
- [ ] Implement SSE event streaming
- [ ] Register router in `main.py`

**Phase 3: Testing**
- [ ] Test ChatKit.js integration
- [ ] Verify conversation persistence
- [ ] Debug and fix issues

**Phase 4: Demo!** 🎉

If you encounter issues, refer to the debugging checklist and common pitfalls above.

---

## References

### Official ChatKit Documentation
- [ChatKit.js Official Docs](https://openai.github.io/chatkit-js/)
- [ChatKit API Guide](https://platform.openai.com/docs/guides/chatkit)
- [Advanced ChatKit Integration](https://platform.openai.com/docs/guides/custom-chatkit) - Official SDK approach
- [ChatKit GitHub](https://github.com/openai/chatkit-js)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)

### Note on Official Integration
The official ChatKit integration uses the **ChatKit Python SDK** (`openai-chatkit`), which requires implementing `ChatKitServer` class and overriding the `respond()` method. This document describes an **unofficial adapter pattern** that bypasses the SDK for faster implementation at the cost of limited features and support.

**For production applications**, consider migrating to the official ChatKit Python SDK after your hackathon.
