---
name: mcp-expert
description: Expert guidance for Model Context Protocol (MCP) implementation using the official Python SDK. Use when building MCP servers, implementing stateless tools with database-backed state, designing tool schemas, or testing MCP tool invocation. Critical for Phase III implementation requiring 5 task operation tools (add_task, list_tasks, complete_task, delete_task, update_task) that must be stateless and Constitution Principle XI compliant.
---

# MCP Expert

Expert guidance for Model Context Protocol (MCP) implementation with official Python SDK.

## Overview

This skill covers MCP server architecture, stateless tool design, and the 5 required task management tools for Phase III.

**Official SDK**: https://github.com/modelcontextprotocol/python-sdk

## Core MCP Concepts

### What is MCP?

Model Context Protocol (MCP) provides a standardized way for AI agents to interact with applications through well-defined tools.

**Key Principles**:
1. **Stateless Tools** - No in-memory state between requests
2. **Database-Backed** - All state persisted to database
3. **Standardized Schemas** - JSON Schema for tool inputs
4. **Tool Composition** - Agents can chain multiple tools

### MCP vs Direct API Calls

```
Without MCP:
User → AI → Custom parsing → Direct DB calls → Response

With MCP:
User → AI → MCP Tool Selection → Tool Execution → Response
```

**Benefits**:
- Standardized tool interface
- Clear separation of concerns
- Easier testing and debugging
- Tool composition capabilities

## 1. MCP Server Setup

### Installation

```bash
# Phase III backend
cd phaseIII/backend
uv add mcp
```

### Server Initialization

```python
# phaseIII/backend/app/mcp/server.py
from mcp.server import Server
from mcp.server.models import Tool

class MCPServerManager:
    """Manages MCP server and tools"""

    def __init__(self):
        self.server = Server("todo-mcp-server")
        self.tools_impl = MCPTools()  # Tool implementations

    async def list_tools(self) -> list[Tool]:
        """List all available MCP tools"""
        return [
            self._define_add_task(),
            self._define_list_tasks(),
            self._define_complete_task(),
            self._define_delete_task(),
            self._define_update_task()
        ]

    def _define_add_task(self) -> Tool:
        """Define add_task tool schema"""
        return Tool(
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
        )
```

### Server Lifecycle

```python
class MCPServerManager:
    def __init__(self):
        self.server = Server("todo-mcp-server")
        # Server is ready immediately - no start() needed

    async def execute_tool(
        self,
        name: str,
        user_id: str,
        arguments: dict,
        db: AsyncSession
    ) -> dict:
        """Execute a tool by name"""
        # Route to appropriate tool implementation
        if name == "add_task":
            return await self.tools_impl.add_task(user_id, arguments, db)
        elif name == "list_tasks":
            return await self.tools_impl.list_tasks(user_id, arguments, db)
        # ... other tools
        else:
            raise ValueError(f"Unknown tool: {name}")
```

## 2. Stateless Tool Design

### The Stateless Principle

**Critical**: Tools MUST NOT hold state between requests (Constitution Principle XI)

```python
# ❌ WRONG - Holds state in memory
class MCPTools:
    def __init__(self):
        self.user_tasks = {}  # BAD: In-memory state

    async def add_task(self, user_id: str, args: dict):
        if user_id not in self.user_tasks:
            self.user_tasks[user_id] = []
        self.user_tasks[user_id].append(args["title"])

# ✅ CORRECT - Database-backed state
class MCPTools:
    def __init__(self):
        self.task_service = TaskService()  # Stateless service

    async def add_task(self, user_id: str, args: dict, db: AsyncSession):
        # All state in database
        task = await self.task_service.create_task(
            db=db,
            user_id=user_id,
            title=args["title"],
            description=args.get("description", "")
        )
        return {"task_id": task.id, "status": "created", "title": task.title}
```

### Database Session Management

**Pattern**: Pass database session to each tool invocation

```python
async def execute_tool(
    self,
    name: str,
    user_id: str,
    arguments: dict,
    db: AsyncSession  # Database session passed in
) -> dict:
    """Execute tool with database session"""
    return await self.tools_impl.add_task(user_id, arguments, db)
```

### Transaction Handling

```python
async def add_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
    """Tool with transaction handling"""
    try:
        task = Task(
            user_id=user_id,
            title=args["title"],
            description=args.get("description", ""),
            completed=False
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to create task: {str(e)}")
```

## 3. Tool Schema Design

### JSON Schema Structure

MCP tools use JSON Schema for input validation:

```python
inputSchema={
    "type": "object",
    "properties": {
        "field_name": {
            "type": "string|number|boolean|array|object",
            "description": "Clear description for AI"
        }
    },
    "required": ["field1", "field2"]  # Optional fields omitted
}
```

### Parameter Types

```python
# String parameter
"title": {
    "type": "string",
    "description": "Task title (max 200 chars)"
}

# Integer parameter
"task_id": {
    "type": "integer",
    "description": "ID of task to complete"
}

# Enum parameter
"status": {
    "type": "string",
    "enum": ["all", "pending", "completed"],
    "description": "Filter tasks by status"
}

# Optional parameter (not in required array)
"description": {
    "type": "string",
    "description": "Optional task description"
}
```

### Schema Best Practices

1. **Clear descriptions** - Help AI understand when to use each parameter
2. **Type constraints** - Use enums for limited options
3. **Required fields** - Only mark truly required fields
4. **Default values** - Handle in tool implementation, not schema

## 4. Phase III Required Tools

### Tool 1: add_task

**Purpose**: Create a new task

```python
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
)

# Implementation
async def add_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
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
```

### Tool 2: list_tasks

**Purpose**: Retrieve user's tasks with optional filtering

```python
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
)

# Implementation
async def list_tasks(self, user_id: str, args: dict, db: AsyncSession) -> list[dict]:
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
```

### Tool 3: complete_task

**Purpose**: Mark a task as complete

```python
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
)

# Implementation
async def complete_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
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
```

### Tool 4: delete_task

**Purpose**: Remove a task permanently

```python
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
)

# Implementation
async def delete_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
    # Get task first to return title
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
```

### Tool 5: update_task

**Purpose**: Modify task title or description

```python
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
        "required": ["task_id"]  # At least one of title/description should be provided
    }
)

# Implementation
async def update_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
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

## 5. Tool Implementation Structure

### Complete Tool Implementation Example

```python
# phaseIII/backend/app/mcp/tools.py
from app.services.task_service import TaskService

class MCPTools:
    """MCP tool implementations - STATELESS"""

    def __init__(self):
        self.task_service = TaskService()  # Stateless service

    async def add_task(
        self,
        user_id: str,
        args: dict,
        db: AsyncSession
    ) -> dict:
        """
        Create a new task

        Args:
            user_id: Owner user ID
            args: Tool arguments (title, description)
            db: Database session

        Returns:
            {"task_id": int, "status": str, "title": str}

        Raises:
            ValueError: If title is invalid
        """
        # Validate input
        if not args.get("title", "").strip():
            raise ValueError("Title cannot be empty")

        # Create task via service
        task = await self.task_service.create_task(
            db=db,
            user_id=user_id,
            title=args["title"],
            description=args.get("description", "")
        )

        # Return standardized response
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
```

### Error Handling Pattern

```python
async def complete_task(self, user_id: str, args: dict, db: AsyncSession) -> dict:
    """Complete a task with proper error handling"""
    try:
        task = await self.task_service.update_task(
            db=db,
            user_id=user_id,
            task_id=args["task_id"],
            completed=True
        )

        if not task:
            raise ValueError(f"Task {args['task_id']} not found")

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

    except ValueError as e:
        # User-friendly error
        raise ValueError(str(e))

    except Exception as e:
        # Unexpected error
        raise ValueError(f"Failed to complete task: {str(e)}")
```

## 6. User ID Scoping

**Critical**: All tool operations MUST scope to user_id

### Correct Scoping Pattern

```python
async def list_tasks(self, user_id: str, args: dict, db: AsyncSession) -> list[dict]:
    """Always filter by user_id"""
    tasks = await self.task_service.list_tasks(
        db=db,
        user_id=user_id,  # ALWAYS scope to user
        status=args.get("status", "all")
    )
    return [{"id": t.id, "title": t.title, ...} for t in tasks]
```

### Service Layer Enforcement

```python
# phaseIII/backend/app/services/task_service.py
class TaskService:
    async def get_task(
        self,
        db: AsyncSession,
        user_id: str,
        task_id: int
    ) -> Task | None:
        """Get task - ALWAYS check user_id"""
        result = await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # Security: user can only access their tasks
            )
        )
        return result.scalar_one_or_none()
```

## 7. Testing MCP Tools

### Unit Test Pattern

```python
# phaseIII/backend/tests/test_mcp_tools.py
import pytest
from app.mcp.tools import MCPTools
from app.models.task import Task

@pytest.mark.asyncio
async def test_add_task(db_session):
    """Test add_task tool"""
    tools = MCPTools()

    result = await tools.add_task(
        user_id="test-user",
        args={"title": "Buy groceries", "description": "Milk, eggs"},
        db=db_session
    )

    assert result["status"] == "created"
    assert result["title"] == "Buy groceries"
    assert "task_id" in result

    # Verify in database
    task = await db_session.get(Task, result["task_id"])
    assert task.user_id == "test-user"
    assert task.title == "Buy groceries"
```

### Test User Isolation

```python
@pytest.mark.asyncio
async def test_user_isolation(db_session):
    """Test users can't access each other's tasks"""
    tools = MCPTools()

    # User A creates task
    result_a = await tools.add_task(
        user_id="user-a",
        args={"title": "User A task"},
        db=db_session
    )

    # User B tries to complete User A's task
    with pytest.raises(ValueError, match="not found"):
        await tools.complete_task(
            user_id="user-b",
            args={"task_id": result_a["task_id"]},
            db=db_session
        )
```

### Integration Test Pattern

```python
@pytest.mark.asyncio
async def test_complete_workflow(db_session):
    """Test complete task lifecycle"""
    tools = MCPTools()
    user_id = "test-user"

    # 1. Add task
    add_result = await tools.add_task(
        user_id=user_id,
        args={"title": "Test task"},
        db=db_session
    )
    task_id = add_result["task_id"]

    # 2. List tasks (should include new task)
    list_result = await tools.list_tasks(
        user_id=user_id,
        args={"status": "pending"},
        db=db_session
    )
    assert any(t["id"] == task_id for t in list_result)

    # 3. Complete task
    complete_result = await tools.complete_task(
        user_id=user_id,
        args={"task_id": task_id},
        db=db_session
    )
    assert complete_result["status"] == "completed"

    # 4. Verify in completed list
    completed_result = await tools.list_tasks(
        user_id=user_id,
        args={"status": "completed"},
        db=db_session
    )
    assert any(t["id"] == task_id for t in completed_result)
```

## 8. Common Pitfalls

### Pitfall 1: Storing State in Tool Class

```python
# ❌ WRONG - State persists between requests
class MCPTools:
    def __init__(self):
        self.cache = {}  # BAD: Breaks stateless requirement

# ✅ CORRECT - Only configuration, no state
class MCPTools:
    def __init__(self):
        self.task_service = TaskService()  # Stateless service only
```

### Pitfall 2: Not Scoping to User ID

```python
# ❌ WRONG - Can access any user's task
async def get_task(self, task_id: int, db: AsyncSession):
    return await db.get(Task, task_id)

# ✅ CORRECT - Always scope to user
async def get_task(self, user_id: str, task_id: int, db: AsyncSession):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

### Pitfall 3: Missing Error Handling

```python
# ❌ WRONG - Unhandled exceptions
async def delete_task(self, user_id: str, args: dict, db: AsyncSession):
    task = await self.get_task(user_id, args["task_id"], db)
    await db.delete(task)  # Crashes if task is None

# ✅ CORRECT - Explicit error handling
async def delete_task(self, user_id: str, args: dict, db: AsyncSession):
    task = await self.get_task(user_id, args["task_id"], db)
    if not task:
        raise ValueError(f"Task {args['task_id']} not found")
    await db.delete(task)
    await db.commit()
```

## 9. Integration with OpenAI Agents

MCP tools are invoked by OpenAI agents through function calling:

```python
# In ChatService
async def process_message(self, ...):
    # Get MCP tools
    mcp_tools = await self.mcp.list_tools()

    # Convert to OpenAI format
    tool_schemas = self._convert_to_openai_format(mcp_tools)

    # OpenAI agent invokes tools
    response = await self.client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tool_schemas,
        tool_choice="auto"
    )

    # Execute MCP tools based on agent's decision
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            result = await self.mcp.execute_tool(
                name=tool_call.function.name,
                user_id=user_id,
                arguments=json.loads(tool_call.function.arguments),
                db=db
            )
```

## Constitution Compliance

**Principle XI Requirements**:
- ✅ 5 tools implemented (add, list, complete, delete, update)
- ✅ All tools stateless (no in-memory state)
- ✅ All state in database (tasks_phaseiii table)
- ✅ Proper user ID scoping
- ✅ Graceful error handling

## Key Success Metrics

✅ All 5 MCP tools implemented with correct schemas
✅ Tools pass user isolation tests
✅ No state held between requests (stateless verified)
✅ All operations correctly scoped to user_id
✅ Tool errors are gracefully handled
✅ Integration with OpenAI Agents SDK works correctly
