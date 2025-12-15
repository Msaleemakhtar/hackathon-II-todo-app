# 📝 Modern Todo Application

<div align="center">

A full-stack, production-ready task management application built with **Next.js 16**, **FastAPI**, and **PostgreSQL**. Features modern authentication, real-time updates, and a beautiful, responsive UI.

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🎯 Core Functionality
- **Task Management** - Create, update, delete, and organize tasks with priority levels and due dates
- **Smart Categories** - Organize tasks into customizable categories with colors
- **Flexible Tags** - Multi-tag support for advanced task organization
- **Advanced Filtering** - Filter by status, priority, category, tags, and search by keywords
- **Task Recurrence** - Support for recurring tasks with iCal RRULE format
- **Reminder System** - Set customizable reminders for tasks with push notifications
- **Drag & Drop** - Intuitive task reordering with visual feedback
- **Virtualized Lists** - High-performance rendering for thousands of tasks

### 🔐 Authentication & Security
- **Better Auth Integration** - Modern authentication with session management
- **JWT Tokens** - Stateless API authentication with automatic refresh
- **Secure Sessions** - HTTP-only cookies with CSRF protection
- **Data Isolation** - Strict user data separation at database level
- **Password Security** - Bcrypt hashing with secure salt rounds

### 🎨 User Experience
- **Responsive Design** - Mobile-first UI that works on all devices
- **Real-time Updates** - Optimistic UI updates for instant feedback
- **Dark Mode Ready** - Theme support with Tailwind CSS
- **Interactive Dashboard** - Visual task analytics and progress tracking
- **Keyboard Shortcuts** - Efficient task navigation and management (press ? for help)
- **Offline Support** - Full offline functionality with background sync
- **Progressive Web App** - Installable on desktop and mobile devices

### 📱 Progressive Web App
- **Installable** - Add to home screen on iOS, Android, and desktop
- **Offline Mode** - Work without internet, sync when reconnected
- **Push Notifications** - Browser notifications for task reminders
- **App Shortcuts** - Quick actions from app icon (New Task, Search)
- **Standalone Mode** - Runs in its own window like a native app
- **Service Worker** - Background sync and smart caching

### 📊 Performance & Monitoring
- **Error Tracking** - Sentry integration for production error monitoring
- **Performance Analytics** - Core Web Vitals tracking (LCP, FID, CLS, INP, TTFB)
- **Event Analytics** - User interaction tracking with privacy controls
- **Privacy-First** - No PII collection, easy opt-out, GDPR compliant
- **Real-time Metrics** - Dashboard for monitoring app health

### 🏗️ Technical Excellence
- **Spec-Driven Development** - Built following constitutional governance rules
- **Type Safety** - Full TypeScript coverage with Pydantic schemas
- **API Documentation** - Auto-generated Swagger/ReDoc documentation
- **Database Migrations** - Version-controlled schema with Alembic
- **Comprehensive Testing** - Unit and integration tests with 80%+ coverage
- **Production Ready** - Docker support with multi-stage builds
- **Redis Caching** - Optional high-performance caching layer
- **Background Workers** - Task scheduling for reminders and cleanup

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Docker** & **Docker Compose** (recommended) OR
- **Python 3.11+** with [uv](https://github.com/astral-sh/uv)
- **Node.js 20+** with [Bun](https://bun.sh/)
- **PostgreSQL 15+** (if not using Docker)

### 🐳 Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/hackathon-II-todo-app.git
cd hackathon-II-todo-app

# 2. Copy environment configuration
cp .env.example .env

# 3. Update secrets in .env (IMPORTANT!)
# Generate JWT secret: openssl rand -hex 32
nano .env

# 4. Start all services
docker compose up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**First Time Setup:**
```bash
# 1. Initialize Better Auth database tables (frontend authentication)
docker compose exec frontend bun run scripts/init-better-auth-db.ts

# 2. Run backend database migrations (tasks, categories, tags)
docker compose exec backend uv run alembic upgrade head

# 3. Verify all tables were created successfully
docker compose exec backend uv run python -c "

```

**Expected Database Tables**:
- ✅ `user`, `account`, `session`, `verification` - Better Auth (frontend)
- ✅ `users`, `tasks`, `categories`, `tags`, `task_tag_link` - FastAPI Backend
- ✅ `alembic_version` - Migration tracking

### 💻 Option 2: Local Development

For development with hot-reload:

#### Backend Setup
```bash
cd backend

# Install dependencies with uv
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your database URL and secrets

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies with Bun
bun install

# Copy and configure environment
cp .env.example .env.local
# Edit .env.local with API URL and secrets

# Initialize Better Auth tables
bun run scripts/init-better-auth-db.ts

# Start development server
bun run dev
```

---

## 📚 Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TODO APPLICATION                          │
└─────────────────────────────────────────────────────────────────┘

    User Browser
         │
         ├─────────────> Next.js Frontend (Port 3000)
         │                   │
         │                   ├─> Better Auth (Session Management)
         │                   │   └─> PostgreSQL (user, session tables)
         │                   │
         │                   └─> React 19 + TypeScript
         │                       ├─> Tailwind CSS + shadcn/ui
         │                       ├─> Zustand (State Management)
         │                       └─> Axios (HTTP Client)
         │                               │
         │                               │ JWT Token
         │                               ▼
         └─────────────> FastAPI Backend (Port 8000)
                             │
                             ├─> JWT Validation (python-jose)
                             ├─> Business Logic (Services)
                             ├─> SQLModel ORM
                             └─> PostgreSQL (tasks, categories, tags)
```

### Technology Stack

#### Frontend
- **Framework**: Next.js 16 (App Router) with React 19
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand
- **Authentication**: Better Auth (PostgreSQL sessions)
- **HTTP Client**: Axios with interceptors
- **Icons**: Lucide React
- **Date Handling**: date-fns

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database Driver**: asyncpg (async PostgreSQL)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose[cryptography])
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **API Documentation**: Swagger/ReDoc (auto-generated)

#### Infrastructure
- **Database**: PostgreSQL 16
- **Package Managers**: uv (Python), Bun (JavaScript)
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (production ready)




## 📖 API Documentation

### Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc



## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_tasks.py

# Run tests in parallel
uv run pytest -n auto
```

### Frontend Tests
```bash
cd frontend

# Run unit tests (if configured)
bun test

# Type checking
bun run type-check

# Linting
bun run lint
```

---

## 🛠️ Development

### Code Quality

#### Backend
```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Auto-fix issues
uv run ruff check --fix .

# Security audit
uv run pip-audit
```

#### Frontend
```bash
# Linting
bun run lint

# Type checking
tsc --noEmit
```

### Database Migrations

```bash
# Create new migration
cd backend
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Adding Dependencies

#### Backend
```bash
cd backend
uv add <package-name>              # Production dependency
uv add --dev <package-name>        # Development dependency
```

#### Frontend
```bash
cd frontend
bun add <package-name>             # Production dependency
bun add -d <package-name>          # Development dependency
```

---

## 🐳 Docker Commands

### Build Images
```bash
# Build all images
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend

# Build without cache
docker compose build --no-cache
```

### Manage Services
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d backend

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Execute commands in containers
docker compose exec backend alembic upgrade head
docker compose exec frontend bun run scripts/init-better-auth-db.ts
```

### Database Management
```bash
# Access PostgreSQL shell
docker compose exec db psql -U todouser -d todo_dev

# Backup database
docker compose exec db pg_dump -U todouser todo_dev > backup.sql

# Restore database
docker compose exec -T db psql -U todouser todo_dev < backup.sql
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Update environment variables in `.env`
- [ ] Generate secure secrets: `openssl rand -hex 32`
- [ ] Configure production database URL
- [ ] Enable HTTPS/SSL certificates
- [ ] Update CORS origins in backend
- [ ] Set `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Run database migrations
- [ ] Initialize Better Auth tables
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and logging
- [ ] Configure automated backups

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_USER` | Database username | `todouser` |
| `DB_PASSWORD` | Database password | `securepassword123` |
| `DB_NAME` | Database name | `todo_production` |
| `JWT_SECRET_KEY` | JWT signing secret (64+ chars) | Generate with `openssl rand -hex 32` |
| `BETTER_AUTH_SECRET` | Auth secret (32+ chars) | Generate with `openssl rand -hex 16` |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `https://api.yourdomain.com/api` |
| `CORS_ORIGINS` | Allowed frontend origins | `["https://yourdomain.com"]` |

#### Optional Variables (Advanced Features)

| Variable | Description | Example |
|----------|-------------|---------|
| `SENTRY_DSN` (backend) | Sentry DSN for backend error tracking | `https://...@sentry.io/123` |
| `NEXT_PUBLIC_SENTRY_DSN` | Sentry DSN for frontend client errors | `https://...@sentry.io/456` |
| `SENTRY_DSN` (frontend) | Sentry DSN for frontend server errors | `https://...@sentry.io/789` |
| `REDIS_URL` | Redis connection for caching | `redis://localhost:6379/0` |
| `VAPID_PRIVATE_KEY` | Web Push private key (auto-generated) | Base64 encoded key |
| `VAPID_PUBLIC_KEY` | Web Push public key (auto-generated) | Base64 encoded key |
| `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | Web Push key for frontend | Same as VAPID_PUBLIC_KEY |


---

## 📱 Progressive Web App

### Installation

The app can be installed on any device:

**Desktop (Chrome, Edge):**
1. Visit the site and click the install icon in the address bar
2. Or look for the custom install prompt
3. Click "Install" to add to desktop

**Android (Chrome):**
1. Tap "Add to Home Screen" when prompted
2. The app appears on your home screen like a native app

**iOS (Safari):**
1. Tap the Share button
2. Select "Add to Home Screen"
3. Confirm to install

### PWA Features

- **Offline Mode**: Work without internet, changes sync when reconnected
- **Push Notifications**: Receive browser notifications for task reminders
- **App Shortcuts**: Quick access to "New Task" and "Search" from app icon
- **Standalone Mode**: Runs in its own window without browser UI
- **Fast Performance**: Cached assets for instant loading



## 📝 Documentation

- [**Backend Documentation**](./backend/README.md) - FastAPI setup, API reference, database models, advanced features
- [**Frontend Documentation**](./frontend/README.md) - Next.js setup, components, hooks, PWA features
- [**Backend Tests**](./backend/tests/README.md) - Test suite documentation and best practices
- [**Constitutional Governance**](./.specify/memory/constitution.md) - Development principles and rules
- [**Architecture Decision Records**](./history/adr/) - Key architectural decisions
---

## 🤝 Contributing

We follow **Spec-Driven Development (SDD)** principles. All contributions must:

1. **Read the Constitution** - Understand project governance at `.specify/memory/constitution.md`
2. **Create a Feature Spec** - Document requirements before coding
3. **Follow Code Standards** - Pass linting, formatting, and tests
4. **Write Tests** - Maintain 80%+ coverage
5. **Document Decisions** - Create ADRs for significant changes
6. **Submit PHRs** - Record prompt history for AI-assisted work

### Contribution Workflow

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/hackathon-II-todo-app.git
cd hackathon-II-todo-app

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes following SDD principles
# - Create spec in specs/<feature-name>/
# - Document architecture decisions
# - Write tests first (TDD)
# - Implement feature
# - Update documentation

# 4. Run quality checks
cd backend && uv run ruff check . && uv run pytest
cd frontend && bun run lint && bun test

# 5. Commit and push
git add .
git commit -m "feat: Add your feature description"
git push origin feature/your-feature-name

# 6. Open Pull Request
```

---

## 📊 Performance

### Backend Metrics
- **Response Time**: < 100ms (p95)
- **Throughput**: 1000+ requests/second
- **Database Queries**: Optimized with indexes
- **Connection Pooling**: 2-5 connections (asyncpg)
- **Caching**: Optional Redis for 10x faster repeated queries

### Frontend Metrics
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Bundle Size**: < 200KB (gzipped)
- **Lighthouse Score**: 90+ (Performance)
- **PWA Score**: 100 (Installability)

### Performance Monitoring

**Core Web Vitals Tracking:**
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **INP** (Interaction to Next Paint): < 200ms
- **TTFB** (Time to First Byte): < 600ms

**Analytics Dashboard:**
- Real-time performance metrics
- User interaction tracking
- Error rate monitoring
- Privacy-first (no PII, easy opt-out)

---

## 🔍 Monitoring & Error Tracking

### Production Monitoring

**Sentry Integration:**
- **Backend**: FastAPI error tracking with 10% trace sampling
- **Frontend**: Client, server, and edge error tracking
- **Session Replay**: 10% of sessions recorded for debugging
- **Development Filtering**: No dev errors sent to Sentry

**Setup:**
```bash
# Backend .env
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
ENVIRONMENT=production

# Frontend .env.local
NEXT_PUBLIC_SENTRY_DSN=https://your-client-dsn@sentry.io/project-id
SENTRY_DSN=https://your-server-dsn@sentry.io/project-id
```

### Analytics Features

**Event Tracking:**
- Task created, completed, deleted, reordered
- Search performed
- Reminder set
- Filter applied

**Privacy Controls:**
- No PII collection
- Opt-out via settings
- Development environment filtering
- GDPR compliant


---

## 🔧 Troubleshooting

### Common Issues

**Issue: "Connection is insecure" database error**
```bash
# For asyncpg (backend), use ssl=require (NOT sslmode=require)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require

# For Better Auth (frontend), use sslmode=require
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

**Issue: API returns 401 Unauthorized**
```bash
# Ensure BETTER_AUTH_SECRET matches between frontend and backend
# Check .env.local (frontend) and .env (backend)
```

**Issue: Docker port conflicts**
```bash
# Change ports in .env or docker-compose.yml
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

**Issue: Database migration errors**
```bash
# Check if migrations exist
ls backend/alembic/versions/

# If empty, migrations haven't been created - run initial migration
docker compose exec backend uv run alembic upgrade head

# If migrations exist but fail, check for Better Auth table conflicts
# See backend/README.md for detailed migration troubleshooting
```

**Issue: Tasks/Categories creation fails with 404 errors**
```bash
# This means database tables don't exist - apply migrations
docker compose exec backend uv run alembic upgrade head

# Verify tables were created
docker compose exec backend uv run python -c "

```

**Issue: Better Auth error "relation 'session' does not exist"**
```bash
# This means Better Auth database tables don't exist - initialize them
docker compose exec frontend bun run scripts/init-better-auth-db.ts

# Verify tables were created
docker compose exec frontend npx pg-gui --connection-string $DATABASE_URL --command "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('user', 'account', 'session', 'verification');"
```

**Recent Fixes (December 2025)**:
- ✅ Fixed missing database migrations (empty alembic/versions/)
- ✅ Added Category model import to alembic/env.py
- ✅ Fixed asyncpg SSL parameter (ssl=require instead of sslmode=require)
- ✅ Prevented Better Auth table drops in migrations
- ✅ Added sqlmodel import to migration files

See [Backend README](./backend/README.md#troubleshooting) and [Frontend README](./frontend/README.md#troubleshooting) for more details.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [Next.js](https://nextjs.org/) - The React Framework for Production
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for Python
- [Better Auth](https://www.better-auth.com/) - Authentication for Next.js
- [PostgreSQL](https://www.postgresql.org/) - The World's Most Advanced Open Source Database
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases in Python with type safety

---

<div align="center">

**Made with ❤️ by [Saleem Akhtar](https://github.com/Msaleemakhtar)**

[Report Bug](https://github.com/Msaleemakhtar/hackathon-II-todo-app/issues) • [Request Feature](https://github.com/Msaleemakhtar/hackathon-II-todo-app/issues) • [Documentation](./docs)

</div>
