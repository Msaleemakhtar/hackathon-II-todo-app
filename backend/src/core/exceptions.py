"""Custom exceptions for the application."""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception with error code support."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception with detail and code."""
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code
