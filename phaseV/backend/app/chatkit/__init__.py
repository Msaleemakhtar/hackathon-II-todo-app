"""
ChatKit integration package for PhaseIII backend.

This package contains the official OpenAI ChatKit Python SDK integration,
including:
- PostgresStore: Store interface implementation for PostgreSQL
- TaskChatServer: ChatKitServer subclass with MCP integration
- middleware: Authentication and context extraction
"""

from app.chatkit.middleware import extract_user_context
from app.chatkit.postgres_store import PostgresStore
from app.chatkit.task_server import TaskChatServer

__all__ = ["PostgresStore", "TaskChatServer", "extract_user_context"]
