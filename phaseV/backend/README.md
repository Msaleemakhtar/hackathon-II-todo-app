# Phase III Backend - AI-Powered Task Management with ChatKit

Conversational AI task management system built with **OpenAI ChatKit SDK**, **OpenAI Agents SDK**, **MCP Protocol**, and **Gemini 2.0**.

## Overview

Phase III implements a natural language interface for task management using the official OpenAI ChatKit Python SDK. Users can manage tasks through conversational AI with full conversation persistence and multi-user isolation.

### Key Technologies

- **OpenAI ChatKit SDK** (`openai-chatkit`) - Official ChatKit backend integration
- **OpenAI Agents SDK** for AI orchestration
- **MCP (Model Context Protocol)** for tool discovery and execution
- **LiteLLM** for multi-provider LLM support (OpenAI GPT-3.5 or Gemini 2.0)
- **FastAPI** for the REST API framework
- **PostgreSQL** (Neon Serverless) for data persistence
- **Better Auth** for JWT authentication

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ChatKit SDK Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │         Frontend (Next.js + ChatKit.js)              │      │
│  │         - @openai/chatkit-react                      │      │
│  │         - Better Auth JWT                            │      │
│  └────────────────────┬─────────────────────────────────┘      │
│                       │ POST /chatkit                           │
│                       │ (Bearer JWT Token)                      │
│  ┌────────────────────▼─────────────────────────────────┐      │
│  │         ChatKit SDK (Port 8000)                      │      │
│  │  ┌───────────────────────────────────────────────┐   │      │
│  │  │ extract_user_context() - Auth Middleware      │   │      │
│  │  │ - Validates JWT                              │   │      │
│  │  │ - Extracts user_id                           │   │      │
│  │  └─────────────────┬─────────────────────────────┘   │      │
│  │                    │                                  │      │
│  │  ┌─────────────────▼─────────────────────────────┐   │      │
│  │  │ TaskChatServer (ChatKitServer)               │   │      │
│  │  │ - respond() method                           │   │      │
│  │  │ - OpenAI Agents SDK integration              │   │      │
│  │  │ - MCP tool orchestration                     │   │      │
│  │  └─────────┬──────────────────┬─────────────────┘   │      │
│  │            │                  │                      │      │
│  │  ┌─────────▼────────┐  ┌──────▼──────────────┐      │      │
│  │  │ PostgresStore    │  │  MCP Server         │      │      │
│  │  │ (Store Interface)│  │  (Port 8001)        │      │      │
│  │  │ - save_thread    │  │  - FastMCP          │      │      │
│  │  │ - load_thread    │  │  - 5 Tools          │      │      │
│  │  │ - save_item      │  │  - HTTP Transport   │      │      │
│  │  │ - load_items     │  │                     │      │      │
│  │  └─────────┬────────┘  └─────────────────────┘      │      │
│  │            │                                         │      │
│  │  ┌─────────▼────────────────────────────────┐       │      │
│  │  │         PostgreSQL                       │       │      │
│  │  │         - Conversations                  │       │      │
│  │  │         - Messages                       │       │      │
│  │  │         - Tasks                          │       │      │
│  │  └──────────────────────────────────────────┘       │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. ChatKit SDK Integration
- **TaskChatServer**: Extends `ChatKitServer` from `openai-chatkit`
  - Implements `respond()` method with OpenAI Agents SDK
  - Connects to MCP server for tool execution
  - Streams responses to frontend
- **PostgresStore**: Implements ChatKit `Store` interface
  - Maps ChatKit threads → Conversation table
  - Maps ChatKit items → Message table
  - Provides conversation persistence
- **Auth Middleware**: JWT validation
  - Extracts user_id from Bearer token
  - Injects user context into all requests

#### 2. MCP Server (Port 8001)
- **Framework**: FastMCP (Python SDK)
- **Transport**: Streamable HTTP (stateless)
- **Protocol Endpoint**: `/mcp`
- **Tools**: 5 task management tools
- **Location**: `app/mcp/`

#### 3. Database
- **PostgreSQL**: Neon Serverless Database
- **Tables**:
  - `conversations` - ChatKit threads with external_id mapping
  - `messages` - User and assistant messages
  - `tasks_phaseiii` - Task data with user_id isolation
  - `user`, `session`, `account`, `verification` - Better Auth tables

## MCP Tools

The MCP server provides 5 tools for task management:

1. **add_task** - Create a new task
   - Parameters: `user_id`, `title`, `description` (optional)
   - Returns: Task ID and confirmation

2. **list_tasks** - List tasks with filtering
   - Parameters: `user_id`, `status` (optional: "all", "pending", "completed")
   - Returns: List of tasks

3. **complete_task** - Mark task as completed
   - Parameters: `user_id`, `task_id`
   - Returns: Confirmation message

4. **delete_task** - Delete a task
   - Parameters: `user_id`, `task_id`
   - Returns: Confirmation message

5. **update_task** - Update task details
   - Parameters: `user_id`, `task_id`, `title` (optional), `description` (optional)
   - Returns: Updated task details

## Technology Stack

### Backend
- **Python**: 3.11+
- **Framework**: FastAPI
- **Package Manager**: UV
- **ORM**: SQLModel (SQLAlchemy 2.0)
- **Database**: PostgreSQL (Neon Serverless)
- **Validation**: Pydantic v2

### ChatKit & AI
- **ChatKit SDK**: `openai-chatkit==1.4.1` - Official backend integration
- **AI Framework**: OpenAI Agents SDK (`agents`)
- **LLM Provider**: LiteLLM (multi-provider support)
- **Models**:
  - OpenAI GPT-3.5-turbo (primary)
  - Gemini 2.0 Flash (fallback)
- **MCP Framework**: FastMCP (official Python SDK)
- **MCP Transport**: HTTP (stateless)

### Authentication
- **Better Auth**: JWT-based authentication
- **Session Management**: Database-backed sessions

## Prerequisites

- **Python**: 3.11 or higher
- **UV**: Python package manager ([Install UV](https://docs.astral.sh/uv/))
- **Docker**: For containerized deployment
- **PostgreSQL**: Neon Serverless or local instance
- **API Keys**:
  - OpenAI API key (primary) OR Gemini API key (fallback)
  - Better Auth secret

## Setup

### 1. Clone and Navigate

```bash
cd phaseIII/backend
```

### 2. Install Dependencies

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies (including openai-chatkit)
uv sync
```

### 3. Configure Environment

Create `.env` file in the `backend/` directory:

```bash
# Copy example env file
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# AI Models (at least one required)
OPENAI_API_KEY=sk-proj-...  # Primary (recommended)
GEMINI_API_KEY=your_gemini_api_key_here  # Fallback

# Better Auth
BETTER_AUTH_SECRET=your-32-char-secret-here

# Application
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000

# MCP Server
MCP_SERVER_URL=http://localhost:8001/mcp
```

### 4. Database Setup

```bash
# Run migrations (includes Better Auth tables)
uv run alembic upgrade head
```

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# From phaseIII directory
cd ..
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

This starts all services:
- Backend API (ChatKit SDK): http://localhost:8000
- MCP Server: http://localhost:8001
- Frontend (Next.js): http://localhost:3000
- Redis Cache: http://localhost:6379
- ChatKit endpoint: http://localhost:8000/chatkit

**Docker Compose Services:**
- `backend` - FastAPI + ChatKit SDK (Port 8000)
- `mcp-server` - FastMCP HTTP Server (Port 8001)
- `frontend` - Next.js Application (Port 3000)
- `redis` - Redis Cache (Port 6379)

**Resource Management:**
Each service has configured resource limits for optimal performance. Adjust in docker-compose.yml if needed.

### Option 2: Local Development

Run services separately for development:

#### Terminal 1 - MCP Server
```bash
./scripts/dev-mcp-server.sh
```

#### Terminal 2 - Backend API (with ChatKit SDK)
```bash
./scripts/dev-backend.sh
```

## Testing

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "service": "phaseiii-backend",
#   "version": "0.1.0",
#   "environment": "development"
# }

# MCP server (list tools)
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Test ChatKit Integration

1. **Start all services** (backend + MCP server + frontend)

2. **Create a user account** at `http://localhost:3000/signup`

3. **Login** at `http://localhost:3000/login`

4. **Navigate to chat** at `http://localhost:3000/chat`

5. **Test conversation**:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task #1 as complete"

## API Endpoints

### Health Check
- `GET /health` - Service health status

### ChatKit Endpoint (Primary)
- `POST /chatkit` - ChatKit SDK endpoint
  - Handles all chat interactions
  - Requires JWT Bearer token in Authorization header
  - Streams responses as Server-Sent Events (SSE)
  - Automatically persists conversations and messages

**Authentication**:
```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "thread": {"id": "thread_123"},
    "messages": [
      {"role": "user", "content": "Add task to buy milk"}
    ]
  }'
```

## Development Workflow

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application with ChatKit mounting
│   ├── config.py            # Configuration settings
│   ├── models/              # SQLModel database models
│   │   ├── conversation.py  # Conversation model (with external_id)
│   │   ├── message.py       # Message model
│   │   └── task.py          # Task model
│   ├── services/
│   │   ├── conversation_service.py  # Conversation CRUD
│   │   └── message_service.py       # Message CRUD
│   ├── chatkit/             # ← ChatKit SDK Integration
│   │   ├── __init__.py      # Package exports
│   │   ├── postgres_store.py    # Store interface implementation
│   │   ├── task_server.py       # ChatKitServer subclass
│   │   └── middleware.py        # Auth middleware
│   ├── dependencies/
│   │   └── auth.py          # JWT validation
│   └── mcp/
│       ├── server.py        # FastMCP instance
│       ├── tools.py         # MCP tool implementations
│       └── standalone.py    # MCP server entry point
├── alembic/                 # Database migrations
├── scripts/
│   ├── dev-backend.sh       # Run backend in dev mode
│   └── dev-mcp-server.sh    # Run MCP server in dev mode
├── pyproject.toml           # UV project configuration (with openai-chatkit)
├── Dockerfile               # Backend container
├── Dockerfile.mcp           # MCP server container
└── README.md                # This file
```

### Key ChatKit SDK Files

#### `app/chatkit/postgres_store.py` (252 lines)
Implements ChatKit `Store` interface:
- `save_thread()` - Creates/updates conversations with external_id
- `load_thread()` - Loads conversations by ID
- `save_item()` - Saves user/assistant messages
- `load_items()` - Loads conversation history

#### `app/chatkit/task_server.py` (249 lines)
Extends `ChatKitServer`:
- `respond()` - Processes user messages with OpenAI Agents SDK
- Connects to MCP server for tool execution
- Yields `AssistantMessageItem` events for streaming

#### `app/chatkit/middleware.py` (68 lines)
Authentication middleware:
- `extract_user_context()` - Validates JWT and extracts user_id
- Creates context dict passed to all Store methods

### Adding New MCP Tools

1. Define the tool function in `app/mcp/tools.py`:

```python
from app.mcp.server import mcp

@mcp.tool()
async def my_new_tool(user_id: str, param: str) -> str:
    """Tool description for the AI agent."""
    # Implementation
    return "Result"
```

2. The tool is automatically discovered by the OpenAI Agent
3. Test with integration test suite

### Modifying the AI Agent

Edit `app/chatkit/task_server.py`:

```python
def _get_system_instructions(self) -> str:
    """Customize agent behavior and instructions."""
    return """Your custom instructions here"""
```

## Troubleshooting

### Common Issues

#### 1. ChatKit SDK Import Error

**Error**: `ModuleNotFoundError: No module named 'chatkit'`

**Solutions**:
- Install ChatKit SDK: `uv pip install openai-chatkit`
- Verify installation: `uv pip list | grep chatkit`

#### 2. JWT Authentication Failed (401)

**Error**: `401 Unauthorized - Missing Authorization header`

**Solutions**:
- Ensure JWT token is included: `Authorization: Bearer YOUR_TOKEN`
- Verify Better Auth is configured correctly
- Check token expiration

#### 3. MCP Server Connection Refused

**Error**: `Connection refused to http://localhost:8001/mcp`

**Solutions**:
- Verify MCP server is running: `curl http://localhost:8001/health`
- Check MCP server logs: `docker compose logs mcp-server`
- Restart MCP server: `docker compose restart mcp-server`

#### 4. Database Migration Error

**Error**: `Could not connect to database`

**Solutions**:
- Verify DATABASE_URL is correct in `.env`
- Check database is accessible
- Run migrations: `uv run alembic upgrade head`

#### 5. Model API Quota Exceeded

**Error**: `429 Too Many Requests - Quota exceeded`

**Solutions**:
- OpenAI: Check usage at https://platform.openai.com/usage
- Gemini: Check usage at https://ai.dev/usage
- Switch models: Set `OPENAI_API_KEY` or `GEMINI_API_KEY`

#### 6. Gemini Rate Limiting (Free Tier)

**Error**: `litellm.RateLimitError: Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests`

**Solutions**:
- **Switch to OpenAI**: Set valid `OPENAI_API_KEY` in `.env` and restart
- **Upgrade Gemini**: Move to paid tier for higher quotas
- **Use Gemini 2.5 Pro**: Has higher free tier limits than 2.0 Flash
- **Wait for reset**: Free tier quotas reset daily

**Model Selection Logic** (see `task_server.py:58-71`):
```python
if settings.openai_api_key:    # Prefers OpenAI if available
    model = "gpt-3.5-turbo"
elif settings.gemini_api_key:  # Falls back to Gemini
    model = "gemini/gemini-2.5-pro"
```

To switch models, update `.env` and restart:
```bash
# Use OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
#GEMINI_API_KEY=  # Comment out

# Or use Gemini
#OPENAI_API_KEY=  # Comment out
GEMINI_API_KEY=your-gemini-key-here

# Restart backend
docker compose restart backend
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# MCP server only
docker compose logs -f mcp-server

# Last 50 lines
docker compose logs --tail 50 backend
```

### Container Management

```bash
# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f mcp-server
docker compose logs -f frontend

# Restart service
docker compose restart backend

# Rebuild and restart
docker compose up --build -d backend

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Scale services (if needed)
docker compose up -d --scale backend=2
```

### Docker Image Optimization

All Dockerfiles use multi-stage builds for minimal image size:

**Backend Dockerfile** (`phaseIII/backend/Dockerfile`):
- Builder stage: UV package manager + dependencies
- Runtime stage: Python 3.11-slim with only production dependencies
- Security: Non-root user (appuser)
- Health checks: curl-based
- Size: ~200MB

**MCP Server Dockerfile** (`phaseIII/backend/Dockerfile.mcp`):
- Builder stage: UV package manager + dependencies
- Runtime stage: Python 3.11-slim with MCP-specific dependencies
- Security: Non-root user (mcpuser)
- Health checks: curl-based
- Size: ~200MB

**Frontend Dockerfile** (`phaseIII/frontend/Dockerfile`):
- Dependencies stage: Clean npm ci install
- Builder stage: Next.js build with standalone output
- Runner stage: Node 20-alpine with minimal production files
- Security: Non-root user (nextjs)
- Health checks: Node-based HTTP check
- Size: ~150MB

### Production Deployment

For production deployments, remove the volume mounts in docker-compose.yml:

```yaml
# Remove these sections for production
# volumes:
#   - ./backend/app:/app/app:ro
#   - ./backend/.env:/app/.env:ro
```

Set proper environment variables:
```bash
# Create production .env file
cp .env.example .env.production

# Edit with production values
nano .env.production

# Run with production config
docker compose --env-file .env.production up -d
```

## Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key (primary) | - | One required |
| `GEMINI_API_KEY` | Google Gemini API key (fallback) | - | One required |
| `BETTER_AUTH_SECRET` | JWT secret key (32+ chars) | - | Yes |
| `MCP_SERVER_URL` | MCP server endpoint | `http://localhost:8001/mcp` | Yes |
| `ENVIRONMENT` | Environment name | `development` | No |
| `HOST` | Server bind host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | No |

### MCP Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` | MCP server bind host | `0.0.0.0` |
| `MCP_PORT` | MCP server port | `8001` |

## Performance Considerations

### Response Times
- MCP tool discovery: < 100ms
- Agent processing (simple): 2-5 seconds
- Agent processing (complex): 5-15 seconds
- ChatKit SSE streaming: Real-time

### Rate Limits
- OpenAI GPT-3.5: Based on tier (pay-as-you-go)
- Gemini Free Tier: ~60 requests/minute
- Gemini Paid Tier: Higher limits based on plan

### Scalability
- ChatKit SDK supports horizontal scaling
- Stateless HTTP MCP transport enables load balancing
- PostgreSQL connection pooling configured
- Store interface handles concurrent requests

## Security

### Current Implementation
- JWT authentication via Better Auth
- Environment-based configuration (no hardcoded secrets)
- CORS protection configured
- Input validation with Pydantic
- SQL injection protection via SQLModel/SQLAlchemy
- User isolation via user_id in all operations

### Best Practices
- Rotate API keys regularly
- Use strong BETTER_AUTH_SECRET (32+ characters)
- Enable SSL/TLS in production
- Implement rate limiting per user
- Monitor authentication failures

## Migration from Custom Adapter

If upgrading from the custom adapter approach:

1. **Removed Files**:
   - `app/routers/chatkit_adapter.py` (custom adapter)
   - `app/routers/chat.py` (old chat endpoint)
   - `app/services/agent_service.py` (merged into TaskChatServer)

2. **New Files**:
   - `app/chatkit/postgres_store.py`
   - `app/chatkit/task_server.py`
   - `app/chatkit/middleware.py`

3. **Key Changes**:
   - Endpoint: `/api/{user_id}/chat` → `/chatkit`
   - Architecture: Custom adapter → Official ChatKit SDK
   - Authentication: Path parameter → JWT Bearer token

## Documentation

- **OpenAI ChatKit SDK**: https://pypi.org/project/openai-chatkit/
- **ChatKit React**: https://www.npmjs.com/package/@openai/chatkit-react
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastMCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **LiteLLM**: https://docs.litellm.ai/
- **Better Auth**: https://better-auth.com/

## Contributing

1. Follow the Spec-Driven Development (SDD) workflow
2. All changes must have corresponding specifications
3. Update tests for new features
4. Follow the project constitution at `.specify/memory/constitution.md`

## License

See LICENSE file in project root.

---

**Status**: ✅ ChatKit SDK Migration Complete - Production Ready

**Architecture**: Official OpenAI ChatKit Python SDK + OpenAI Agents SDK + MCP Protocol

**Last Updated**: 2025-12-20
