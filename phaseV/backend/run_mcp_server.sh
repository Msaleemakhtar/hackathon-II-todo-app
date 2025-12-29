#!/bin/bash
# MCP Server launcher script
cd "$(dirname "$0")"
exec uv run python -m app.mcp
