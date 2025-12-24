# Phase III - Docker Deployment Guide

Complete guide for running Phase III with Docker and Docker Compose.

## Quick Start

```bash
# From phaseIII directory
docker compose up -d

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - MCP Server: http://localhost:8001
# - Redis: localhost:6379
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                 Docker Compose Stack                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │  MCP Server  │  │
│  │  (Next.js)   │  │  (FastAPI)   │  │   (FastMCP)  │  │
│  │  Port 3000   │  │  Port 8000   │  │  Port 8001   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┼──────────────────┘          │
│                           │                             │
│                  ┌────────▼────────┐                    │
│                  │     Redis       │                    │
│                  │   Port 6379     │                    │
│                  └─────────────────┘                    │
│                                                          │
│         Network: phaseiii-network (bridge)              │
└─────────────────────────────────────────────────────────┘
```

## Services

### 1. Frontend (phaseiii-frontend)
- **Technology**: Next.js 16 + React 19
- **Port**: 3000
- **Image Size**: ~150MB
- **Features**:
  - Multi-stage build with standalone output
  - Non-root user (nextjs:nodejs)
  - Health checks enabled
  - ChatKit React integration

### 2. Backend (phaseiii-backend)
- **Technology**: FastAPI + ChatKit SDK
- **Port**: 8000
- **Image Size**: ~200MB
- **Features**:
  - UV package manager for fast builds
  - Multi-stage build
  - Non-root user (appuser)
  - Alembic migrations included
  - Health checks enabled

### 3. MCP Server (phaseiii-mcp-server)
- **Technology**: FastMCP HTTP Server
- **Port**: 8001
- **Image Size**: ~200MB
- **Features**:
  - Standalone MCP server
  - Non-root user (mcpuser)
  - 5 task management tools
  - Health checks enabled

### 4. Redis (phaseiii-redis)
- **Technology**: Redis 7 Alpine
- **Port**: 6379
- **Features**:
  - Persistent data storage
  - AOF (Append-Only File) enabled
  - Health checks enabled

## Docker Images

All images are optimized using multi-stage builds:

### Frontend Dockerfile
```dockerfile
Stage 1: deps     - Install dependencies (node_modules)
Stage 2: builder  - Build Next.js (standalone output)
Stage 3: runner   - Minimal runtime (Node 20-alpine)
```

### Backend Dockerfile
```dockerfile
Stage 1: builder  - UV install dependencies (.venv)
Stage 2: runtime  - Python 3.11-slim + app code
```

### MCP Server Dockerfile
```dockerfile
Stage 1: builder  - UV install dependencies (.venv)
Stage 2: runtime  - Python 3.11-slim + MCP app
```

## Environment Variables

### Required for All Services

Create a `.env` file in the phaseIII directory:

```bash
# Database (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# AI Models (at least one required)
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=your_gemini_api_key

# Better Auth
BETTER_AUTH_SECRET=your-32-char-secret-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

## Common Commands

### Starting Services

```bash
# Start all services
docker compose up

# Start in background (detached)
docker compose up -d

# Start specific services
docker compose up backend mcp-server

# Rebuild and start
docker compose up --build

# Watch logs
docker compose logs -f
docker compose logs -f backend
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop specific service
docker compose stop backend
```

### Managing Services

```bash
# Check status
docker compose ps

# Restart service
docker compose restart backend

# View logs
docker compose logs -f backend

# Execute command in container
docker compose exec backend bash

# Rebuild specific service
docker compose build backend
```

### Database Operations

```bash
# Run migrations
docker compose exec backend uv run alembic upgrade head

# Create new migration
docker compose exec backend uv run alembic revision --autogenerate -m "description"

# Rollback migration
docker compose exec backend uv run alembic downgrade -1
```

## Resource Management

Each service has configured resource limits in docker-compose.yml:

| Service | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved |
|---------|-----------|--------------|--------------|-----------------|
| Backend | 1.0 core  | 1GB          | 0.5 core     | 512MB           |
| Frontend| 1.0 core  | 1GB          | 0.5 core     | 512MB           |
| MCP     | 0.5 core  | 512MB        | 0.25 core    | 256MB           |
| Redis   | 0.5 core  | 256MB        | 0.25 core    | 128MB           |

Adjust these limits in docker-compose.yml based on your system resources.

## Health Checks

All services include health checks:

- **Backend**: `curl http://localhost:8000/health`
- **MCP Server**: `curl http://localhost:8001/health`
- **Frontend**: `curl http://localhost:3000/`
- **Redis**: `redis-cli ping`

Health check intervals: 30s (10s for Redis)

## Development vs Production

### Development Mode (Current)

- Volume mounts enabled for hot-reload
- Source code mounted as read-only
- .env file mounted
- Verbose logging

```yaml
volumes:
  - ./backend/app:/app/app:ro
  - ./backend/.env:/app/.env:ro
```

### Production Mode

Remove volume mounts from docker-compose.yml:

```yaml
# Remove this section for production
# volumes:
#   - ./backend/app:/app/app:ro
```

Use production environment file:

```bash
docker compose --env-file .env.production up -d
```

## Networking

All services communicate via Docker network: `phaseiii-network`

- **Internal URLs**:
  - Backend: `http://backend:8000`
  - MCP Server: `http://mcp-server:8001`
  - Frontend: `http://frontend:3000`
  - Redis: `redis://redis:6379`

- **External URLs** (from host):
  - Backend: `http://localhost:8000`
  - MCP Server: `http://localhost:8001`
  - Frontend: `http://localhost:3000`
  - Redis: `localhost:6379`

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs service-name

# Check container status
docker compose ps

# Inspect container
docker inspect phaseiii-backend
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Health Check Failing

```bash
# Manual health check
docker compose exec backend curl -f http://localhost:8000/health

# Check logs for errors
docker compose logs backend

# Restart service
docker compose restart backend
```

### Out of Memory

```bash
# Check container resources
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1G
```

### Database Connection Issues

```bash
# Verify DATABASE_URL
docker compose exec backend env | grep DATABASE_URL

# Test connection
docker compose exec backend python -c "from sqlmodel import create_engine; engine = create_engine('your_url'); print('Connected!')"

# Check if using correct host (localhost vs docker service name)
```

### Frontend Signup/Login Not Working

**Symptoms:**
- "database error" on signup
- "Failed to initialize database adapter" in frontend logs
- 500 errors on `/api/auth/sign-up/email`

**Solutions:**

**1. Verify NEXT_PUBLIC_BETTER_AUTH_URL**
```bash
# Check frontend environment
docker compose exec frontend env | grep NEXT_PUBLIC_BETTER_AUTH_URL

# Should be: http://localhost:3000
# NOT: http://localhost:8000/auth
```

**Fix**: Update `.env` file:
```bash
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Explanation**: Better Auth routes (`/api/auth/*`) are in the **frontend**, not backend.

**2. Check Better Auth Database Connection**

Frontend logs showing adapter errors means Better Auth can't connect to PostgreSQL:

```bash
# View frontend logs
docker compose logs -f frontend

# Look for: "Failed to initialize database adapter"
```

**Verify**:
- `DATABASE_URL` is set in `.env` and passed to frontend container
- Better Auth tables exist in database (run migrations if needed)
- Database accepts connections from Docker network

**3. Rebuild Frontend After .env Changes**

Environment variables are baked into the Next.js build:

```bash
# Rebuild and restart frontend
docker compose build frontend
docker compose up -d frontend

# Or force recreate
docker compose up -d --force-recreate frontend
```

**4. Verify Better Auth Tables**

```bash
# Connect to your database and check tables exist:
# - user
# - session
# - account
# - verification

# If missing, run migrations in backend:
docker compose exec backend uv run alembic upgrade head
```

### AI Model API Key Issues

**Symptoms:**
- "Incorrect API key provided" errors
- "Quota exceeded" or rate limiting errors
- Chat responses fail with authentication errors

**Solutions:**

**1. OpenAI vs Gemini Selection**

Backend prefers OpenAI if both keys are set (see `backend/app/chatkit/task_server.py:58-71`):

```python
if settings.openai_api_key:    # ← Checks OpenAI first
    # Use GPT-3.5-turbo
elif settings.gemini_api_key:  # ← Falls back to Gemini
    # Use Gemini 2.5 Pro
```

**2. Fix Invalid API Key**

```bash
# Check which key is active
docker compose exec backend env | grep -E 'OPENAI_API_KEY|GEMINI_API_KEY'

# Update .env with valid key
nano .env

# Restart backend to pick up changes
docker compose restart backend

# Verify in logs
docker compose logs backend | grep "initialized with"
# Should see: "TaskChatServer initialized with GPT-3.5-turbo" or "Gemini 2.5 Pro"
```

**3. Handle Rate Limiting**

**Gemini Free Tier Exhausted:**
```
litellm.RateLimitError: Quota exceeded for metric:
generativelanguage.googleapis.com/generate_content_free_tier_requests
```

**Solutions:**
- Use OpenAI instead (set `OPENAI_API_KEY` in `.env`)
- Or upgrade to Gemini paid tier
- Or wait for quota reset (free tier resets daily)

**4. Switch Between Models**

To use **OpenAI GPT-3.5**:
```bash
# .env
OPENAI_API_KEY=sk-proj-your-key-here
#GEMINI_API_KEY=  # Comment out or leave empty
```

To use **Gemini 2.5 Pro**:
```bash
# .env
#OPENAI_API_KEY=  # Comment out
GEMINI_API_KEY=your-gemini-key-here
```

Then restart:
```bash
docker compose restart backend
```

## Best Practices

### 1. Security
- ✅ All services run as non-root users
- ✅ No secrets in Dockerfiles
- ✅ Environment variables for configuration
- ✅ Minimal base images (alpine, slim)
- ✅ Health checks enabled

### 2. Performance
- ✅ Multi-stage builds for smaller images
- ✅ Layer caching optimized
- ✅ Dependencies installed before source code
- ✅ Resource limits configured
- ✅ Redis for caching

### 3. Development
- ✅ Hot-reload with volume mounts
- ✅ Source code mounted as read-only
- ✅ Easy log access
- ✅ Service dependencies managed
- ✅ Network isolation

### 4. Production
- Remove volume mounts
- Use production environment variables
- Enable HTTPS/SSL
- Configure proper resource limits
- Set up monitoring and alerting
- Use secrets management (Docker Secrets, Vault)

## CI/CD Integration

### Building Images

```bash
# Build all images
docker compose build

# Build with cache disabled
docker compose build --no-cache

# Push to registry
docker tag phaseiii-backend:latest registry.example.com/phaseiii-backend:latest
docker push registry.example.com/phaseiii-backend:latest
```

### GitHub Actions Example

```yaml
name: Build and Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: |
          cd phaseIII
          docker compose build
      - name: Push to registry
        run: |
          docker tag phaseiii-backend:latest ${{ secrets.REGISTRY }}/backend:latest
          docker push ${{ secrets.REGISTRY }}/backend:latest
```

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific service
docker stats phaseiii-backend

# Export metrics
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Log Management

```bash
# Follow logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail 100

# Since timestamp
docker compose logs --since 2024-01-01T00:00:00

# Service-specific
docker compose logs -f backend mcp-server
```

## Backup and Restore

### Redis Data Backup

```bash
# Backup Redis data
docker compose exec redis redis-cli BGSAVE
docker cp phaseiii-redis:/data/dump.rdb ./backup/

# Restore Redis data
docker cp ./backup/dump.rdb phaseiii-redis:/data/
docker compose restart redis
```

### Database Backup (PostgreSQL)

```bash
# Dump database (from container with pg_dump)
docker compose exec backend pg_dump $DATABASE_URL > backup.sql

# Restore database
docker compose exec -T backend psql $DATABASE_URL < backup.sql
```

## Additional Resources

- **Backend README**: `phaseIII/backend/README.md`
- **Frontend README**: `phaseIII/frontend/README.md`
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

**Last Updated**: 2025-12-23
**Docker Compose Version**: 2.x+
**Docker Engine Version**: 20.10+
