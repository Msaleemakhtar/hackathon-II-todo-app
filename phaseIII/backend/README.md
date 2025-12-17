# Phase III MCP Server Backend

AI-powered todo chatbot backend implementing the Model Context Protocol (MCP) using **FastMCP with stateless HTTP transport** and 5 stateless tools for task management.

## 🎯 Features

### AI Chat Service ✅
- **Conversational AI**: Natural language task management via chat interface
- **OpenAI Agents SDK**: Integrated agent orchestration framework
- **Gemini AI**: Powered by Google's Gemini 1.5 Flash via LiteLLM
- **MCP Tool Integration**: AI automatically invokes MCP tools based on user intent
- **Multi-turn Conversations**: Stateful conversation tracking with database persistence
- **Intelligent Routing**: Context-aware tool selection and parameter extraction

### MCP Tools (All Implemented ✅)
- **add_task**: Create new tasks with title and optional description
- **list_tasks**: Retrieve tasks with status filtering (all/pending/completed)
- **complete_task**: Mark tasks as complete (idempotent)
- **delete_task**: Remove tasks permanently
- **update_task**: Modify task title and/or description

### Core Capabilities
- ✅ **FastMCP with HTTP Transport**: Stateless HTTP server using FastMCP framework
- ✅ **Stateless Architecture**: Database-backed state, horizontally scalable
- ✅ **Multi-User Isolation**: JWT-based user_id scoping on all operations
- ✅ **Async Operations**: FastAPI + SQLModel with asyncpg driver
- ✅ **Comprehensive Validation**: Input validation with standardized error responses
- ✅ **Error Handling**: Global error handler with consistent format `{detail, code, field?}`
- ✅ **Logging**: Configurable logging with request/response tracking
- ✅ **Type Safety**: Modern Python type hints with mypy support

## 📋 Prerequisites

- **Python**: 3.11-3.13 (3.13 recommended, 3.14 has SQLite compatibility issues)
- **UV Package Manager**: Latest version
- **PostgreSQL**: Neon Serverless or any PostgreSQL 14+
- **Better Auth Secret**: For JWT token validation
- **Gemini API Key**: For AI chat service (Google AI Studio)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd phaseIII/backend

# Install all dependencies with UV
uv sync
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DATABASE_URL: PostgreSQL connection string
# - BETTER_AUTH_SECRET: Better Auth secret key
# - GEMINI_API_KEY: Google Gemini API key
```

Example `.env`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
DB_POOL_MIN=5
DB_POOL_MAX=10

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# AI Service
GEMINI_API_KEY=your-gemini-api-key-here

# Server Configuration
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### 3. Run Database Migrations

```bash
# Apply all migrations to create database schema
uv run alembic upgrade head

# Verify migration status
uv run alembic current
```

This creates 3 tables:
- `tasks_phaseiii` - User tasks with indexes
- `conversations` - Chat sessions
- `messages` - Conversation messages with FK constraints

### 4. Start the Server

The server integrates FastAPI with MCP tools and AI chat service:

```bash
# Start the integrated server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start on http://0.0.0.0:8000
```

**What happens when you start the server:**
```
✓ FastMCP Server initialized: phaseiii-task-manager (stateless HTTP)
✓ Started server process
✓ Application startup complete
✓ Starting Phase III Backend...
✓ FastMCP tools registered
✓ Agent service initialized with Gemini via LiteLLM and OpenAI Agents SDK
```

The server provides:
- **REST API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **MCP Endpoint**: http://localhost:8000/mcp
- **Chat Endpoint**: http://localhost:8000/api/chat
- **MCP Tools**: 5 stateless task management tools

## 🧪 Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_models.py -v

# Run with detailed output
uv run pytest -vv
```

### Code Quality

```bash
# Type checking with mypy
uv run mypy app/ --ignore-missing-imports

# Linting with ruff
uv run ruff check app/ tests/

# Auto-fix linting issues
uv run ruff check app/ --fix

# Format code
uv run ruff format app/ tests/
```

## 📚 API Documentation

### Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "service": "todo-mcp-server",
  "version": "0.1.0",
  "mcp_tools_registered": 5
}
```

### MCP Tools

All tools follow the MCP protocol and are accessed via the MCP server.

#### add_task
Create a new task for the authenticated user.

**Input**:
```json
{
  "user_id": "ba_user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Output**:
```json
{
  "task_id": 42,
  "status": "created",
  "title": "Buy groceries"
}
```

#### list_tasks
List tasks with optional status filtering.

**Input**:
```json
{
  "user_id": "ba_user_abc123",
  "status": "pending"
}
```

**Output**:
```json
{
  "tasks": [...],
  "total": 3,
  "status": "pending"
}
```

See [contracts/](../../specs/sphaseIII/001-mcp-server-setup/contracts/) for complete API specifications.

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | FastAPI 0.124+ |
| AI Framework | OpenAI Agents SDK 0.6+ |
| AI Model | Google Gemini 1.5 Flash (via LiteLLM) |
| MCP Framework | **FastMCP (stateless HTTP)** |
| MCP SDK | Official MCP SDK 1.24+ |
| ORM | SQLModel 0.0.27 |
| Database Driver | asyncpg 0.31+ |
| Migration Tool | Alembic 1.17+ |
| Auth Validation | python-jose |
| Package Manager | UV |
| Testing | pytest + pytest-asyncio |
| Code Quality | ruff + mypy |

### Directory Structure

```
phaseIII/backend/
├── app/
│   ├── main.py              # FastAPI app + global handlers
│   ├── config.py            # Settings management
│   ├── database.py          # Async DB session
│   ├── models/              # SQLModel entities
│   │   ├── task.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── chat.py          # Chat request/response schemas
│   │   └── errors.py        # Error response schemas
│   ├── routers/             # API routes
│   │   └── chat.py          # Chat endpoints
│   ├── services/            # Business logic
│   │   ├── agent_service.py      # OpenAI Agents SDK orchestrator
│   │   ├── conversation_service.py
│   │   ├── message_service.py
│   │   └── task_service.py
│   ├── dependencies/        # FastAPI dependencies
│   │   └── auth.py          # Authentication dependencies
│   ├── mcp/                 # MCP server
│   │   ├── server.py        # FastMCP server manager
│   │   └── tools.py         # MCP tool implementations (5 tools)
│   └── utils/
│       └── errors.py        # Error handling utilities
├── tests/                   # Test suite
├── alembic/                 # Database migrations
└── pyproject.toml           # Dependencies & config
```

### AI Service Architecture

The AI chat service uses a **stateless agent** pattern with database-backed conversation history:

**Flow:**
```
User Message → Chat API → Agent Service → OpenAI Agents SDK
                               ↓
                        Gemini (via LiteLLM)
                               ↓
                        Intent Recognition
                               ↓
                        MCP Tool Selection
                               ↓
                    MCP Server HTTP Request
                               ↓
                    Tool Execution (Stateless)
                               ↓
                        Database Query
                               ↓
                    Result → AI Response → User
```

**Key Components:**
- **AgentService** (`app/services/agent_service.py`): Orchestrates AI agent with MCP tools
- **LitellmModel**: Wraps Gemini API in OpenAI-compatible interface
- **OpenAI Agents SDK Runner**: Handles multi-turn tool execution
- **MCPServerStreamableHttp**: Connects to MCP tools via HTTP

**Stateless Design:**
- No in-memory session state (SDK's SQLite memory not used for persistence)
- Conversation history stored in PostgreSQL
- Each request rebuilds context from database
- Horizontally scalable architecture

### FastMCP Configuration

This project uses **FastMCP** with stateless HTTP transport:

**Key Configuration:**
- **Framework**: FastMCP from `mcp.server.fastmcp`
- **Transport**: StreamableHTTP (stateless)
- **Port**: 8000 (default)
- **MCP Endpoint**: `/mcp`

**Why FastMCP + Stateless HTTP?**
- ✅ **HTTP-based**: Easy integration with web services and testing tools
- ✅ **Stateless**: Each request is independent, improving scalability
- ✅ **Production-ready**: Better suited for production deployments than stdio
- ✅ **RESTful**: Compatible with standard HTTP clients
- ✅ **Framework benefits**: Simplified tool registration with decorators

**Tool Registration:**
```python
@mcp.tool()
async def my_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """Tool implementation."""
    return {"status": "success"}
```

### Database Schema

**tasks_phaseiii**:
- Primary Key: `id`
- Indexes: `user_id`, `created_at`
- Fields: id, user_id, title, description, completed, created_at, updated_at

**conversations**:
- Primary Key: `id`
- Index: `user_id`
- Fields: id, user_id, created_at, updated_at

**messages**:
- Primary Key: `id`
- Indexes: `conversation_id`, `user_id`
- Foreign Key: `conversation_id` → `conversations.id` (CASCADE)
- Fields: id, conversation_id, user_id, role, content, created_at

## 🔒 Security

### Multi-User Isolation

All operations enforce user isolation through JWT validation:

1. **JWT Extraction**: Extract user_id from Better Auth JWT token
2. **Query Scoping**: All database queries include `WHERE user_id = {authenticated_user_id}`
3. **Ownership Validation**: Update/delete operations verify ownership before modification

### Error Handling

Standardized error format:
```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "field": "field_name"  // optional
}
```

Error codes:
- `INVALID_TITLE`: Title validation failed
- `DESCRIPTION_TOO_LONG`: Description exceeds 1000 chars
- `INVALID_USER_ID`: Missing or invalid user ID
- `TASK_NOT_FOUND`: Task doesn't exist or wrong user
- `INVALID_PARAMETER`: Invalid parameter value
- `DATABASE_ERROR`: Database connection failed

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `BETTER_AUTH_SECRET` | Better Auth secret key | - | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |
| `DB_POOL_MIN` | Min database connections | 5 | ❌ |
| `DB_POOL_MAX` | Max database connections | 10 | ❌ |
| `JWT_CACHE_SIZE` | JWT cache size | 1000 | ❌ |
| `JWT_CACHE_TTL` | JWT cache TTL (seconds) | 300 | ❌ |
| `DEBUG` | Enable debug mode | false | ❌ |
| `LOG_LEVEL` | Logging level | INFO | ❌ |
| `HOST` | Server host | 0.0.0.0 | ❌ |
| `PORT` | Server port | 8000 | ❌ |

### Database Configuration

Connection pooling is automatically managed:
- Minimum pool size: `DB_POOL_MIN` (default: 5)
- Maximum pool size: `DB_POOL_MAX` (default: 10)
- Pool overflow: `MAX - MIN` connections
- Pre-ping enabled: Verifies connections before use

## 🔄 Development Workflow

### Create New Migration

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "description"

# Create empty migration
uv run alembic revision -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Add New MCP Tool

1. Create tool file: `app/mcp/tools/my_tool.py`
2. Implement with `@mcp_server_manager.server.tool()` decorator (FastMCP)
3. Add validation using `app/mcp/validators.py`
4. Register tool in `app/mcp/tools/__init__.py`
5. Create JSON contract in `contracts/my_tool.json`
6. Write tests in `tests/test_mcp_tools/test_my_tool.py`

**Example tool implementation:**
```python
from app.mcp.server import mcp_server_manager

@mcp_server_manager.server.tool()
async def my_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """Tool description."""
    # Implementation here
    return {"status": "success"}

# Register tool
mcp_server_manager.register_tool(
    name="my_tool",
    description="Tool description",
    handler=my_tool
)
```

## 📦 Phase Separation

This backend maintains **complete independence** from Phase II:

✅ **Separate Tables**: Uses `tasks_phaseiii`, not `tasks`
✅ **Independent Migrations**: Separate Alembic history
✅ **Zero Imports**: No imports from `phaseII/` directory
✅ **Isolated Directory**: Located in `phaseIII/backend/`

Verification:
```bash
# Verify no Phase II imports
grep -r "from phaseII" app/ || echo "✅ Clean"
grep -r "import phaseII" app/ || echo "✅ Clean"
```

## 🐛 Troubleshooting

### Python Version Issues (SQLite Compatibility)

If you encounter `ModuleNotFoundError: No module named '_sqlite3'`:

```bash
# Check current Python version
python3 --version

# The OpenAI Agents SDK requires SQLite support
# Python 3.14 may have compatibility issues

# Solution 1: Switch to Python 3.13 (Recommended)
uv python pin 3.13
uv sync

# Solution 2: Install SQLite development libraries
sudo apt-get update && sudo apt-get install -y libsqlite3-dev

# Verify SQLite support
python3 -c "import sqlite3; print('SQLite3 OK')"
```

### Database Connection Issues

```bash
# Test database connection
uv run python -c "from app.database import engine; import asyncio; asyncio.run(engine.dispose())"

# Check migration status
uv run alembic current

# Verify tables exist
# Connect to PostgreSQL and run:
SELECT tablename FROM pg_tables WHERE schemaname='public';
```

### Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Server Startup Issues

```bash
# Check if server is running
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","service":"phaseiii-task-manager"}

# View server logs
# The server outputs detailed startup logs including:
# - FastMCP server initialization
# - Tool registration
# - Agent service initialization
# - Database connection status

# Test MCP endpoint
curl http://localhost:8000/mcp

# Test chat endpoint (requires authentication)
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "List my tasks"}'
```

## 📄 License

Part of the Phase III Todo App project.

## 🤝 Contributing

This is the MCP server implementation for Phase III. See the main project documentation for contribution guidelines.

---

**Status**: ✅ Production Ready - All core features implemented and tested
