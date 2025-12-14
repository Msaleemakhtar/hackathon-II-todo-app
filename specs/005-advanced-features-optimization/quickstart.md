# Quickstart Guide: Advanced Features & Optimization

**Feature**: Advanced Features & Optimization - Time Reminders, Notifications, Performance, UX, Monitoring & Analytics  
**Branch**: `005-advanced-features-optimization`  
**Input**: Feature specification from `/specs/005-advanced-features-optimization/spec.md`  

## Overview

This guide will help you set up the development environment for the Advanced Features & Optimization branch of the Todo App, including:

- Time reminders and notifications
- Performance optimization features
- UX enhancements (keyboard shortcuts, drag-and-drop)
- Monitoring and analytics integration
- PWA capabilities

## Prerequisites

- Python 3.11+
- Node.js 18+ (or Bun 1.0+)
- PostgreSQL 12+
- Redis server
- Docker and Docker Compose (recommended for local development)

## Local Development Setup

### 1. Clone and Prepare Repository

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd hackathon-II-todo-app

# Switch to the feature branch
git checkout 005-advanced-features-optimization
```

### 2. Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Set up Python environment (recommended to use virtual environment):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
# Or if uv is not available:
pip install -r requirements.txt
```

4. Set up environment variables (copy `.env.example` to `.env` and configure):
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Configure required services in `.env`:
   - Database connection (DATABASE_URL)
   - Redis connection (REDIS_URL)
   - SMTP settings (for email notifications)
   - Sentry DSN (for error tracking)
   - Better Auth shared secret
   - VAPID keys (for web push notifications)

### 3. Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
bun install
# Or if using npm:
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Add required environment variables to `.env.local`:
   - NEXT_PUBLIC_API_BASE_URL
   - NEXT_PUBLIC_SENTRY_DSN
   - Any other frontend-specific variables

### 4. Required Services Configuration

#### Redis Setup
1. Install Redis:
   - macOS: `brew install redis`
   - Ubuntu: `sudo apt install redis-server`
   - Or run with Docker: `docker run -p 6379:6379 --name todo-redis -d redis:alpine`

2. Start Redis server:
   - Manual: `redis-server`
   - Or via Docker: `docker start todo-redis`

#### PostgreSQL Setup
1. Ensure PostgreSQL is running and accessible
2. Create the database if it doesn't exist:
   - Connect to PostgreSQL: `psql -U postgres`
   - Create database: `CREATE DATABASE todoapp_development;`
   - Create user if needed: `CREATE USER todoapp_user WITH PASSWORD 'your_password';`
   - Grant privileges: `GRANT ALL PRIVILEGES ON DATABASE todoapp_development TO todoapp_user;`

#### SMTP Configuration
To enable email notifications, configure SMTP settings in your backend `.env`:
- `SMTP_HOST`: Your SMTP server (e.g., smtp.gmail.com)
- `SMTP_PORT`: Port number (e.g., 587 for TLS)
- `SMTP_USERNAME`: Your email address
- `SMTP_PASSWORD`: Your email app password
- `SMTP_FROM_EMAIL`: Email address to send from

#### VAPID Keys for Web Push Notifications
Generate VAPID keys for browser notifications:
1. Install web-push: `pip install web-push`
2. Generate keys using a VAPID key generator tool or library
3. Set `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY` in `.env`

## Running the Application

### Method 1: Using Docker Compose (Recommended)

1. From the project root:
```bash
docker-compose up --build
```

2. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - Backend docs: http://localhost:8000/docs

### Method 2: Manual Setup

1. Start backend:
```bash
# In backend directory
source venv/bin/activate  # Activate virtual environment
uv run alembic upgrade head  # Run database migrations
uv run uvicorn src.main:app --reload --port 8000
```

2. In a new terminal, start frontend:
```bash
# In frontend directory  
bun run dev
```

3. Both services will be running:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Required Services

### Redis
- For caching layer implementation
- Used by backend for storing frequently accessed data
- Ensure Redis server is running before starting the backend

### PostgreSQL
- Primary database for all application data
- Stores tasks, users, reminders, and other entities
- Ensure database is created and accessible

### SMTP Server
- For sending email notifications
- Configure in backend `.env` file
- Required for reminder functionality

### Sentry Account
- For error tracking and monitoring
- Required for error monitoring features
- Get DSN from your Sentry dashboard

## Testing the New Features

### 1. Reminders and Notifications
1. Create a task with a due date
2. Set a reminder for that task
3. Verify the reminder appears in the notification bell
4. Check that you receive the notification at the scheduled time

### 2. Performance Features
1. Create 10,000+ tasks using the test data script
2. Navigate to the task list page
3. Verify smooth scrolling performance
4. Check that virtual scrolling is working correctly

### 3. Keyboard Shortcuts
1. Visit the main task list page
2. Press `Cmd/Ctrl+K` - should open quick search
3. Press `Cmd/Ctrl+N` - should open new task modal
4. Press `?` - should show keyboard shortcuts help

### 4. Drag-and-Drop
1. Go to the task list page
2. Drag a task to a new position
3. Verify the visual reorder happens immediately
4. Refresh the page and verify the new order persists

### 5. Offline Functionality
1. Load the app in a browser
2. Go to offline mode (dev tools)
3. Verify that cached tasks are still visible
4. Make changes while offline
5. Go back online and verify changes sync

### 6. PWA Features
1. Visit the app in Chrome or other supported browser
2. Check for install prompt in address bar
3. Install the PWA
4. Open as standalone app
5. Verify it works without internet connection

## Troubleshooting

### Common Issues

1. **Database migrations failing**: Run `alembic upgrade head` to apply latest migrations
2. **Redis not connecting**: Verify Redis server is running and URL is correct
3. **Frontend can't connect to backend**: Check that both are running and CORS settings are correct
4. **Web push notifications not working**: Verify VAPID keys are correctly configured
5. **Email notifications failing**: Check SMTP configuration in `.env`

### Performance Testing

To test the performance optimizations:
```bash
# Run the performance test script (if available)
python scripts/performance_test.py

# Or use the load testing tool
# (Tool and instructions would be in a separate performance testing documentation)
```

## Next Steps

1. Complete the initial setup and verify all services are running
2. Run the test suite to ensure everything is working correctly
3. Review the tasks in `/specs/005-advanced-features-optimization/tasks.md` to begin implementation
4. Start with the setup tasks (T001-T004) as mentioned in the task breakdown