"""MCP-specific schemas for error responses and tool schemas."""

from pydantic import BaseModel


class MCPError(BaseModel):
    """Standard MCP error response format."""

    detail: str
    code: str
    field: str | None = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "detail": "Title is required and must be 1-200 characters",
                    "code": "INVALID_TITLE",
                    "field": "title"
                },
                {
                    "detail": "Task not found",
                    "code": "TASK_NOT_FOUND"
                },
                {
                    "detail": "Database connection failed",
                    "code": "DATABASE_ERROR"
                }
            ]
        }


class MCPToolResponse(BaseModel):
    """Base class for MCP tool success responses."""

    status: str

    class Config:
        from_attributes = True
