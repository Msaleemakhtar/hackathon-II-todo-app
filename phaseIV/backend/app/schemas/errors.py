from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    code: str
    field: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid authentication credentials",
                "code": "UNAUTHORIZED",
                "field": None,
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""

    detail: str
    code: str
    field: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Title is required and must be 1-200 characters",
                "code": "INVALID_TITLE",
                "field": "title",
            }
        }


# Error codes enum for consistency
class ErrorCode:
    """Standard error codes."""

    # Authentication errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    USER_ID_MISMATCH = "USER_ID_MISMATCH"

    # Validation errors
    INVALID_TITLE = "INVALID_TITLE"
    INVALID_MESSAGE = "INVALID_MESSAGE"

    # Resource errors
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_ACCESS_DENIED = "CONVERSATION_ACCESS_DENIED"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # AI service errors
    AI_SERVICE_UNAVAILABLE = "AI_SERVICE_UNAVAILABLE"
