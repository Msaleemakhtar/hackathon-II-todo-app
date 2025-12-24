#!/bin/bash
# Development script to run MCP server locally

set -e

# Load environment variables (skip complex ones like CORS_ORIGINS)
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | grep -v '^CORS_ORIGINS' | sed 's/\r$//')
    set +a
fi

# Set MCP server configuration
export MCP_HOST=${MCP_HOST:-0.0.0.0}
export MCP_PORT=${MCP_PORT:-8001}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Starting MCP Server (Development Mode)"
echo "======================================"
echo "Host: $MCP_HOST"
echo "Port: $MCP_PORT"
echo "Database: ${DATABASE_URL:0:30}..."
echo ""

# Run with hot-reload for development
uv run python -m app.mcp.standalone
