#!/bin/bash
# Development script to run backend locally

set -e

# Load environment variables (skip complex ones like CORS_ORIGINS)
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | grep -v '^CORS_ORIGINS' | sed 's/\r$//')
    set +a
fi

# Set configuration for local development
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost:8001}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Starting Backend API (Development Mode)"
echo "========================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "MCP Server: $MCP_SERVER_URL"
echo "Database: ${DATABASE_URL:0:30}..."
echo ""

# Run with hot-reload for development
uv run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
