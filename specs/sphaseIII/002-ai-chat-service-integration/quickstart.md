# Quickstart Guide: AI-Powered Conversational Task Management

**Feature**: Phase III AI Chat Service
**Branch**: `002-ai-chat-service-integration`
**Date**: 2025-12-17

This guide provides step-by-step instructions for setting up the development environment and implementing the conversational task management feature.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Setup (FastAPI + MCP)](#backend-setup-fastapi--mcp)
4. [Frontend Setup (OpenAI ChatKit)](#frontend-setup-openai-chatkit)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Development Workflow](#development-workflow)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Python 3.11+**: Backend runtime
- **UV**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Bun**: JavaScript runtime and package manager (`curl -fsSL https://bun.sh/install | bash`)
- **PostgreSQL**: Database (use Neon serverless or local instance)
- **Git**: Version control
- **OpenAI Platform Account**: For ChatKit domain key
- **Google Cloud Account**: For Gemini API key

### API Keys Required

| Service | Key Name | Purpose | Where to Get |
|---------|----------|---------|--------------|
| Gemini | `GEMINI_API_KEY` | AI natural language processing | https://makersuite.google.com/app/apikey |
| Neon | `DATABASE_URL` | PostgreSQL database | https://neon.tech (create project) |
| Better Auth | `BETTER_AUTH_SECRET` | Authentication | Generate 256-bit secret |
| OpenAI | `CHATKIT_DOMAIN_KEY` | ChatKit UI integration | https://platform.openai.com/chatkit |

---

## Environment Setup

### 1. Clone Repository and Checkout Branch

```bash
cd /path/to/hackathon-II-todo-app
git checkout 002-ai-chat-service-integration
```

### 2. Create Phase III Directory Structure

```bash
mkdir -p phaseIII/backend/app/{models,services,routers,mcp,schemas}
mkdir -p phaseIII/backend/alembic/versions
mkdir -p phaseIII/backend/tests
mkdir -p phaseIII/frontend/{app,components,lib}
```

### 3. Set Up Environment Variables

**Backend** (`phaseIII/backend/.env`):
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Better Auth
BETTER_AUTH_SECRET=your_256_bit_secret_here
BETTER_AUTH_URL=http://localhost:3000

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Frontend** (`phaseIII/frontend/.env.local`):
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your_256_bit_secret_here
BETTER_AUTH_URL=http://localhost:3000

# OpenAI ChatKit
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your_chatkit_domain_key
```

---

## Backend Setup (FastAPI + MCP)

### 1. Initialize UV Project

```bash
cd phaseIII/backend

# Create pyproject.toml
cat > pyproject.toml <<EOF
[project]
name = "phaseiii-backend"
version = "0.1.0"
description = "Phase III AI Chat Service Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "alembic>=1.13.0",
    "asyncpg>=0.29.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "google-generativeai>=0.3.0",
    "openai>=1.12.0",
    "mcp>=0.1.0",
    "slowapi>=0.1.9",
    "redis>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.26.0",
    "ruff>=0.1.9",
]
EOF
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev
uv pip install -e ".[dev]"
```

### 3. Create Configuration Module

**File**: `phaseIII/backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # Gemini
    gemini_api_key: str

    # Better Auth
    better_auth_secret: str
    better_auth_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. Set Up Database Connection

**File**: `phaseIII/backend/app/database.py`

```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    future=True
)

# Create async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    """Dependency for getting database session."""
    async with async_session() as session:
        yield session
```

### 5. Initialize Alembic

```bash
cd phaseIII/backend
uv run alembic init alembic
```

Edit `alembic/env.py` to use async engine and import models:

```python
from app.config import settings
from app.models import *  # Import all models
from sqlmodel import SQLModel

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = SQLModel.metadata
```

### 6. Create Initial Migration

```bash
# Generate migration from models
uv run alembic revision --autogenerate -m "Initial schema: tasks_phaseiii, conversations, messages"

# Apply migration
uv run alembic upgrade head
```

---

## Frontend Setup (OpenAI ChatKit)

### 1. Initialize Bun Project

```bash
cd phaseIII/frontend

# Create package.json
cat > package.json <<EOF
{
  "name": "phaseiii-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "bun test"
  }
}
EOF
```

### 2. Install Dependencies

```bash
# Install Next.js and dependencies
bun add next@latest react@latest react-dom@latest
bun add better-auth axios zod
bun add -D @types/react @types/node typescript
```

### 3. Clone ChatKit Starter Template

```bash
# Clone Managed ChatKit template
git clone https://github.com/openai/openai-chatkit-starter-app.git /tmp/chatkit-starter
cp -r /tmp/chatkit-starter/managed-chatkit/* phaseIII/frontend/
rm -rf /tmp/chatkit-starter
```

### 4. Configure Better Auth

**File**: `phaseIII/frontend/lib/auth.ts`

```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [],
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

### 5. Create API Client

**File**: `phaseIII/frontend/lib/api/chat.ts`

```typescript
import axios from "axios";
import { authClient } from "@/lib/auth";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

// Attach JWT token to requests
apiClient.interceptors.request.use(async (config) => {
  const session = await authClient.getSession();
  if (session?.user?.id) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

export interface ChatMessage {
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
  message: ChatMessage
): Promise<ChatResponse> {
  const response = await apiClient.post(`/api/${userId}/chat`, message);
  return response.data;
}
```

---

## Database Setup

### 1. Connect to Neon Database

```bash
# Set DATABASE_URL in .env
# Then apply migrations
cd phaseIII/backend
uv run alembic upgrade head
```

### 2. Verify Tables Created

```sql
-- Connect to Neon via psql or dashboard
\dt

-- Expected tables:
-- tasks_phaseiii
-- conversations
-- messages
-- alembic_version
```

### 3. Create Indexes (if not in migration)

```sql
CREATE INDEX idx_tasks_phaseiii_user_id ON tasks_phaseiii(user_id);
CREATE INDEX idx_tasks_phaseiii_user_completed ON tasks_phaseiii(user_id, completed);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

---

## Running the Application

### Start Backend (Terminal 1)

```bash
cd phaseIII/backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Start Frontend (Terminal 2)

```bash
cd phaseIII/frontend
bun run dev
```

Expected output:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in 1.2s
```

### Verify Services

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

---

## Testing

### Backend Tests

```bash
cd phaseIII/backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_mcp_tools.py

# Run specific test
uv run pytest tests/test_mcp_tools.py::test_add_task
```

### Frontend Tests

```bash
cd phaseIII/frontend

# Run all tests
bun test

# Run with watch mode
bun test --watch

# Run specific test file
bun test components/chat/ChatInterface.test.tsx
```

### Integration Tests

```bash
# Start both services, then run E2E tests
cd phaseIII/backend
uv run pytest tests/integration/test_chat_flow.py
```

---

## Development Workflow

### 1. Create New Model

```bash
# 1. Define model in phaseIII/backend/app/models/<entity>.py
# 2. Generate migration
cd phaseIII/backend
uv run alembic revision --autogenerate -m "Add <entity> model"

# 3. Review migration file
# 4. Apply migration
uv run alembic upgrade head
```

### 2. Create New MCP Tool

```python
# File: phaseIII/backend/app/mcp/tools.py

@mcp_server.tool()
async def new_tool(user_id: str, param: str) -> dict:
    """Tool description for AI agent."""
    # Implementation
    pass
```

### 3. Add New API Endpoint

```python
# File: phaseIII/backend/app/routers/<resource>.py

@router.post("/api/{user_id}/<resource>")
async def create_resource(
    user_id: str,
    data: Schema,
    db: AsyncSession = Depends(get_session),
    auth_user_id: str = Depends(verify_jwt)
):
    # Validate user_id matches auth_user_id
    if user_id != auth_user_id:
        raise HTTPException(403, "User ID mismatch")

    # Implementation
    pass
```

### 4. Update Frontend Component

```typescript
// File: phaseIII/frontend/components/chat/<Component>.tsx

export function NewComponent() {
  const { user } = useSession();

  // Implementation
}
```

### 5. Lint and Format

```bash
# Backend
cd phaseIII/backend
uv run ruff check .
uv run ruff format .

# Frontend
cd phaseIII/frontend
bun run lint
```

---

## Troubleshooting

### Backend Issues

**Issue**: Database connection error
```
Solution:
- Verify DATABASE_URL in .env
- Check Neon database is active
- Test connection: uv run python -c "from app.database import engine; print('OK')"
```

**Issue**: Gemini API key invalid
```
Solution:
- Verify GEMINI_API_KEY in .env
- Check API key at https://makersuite.google.com/app/apikey
- Test: curl https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY
```

**Issue**: MCP tools not found
```
Solution:
- Ensure tools registered in app/mcp/server.py
- Check MCP server initialization in app/main.py
- Verify tools imported correctly
```

### Frontend Issues

**Issue**: ChatKit not loading
```
Solution:
- Verify NEXT_PUBLIC_CHATKIT_DOMAIN_KEY in .env.local
- Check domain allowlist in OpenAI platform settings
- Restart Next.js dev server
```

**Issue**: JWT token not attached to requests
```
Solution:
- Verify Better Auth session exists: console.log(await authClient.getSession())
- Check axios interceptor in lib/api/chat.ts
- Ensure user is authenticated
```

**Issue**: CORS errors
```
Solution:
- Verify CORS_ORIGINS in backend .env includes http://localhost:3000
- Check FastAPI CORS middleware configuration
- Clear browser cache
```

### Common Errors

**"User ID mismatch" (403)**
```
Cause: Path parameter user_id doesn't match JWT user_id
Solution: Ensure frontend uses session.user.id for API URLs
```

**"Conversation not found" (404)**
```
Cause: conversation_id doesn't exist or belongs to another user
Solution: Verify conversation_id before sending, or omit to create new conversation
```

**"Rate limit exceeded" (429)**
```
Cause: More than 10 requests per minute
Solution: Implement request throttling in frontend, show user-friendly message
```

**"AI service unavailable" (503)**
```
Cause: Gemini API timeout or error
Solution: Retry after delay, check Gemini API status, verify API key
```

---

## Next Steps

After completing this quickstart:

1. **Review**: `specs/sphaseIII/002-ai-chat-service-integration/plan.md` for architecture details
2. **Implement**: Follow `specs/sphaseIII/002-ai-chat-service-integration/tasks.md` (when generated)
3. **Test**: Write unit and integration tests for all components
4. **Deploy**: Follow deployment guide in repository README

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Better Auth Docs](https://www.better-auth.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Gemini API Docs](https://ai.google.dev/docs)

---

**Setup Complete!** You're ready to implement the AI-powered conversational task management feature.

For questions or issues, refer to the constitution at `.specify/memory/constitution.md` or the project README.
