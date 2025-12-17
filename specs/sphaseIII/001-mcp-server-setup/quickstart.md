# Quickstart Guide: Phase III MCP Server

**Feature**: MCP Server Implementation
**Last Updated**: 2025-12-17
**For**: Developers setting up Phase III backend

---

## Prerequisites

### Required Tools

- **Python**: 3.11+ (Phase III requirement)
- **UV**: Package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **PostgreSQL**: Neon serverless instance (or local Postgres 14+)
- **Git**: Version control

### Environment Setup

1. **Clone Repository** (if not already done):
   ```bash
   cd /path/to/hackathon-II-todo-app
   git checkout 001-mcp-server-setup  # Feature branch
   ```

2. **Navigate to Phase III Backend**:
   ```bash
   cd phaseIII/backend
   ```

3. **Create Environment File**:
   ```bash
   cp .env.example .env
   ```

4. **Configure Environment Variables** (`.env`):
   ```bash
   # Database
   DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname?ssl=require

   # Authentication (shared with frontend)
   BETTER_AUTH_SECRET=your-32-char-secret-here-must-match-frontend

   # Optional: Performance tuning
   DB_POOL_MIN=5
   DB_POOL_MAX=10
   JWT_CACHE_SIZE=1000
   JWT_CACHE_TTL=1800

   # Development
   DEBUG=true
   ```

---

## Installation

### 1. Install Dependencies

```bash
# Install all dependencies via UV
uv sync

# This installs:
# - FastAPI (web framework)
# - SQLModel (ORM)
# - Alembic (migrations)
# - asyncpg (PostgreSQL driver)
# - python-jose (JWT validation)
# - MCP SDK (tool server)
# - pytest, pytest-asyncio (testing)
```

### 2. Initialize Database

```bash
# Run Alembic migrations
uv run alembic upgrade head

# This creates:
# - tasks_phaseiii table
# - conversations table
# - messages table
# - All required indexes
```

### 3. Verify Installation

```bash
# Check database connection
uv run python -c "from app.database import engine; import asyncio; asyncio.run(engine.dispose())"

# Expected: No errors
```

---

## Running the Server

### Development Mode

```bash
# Start FastAPI with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server starts at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

### Production Mode

```bash
# Start with multiple workers
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Recommended workers: 2-4 per CPU core
```

### Background Process

```bash
# Run in background with nohup
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Check logs
tail -f nohup.out
```

---

## Testing

### Run All Tests

```bash
# Run full test suite
uv run pytest

# Expected output:
# ======================== test session starts =========================
# collected X items
#
# tests/test_models.py ........                                   [ 20%]
# tests/test_mcp_tools/test_add_task.py ....                      [ 30%]
# tests/test_mcp_tools/test_list_tasks.py .....                   [ 45%]
# tests/test_mcp_tools/test_complete_task.py ....                 [ 60%]
# tests/test_mcp_tools/test_delete_task.py ....                   [ 75%]
# tests/test_mcp_tools/test_update_task.py .....                  [ 95%]
# tests/test_integration.py ..                                    [100%]
#
# ======================== X passed in Xs ===========================
```

### Run Specific Test Category

```bash
# MCP tools only
uv run pytest tests/test_mcp_tools/

# Integration tests only
uv run pytest tests/test_integration.py

# With coverage report
uv run pytest --cov=app --cov-report=term-missing

# Expected coverage: ≥80%
```

### Run Single Test

```bash
# Test specific tool
uv run pytest tests/test_mcp_tools/test_add_task.py::test_add_task_creates_task

# With verbose output
uv run pytest -v tests/test_mcp_tools/test_add_task.py
```

---

## Verify MCP Server

### Check Tool Registration

```bash
# List registered MCP tools
uv run python -c "
from app.mcp.server import mcp_server
print('Registered tools:', [t.name for t in mcp_server.tools])
"

# Expected output:
# Registered tools: ['add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task']
```

### Test Tool Invocation

```bash
# Manually invoke add_task tool
uv run python -c "
import asyncio
from app.mcp.server import mcp_server

async def test():
    result = await mcp_server.invoke_tool(
        'add_task',
        user_id='test-user',
        title='Test task'
    )
    print('Result:', result)

asyncio.run(test())
"

# Expected output:
# Result: {'task_id': 1, 'status': 'created', 'title': 'Test task'}
```

---

## Database Management

### Create New Migration

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Add new field to tasks"

# Manually create migration
uv run alembic revision -m "Custom migration"

# Edit generated file in: alembic/versions/XXXXXX_migration_name.py
```

### Apply Migrations

```bash
# Upgrade to latest
uv run alembic upgrade head

# Upgrade one revision
uv run alembic upgrade +1

# Downgrade one revision
uv run alembic downgrade -1

# Check current revision
uv run alembic current
```

### Reset Database (Development Only)

```bash
# ⚠️ WARNING: Deletes all data

# Downgrade all migrations
uv run alembic downgrade base

# Re-apply all migrations
uv run alembic upgrade head
```

---

## Common Issues & Solutions

### Issue: Database Connection Failed

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:
1. **Check DATABASE_URL** in `.env`:
   ```bash
   echo $DATABASE_URL
   # Should start with: postgresql+asyncpg://
   ```

2. **Verify Neon connection**:
   ```bash
   psql "$DATABASE_URL"
   # Should connect without errors
   ```

3. **Check SSL requirement**:
   ```bash
   # Neon requires SSL, ensure URL has: ?ssl=require
   ```

---

### Issue: JWT Validation Failed

**Symptoms**:
```
jose.exceptions.JWTError: Signature verification failed
```

**Solutions**:
1. **Verify BETTER_AUTH_SECRET matches frontend**:
   ```bash
   # Backend .env
   BETTER_AUTH_SECRET=your-secret-here

   # Frontend .env
   BETTER_AUTH_SECRET=your-secret-here  # MUST MATCH
   ```

2. **Check token format**:
   ```bash
   # Token should be passed as:
   Authorization: Bearer <actual-jwt-token>
   ```

3. **Verify token hasn't expired**:
   ```bash
   # Tokens expire after 15-30 minutes
   # Frontend should auto-refresh via Better Auth
   ```

---

### Issue: Migration Version Conflict

**Symptoms**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions**:
1. **Check current revision**:
   ```bash
   uv run alembic current
   ```

2. **Resolve conflicts manually**:
   ```bash
   # Downgrade to common ancestor
   uv run alembic downgrade <revision>

   # Upgrade to head
   uv run alembic upgrade head
   ```

3. **Reset (development only)**:
   ```bash
   uv run alembic downgrade base
   uv run alembic upgrade head
   ```

---

### Issue: Port Already in Use

**Symptoms**:
```
OSError: [Errno 98] Address already in use
```

**Solutions**:
1. **Find process using port 8000**:
   ```bash
   lsof -i :8000
   # Or
   netstat -tuln | grep 8000
   ```

2. **Kill process**:
   ```bash
   kill -9 <PID>
   ```

3. **Use different port**:
   ```bash
   uv run uvicorn app.main:app --port 8001
   ```

---

### Issue: Import Error for Phase II Code

**Symptoms**:
```
ModuleNotFoundError: No module named 'phaseII'
```

**Solution**:
- **This is expected!** Phase III MUST NOT import from Phase II.
- Check imports - remove any `from phaseII...` or `import phaseII...`
- Use Phase III models: `from app.models.task import TaskPhaseIII`

---

### Issue: Test Database Pollution

**Symptoms**:
```
Tests fail due to existing data from previous runs
```

**Solutions**:
1. **Use test fixtures with cleanup**:
   ```python
   @pytest.fixture
   async def clean_db():
       # Tests run
       yield
       # Cleanup after test
       await session.execute(delete(TaskPhaseIII))
   ```

2. **Use testcontainers** (recommended):
   ```bash
   # Each test suite gets isolated PostgreSQL instance
   uv add --dev testcontainers
   ```

---

## API Documentation

### OpenAPI (Swagger) UI

Visit: http://localhost:8000/docs

- Interactive API testing
- Auto-generated from FastAPI
- Test MCP tools directly

### ReDoc

Visit: http://localhost:8000/redoc

- Clean, readable API documentation
- Better for reading than Swagger

### JSON Schema

Visit: http://localhost:8000/openapi.json

- Raw OpenAPI 3.0 schema
- Use for code generation

---

## Development Workflow

### Daily Development Loop

1. **Pull latest changes**:
   ```bash
   git pull origin 001-mcp-server-setup
   ```

2. **Apply new migrations**:
   ```bash
   uv run alembic upgrade head
   ```

3. **Start server with auto-reload**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. **Make changes**:
   - Edit code in `app/`
   - Server auto-reloads on file changes

5. **Run tests**:
   ```bash
   uv run pytest
   ```

6. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement add_task MCP tool"
   ```

### Code Quality Checks

```bash
# Run linter
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type check
uv run mypy app/
```

---

## Debugging

### Enable SQL Echo

```python
# In app/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Logs all SQL queries
)
```

### Enable Debug Logging

```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Python Shell

```bash
# Start REPL with app context
uv run python
```

```python
>>> from app.database import engine
>>> from app.models.task import TaskPhaseIII
>>> import asyncio
>>>
>>> async def test():
...     async with engine.begin() as conn:
...         result = await conn.execute("SELECT COUNT(*) FROM tasks_phaseiii")
...         print(result.scalar())
>>>
>>> asyncio.run(test())
```

---

## Performance Monitoring

### Check Database Connection Pool

```bash
# Monitor active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'your_db';
```

### Measure Tool Response Time

```python
import time
start = time.time()
result = await mcp_server.invoke_tool('list_tasks', user_id='test')
print(f"Response time: {(time.time() - start) * 1000:.2f}ms")
```

---

## Next Steps

1. **Implement MCP Tools** → See `specs/sphaseIII/001-mcp-server-setup/plan.md`
2. **Run Tests** → Ensure ≥80% coverage
3. **Integrate with OpenAI Agents SDK** → Next feature (002-chat-endpoint)
4. **Deploy to Production** → See deployment guide (TBD)

---

## Additional Resources

- **Specification**: `specs/sphaseIII/001-mcp-server-setup/spec.md`
- **Implementation Plan**: `specs/sphaseIII/001-mcp-server-setup/plan.md`
- **Data Model**: `specs/sphaseIII/001-mcp-server-setup/data-model.md`
- **Tool Contracts**: `specs/sphaseIII/001-mcp-server-setup/contracts/*.json`
- **Constitution**: `.specify/memory/constitution.md`
- **MCP SDK Docs**: https://github.com/modelcontextprotocol/python-sdk
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/

---

**Quickstart Version**: 1.0
**Maintained By**: Phase III Development Team
**Last Verified**: 2025-12-17
