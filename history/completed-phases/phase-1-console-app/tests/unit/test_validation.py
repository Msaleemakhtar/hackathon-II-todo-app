"""Unit tests for validation functions."""

from src.constants import (
    ERROR_DESCRIPTION_TOO_LONG,
    ERROR_TITLE_REQUIRED,
    ERROR_TITLE_TOO_LONG,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
)
from src.ui.prompts import validate_description, validate_title


class TestTitleValidation:
    """Tests for validate_title() function."""

    def test_validate_title_valid(self):
        """Valid title (1-200 chars) returns (True, None)."""
        is_valid, error = validate_title("Buy groceries")
        assert is_valid is True
        assert error is None

    def test_validate_title_empty(self):
        """Empty string title returns (False, ERROR 001)."""
        is_valid, error = validate_title("")
        assert is_valid is False
        assert error == ERROR_TITLE_REQUIRED

    def test_validate_title_whitespace_only(self):
        """Whitespace-only title returns (False, ERROR 001)."""
        is_valid, error = validate_title("   ")
        assert is_valid is False
        assert error == ERROR_TITLE_REQUIRED

    def test_validate_title_one_char(self):
        """Title with 1 char passes validation."""
        is_valid, error = validate_title("A")
        assert is_valid is True
        assert error is None

    def test_validate_title_200_chars(self):
        """Title with exactly 200 chars passes validation."""
        title = "A" * 200
        is_valid, error = validate_title(title)
        assert is_valid is True
        assert error is None

    def test_validate_title_201_chars(self):
        """Title with 201 chars returns (False, ERROR 002)."""
        title = "A" * 201
        is_valid, error = validate_title(title)
        assert is_valid is False
        assert error == ERROR_TITLE_TOO_LONG

    def test_validate_title_strips_whitespace(self):
        """Title with leading/trailing spaces gets stripped before validation."""
        is_valid, error = validate_title("  Valid Title  ")
        assert is_valid is True
        assert error is None

    def test_validate_title_preserves_internal_whitespace(self):
        """Title preserves internal whitespace."""
        title = "Buy  groceries  today"
        is_valid, error = validate_title(title)
        assert is_valid is True


class TestDescriptionValidation:
    """Tests for validate_description() function."""

    def test_validate_description_valid(self):
        """Valid description returns (True, None)."""
        is_valid, error = validate_description("Get milk and eggs")
        assert is_valid is True
        assert error is None

    def test_validate_description_empty(self):
        """Empty description returns (True, None)."""
        is_valid, error = validate_description("")
        assert is_valid is True
        assert error is None

    def test_validate_description_1000_chars(self):
        """Description with exactly 1000 chars passes validation."""
        description = "A" * 1000
        is_valid, error = validate_description(description)
        assert is_valid is True
        assert error is None

    def test_validate_description_1001_chars(self):
        """Description with 1001 chars returns (False, ERROR 003)."""
        description = "A" * 1001
        is_valid, error = validate_description(description)
        assert is_valid is False
        assert error == ERROR_DESCRIPTION_TOO_LONG

    def test_validate_description_strips_whitespace(self):
        """Description with leading/trailing spaces gets stripped."""
        is_valid, error = validate_description("  Valid description  ")
        assert is_valid is True
        assert error is None

    def test_validate_description_preserves_internal_whitespace(self):
        """Description preserves internal whitespace."""
        description = "Get  milk  and  eggs"
        is_valid, error = validate_description(description)
        assert is_valid is True


class TestBoundaryConditions:
    """Boundary condition tests for validation."""

    def test_title_exactly_at_max_length(self):
        """Title exactly at MAX_TITLE_LENGTH (200) is valid."""
        title = "X" * MAX_TITLE_LENGTH
        is_valid, error = validate_title(title)
        assert is_valid is True

    def test_title_one_over_max_length(self):
        """Title at MAX_TITLE_LENGTH + 1 (201) is invalid."""
        title = "X" * (MAX_TITLE_LENGTH + 1)
        is_valid, error = validate_title(title)
        assert is_valid is False

    def test_description_exactly_at_max_length(self):
        """Description exactly at MAX_DESCRIPTION_LENGTH (1000) is valid."""
        description = "X" * MAX_DESCRIPTION_LENGTH
        is_valid, error = validate_description(description)
        assert is_valid is True

    def test_description_one_over_max_length(self):
        """Description at MAX_DESCRIPTION_LENGTH + 1 (1001) is invalid."""
        description = "X" * (MAX_DESCRIPTION_LENGTH + 1)
        is_valid, error = validate_description(description)
        assert is_valid is False
