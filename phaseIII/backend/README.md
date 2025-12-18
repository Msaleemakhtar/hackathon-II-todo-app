# Phase III Backend - AI-Powered Task Management

Conversational AI task management system built with **OpenAI Agents SDK**, **MCP Protocol**, and **Gemini 2.0**.

## Overview

Phase III implements a natural language interface for task management, allowing users to manage their tasks through conversational AI. The system uses:

- **OpenAI Agents SDK** for AI orchestration
- **MCP (Model Context Protocol)** for tool discovery and execution
- **LiteLLM** for multi-provider LLM support
- **Gemini 2.0 Flash** as the language model
- **FastAPI** for the REST API
- **PostgreSQL** (Neon Serverless) for data persistence

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  HTTP/MCP   ┌──────────────────┐             │
│  │              │  Protocol   │   MCP Server     │             │
│  │   Backend    │◄────────────┤   (Port 8001)    │             │
│  │ (Port 8000)  │             │                  │             │
│  │              │             │  - FastMCP       │             │
│  │ OpenAI Agent │             │  - 5 Tools       │             │
│  │ + LiteLLM    │             │  - Stateless     │             │
│  │ + Gemini 2.0 │             │  - HTTP Transport│             │
│  └──────┬───────┘             └─────────┬────────┘             │
│         │                               │                      │
│         │                               │                      │
│  ┌──────▼───────┐                ┌──────▼────────┐             │
│  │              │                │               │             │
│  │    Redis     │                │  PostgreSQL   │             │
│  │  (Port 6379) │                │  (External)   │             │
│  │              │                │               │             │
│  └──────────────┘                └───────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. Backend Service (Port 8000)
- **Framework**: FastAPI
- **AI Integration**: OpenAI Agents SDK + LiteLLM
- **Model**: Gemini 2.0 Flash via Google AI Studio API
- **MCP Client**: MCPServerStreamableHttp (stateless HTTP)
- **Location**: `app/`

#### 2. MCP Server (Port 8001)
- **Framework**: FastMCP (Python SDK)
- **Transport**: Streamable HTTP (stateless)
- **Protocol Endpoint**: `/mcp`
- **Tools**: 5 task management tools
- **Location**: `app/mcp/`

#### 3. Supporting Services
- **Redis**: Caching and session storage (Port 6379)
- **PostgreSQL**: Neon Serverless Database (external)

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

### AI & MCP
- **AI Framework**: OpenAI Agents SDK (`agents`)
- **LLM Provider**: LiteLLM (multi-provider support)
- **Model**: Gemini 2.0 Flash (`gemini/gemini-2.0-flash`)
- **MCP Framework**: FastMCP (official Python SDK)
- **MCP Transport**: HTTP (stateless)

### Authentication
- **Better Auth**: (Future integration for user authentication)

## Prerequisites

- **Python**: 3.11 or higher
- **UV**: Python package manager ([Install UV](https://docs.astral.sh/uv/))
- **Docker**: For containerized deployment
- **PostgreSQL**: Neon Serverless or local instance
- **Gemini API Key**: From [Google AI Studio](https://ai.google.dev/)

## Setup

### 1. Clone and Navigate

```bash
cd phaseIII/backend
```

### 2. Install Dependencies

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
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

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000

# MCP Server
MCP_SERVER_URL=http://localhost:8001/mcp

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 4. Database Setup

```bash
# Run migrations
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
- Backend API: http://localhost:8000
- MCP Server: http://localhost:8001
- Redis: http://localhost:6379

### Option 2: Local Development

Run services separately for development:

#### Terminal 1 - MCP Server
```bash
./scripts/dev-mcp-server.sh
```

#### Terminal 2 - Backend API
```bash
./scripts/dev-backend.sh
```

## Testing

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# MCP server (list tools)
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Run Integration Tests

```bash
# Inside backend container
docker compose exec backend python test_agent_mcp_integration.py

# Or locally with UV
uv run python test_agent_mcp_integration.py
```

### Test Conversational AI

```bash
# Send a message to the AI agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy groceries",
    "user_id": "user_123"
  }'
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Chat Endpoint
- `POST /api/chat` - Send message to AI agent
  ```json
  {
    "message": "Create a task to buy groceries",
    "user_id": "user_123",
    "conversation_history": []
  }
  ```

### Task Management (REST API)
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task details
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Complete task

## Development Workflow

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/              # SQLModel database models
│   ├── routes/              # API route handlers
│   ├── services/
│   │   └── agent_service.py # OpenAI Agent orchestrator
│   └── mcp/
│       ├── server.py        # FastMCP instance
│       ├── tools.py         # MCP tool implementations
│       └── standalone.py    # MCP server entry point
├── alembic/                 # Database migrations
├── scripts/
│   ├── dev-backend.sh       # Run backend in dev mode
│   └── dev-mcp-server.sh    # Run MCP server in dev mode
├── test_agent_mcp_integration.py  # Integration tests
├── pyproject.toml           # UV project configuration
├── Dockerfile               # Backend container
├── Dockerfile.mcp           # MCP server container
└── README.md                # This file
```

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

Edit `app/services/agent_service.py`:

```python
def _get_system_instructions(self) -> str:
    """Customize agent behavior and instructions."""
    return """Your custom instructions here"""
```

## Troubleshooting

### Common Issues

#### 1. Gemini API Quota Exceeded (429 Error)

**Error**: `429 Too Many Requests - Quota exceeded`

**Solutions**:
- Check usage at https://ai.dev/usage
- Wait for free tier quota to reset (daily)
- Upgrade to paid tier at https://ai.google.dev/

#### 2. MCP Server Connection Refused

**Error**: `Connection refused to http://mcp-server:8001/mcp`

**Solutions**:
- Verify MCP server is running: `docker compose ps mcp-server`
- Check MCP server logs: `docker compose logs mcp-server`
- Restart MCP server: `docker compose restart mcp-server`

#### 3. Invalid Host Header (421 Error)

**Error**: `421 Misdirected Request - Invalid Host header`

**Solution**: Already fixed in `app/mcp/server.py` with `TransportSecuritySettings`

#### 4. Database Connection Error

**Error**: `Could not connect to database`

**Solutions**:
- Verify DATABASE_URL is correct in `.env`
- Check database is accessible
- Run migrations: `uv run alembic upgrade head`

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

# Restart service
docker compose restart backend

# Rebuild and restart
docker compose up --build -d backend

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | - | Yes |
| `MCP_SERVER_URL` | MCP server endpoint | `http://localhost:8001/mcp` | Yes |
| `ENVIRONMENT` | Environment name | `development` | No |
| `HOST` | Server bind host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | No |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | No |

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

### Rate Limits
- Gemini Free Tier: ~60 requests/minute
- Gemini Paid Tier: Higher limits based on plan

### Scalability
- Stateless HTTP MCP transport enables horizontal scaling
- Redis for distributed caching
- PostgreSQL connection pooling configured

## Security

### Current Implementation
- Environment-based configuration (no hardcoded secrets)
- CORS protection configured
- Input validation with Pydantic
- SQL injection protection via SQLModel/SQLAlchemy

### Future Enhancements
- Better Auth integration for user authentication
- JWT token validation
- Rate limiting per user
- API key rotation

## Documentation

- **Integration Summary**: `OPENAI_AGENT_MCP_INTEGRATION_SUMMARY.md` - Complete integration details
- **MCP Debug Summary**: `MCP_SERVER_DEBUG_SUMMARY.md` - Troubleshooting guide
- **API Reference**: Coming soon
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastMCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **LiteLLM**: https://docs.litellm.ai/

## Contributing

1. Follow the Spec-Driven Development (SDD) workflow
2. All changes must have corresponding specifications
3. Update tests for new features
4. Follow the project constitution at `.specify/memory/constitution.md`

## License

See LICENSE file in project root.

---

**Status**: ✅ Integration Complete - Production Ready (with valid Gemini API quota)

**Last Updated**: 2025-12-19
