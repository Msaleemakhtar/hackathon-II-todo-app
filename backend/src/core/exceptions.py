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


class TaskNotFoundException(AppException):
    """Exception raised when a task is not found."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
            code="TASK_NOT_FOUND",
        )


class TagNotFoundException(AppException):
    """Exception raised when a tag is not found."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
            code="TAG_NOT_FOUND",
        )


class TagAlreadyExistsException(AppException):
    """Exception raised when a tag with the same name already exists."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A tag with this name already exists",
            code="TAG_ALREADY_EXISTS",
        )


class InvalidPaginationException(AppException):
    """Exception raised when pagination parameters are invalid."""

    def __init__(self, detail: str = "Page and limit must be positive integers"):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code="INVALID_PAGINATION",
        )


class InvalidStatusException(AppException):
    """Exception raised when status filter value is invalid."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: all, not_started, pending, in_progress, completed",
            code="INVALID_STATUS",
        )


class InvalidSortFieldException(AppException):
    """Exception raised when sort field is invalid."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sort field must be one of: due_date, priority, created_at, title",
            code="INVALID_SORT_FIELD",
        )


class CategoryNotFoundException(AppException):
    """Exception raised when a category is not found."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
            code="CATEGORY_NOT_FOUND",
        )


class CategoryAlreadyExistsException(AppException):
    """Exception raised when a category with the same name and type already exists."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this name and type already exists",
            code="CATEGORY_ALREADY_EXISTS",
        )


class CannotDeleteDefaultCategoryException(AppException):
    """Exception raised when attempting to delete a default category."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default categories",
            code="CANNOT_DELETE_DEFAULT_CATEGORY",
        )


class CategoryInUseException(AppException):
    """Exception raised when attempting to delete a category that is in use."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category that is in use by tasks",
            code="CATEGORY_IN_USE",
        )


class InvalidCategoryValueException(AppException):
    """Exception raised when a task uses an invalid category value."""

    def __init__(self, category_type: str, value: str):
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {category_type}: '{value}'. Must match one of your defined {category_type} categories.",
            code="INVALID_CATEGORY_VALUE",
        )
