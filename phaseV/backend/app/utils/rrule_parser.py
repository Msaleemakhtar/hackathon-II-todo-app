"""
RRULE (Recurrence Rule) validation utility using python-dateutil.

This module provides validation for iCalendar RRULE format strings.
The RRULE format is defined in RFC 5545 (iCalendar).

Example valid RRULEs:
- FREQ=DAILY
- FREQ=WEEKLY;BYDAY=MO,WE,FR
- FREQ=MONTHLY;BYMONTHDAY=15
- FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25
"""

from datetime import datetime

from dateutil.rrule import rrulestr


def validate_rrule(rule_string: str) -> tuple[bool, str]:
    """
    Validate an iCalendar RRULE format string.

    Args:
        rule_string: The RRULE string to validate (e.g., "FREQ=DAILY")

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if the RRULE is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_rrule("FREQ=DAILY")
        (True, "")

        >>> validate_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        (True, "")

        >>> validate_rrule("INVALID")
        (False, "Invalid recurrence pattern. Examples: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,WE,FR")
    """
    if not rule_string or len(rule_string.strip()) == 0:
        return False, "Recurrence rule cannot be empty"

    try:
        # Parse RRULE with a reference date
        # rrulestr requires DTSTART, so we provide one
        dtstart = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        rrulestr(f"DTSTART:{dtstart}\nRRULE:{rule_string}")
        return True, ""
    except (ValueError, AttributeError) as e:
        return (
            False,
            f"Invalid recurrence pattern. Examples: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,WE,FR. Error: {str(e)}",
        )


def is_valid_rrule(rule_string: str) -> bool:
    """
    Check if an RRULE string is valid.

    Args:
        rule_string: The RRULE string to validate

    Returns:
        True if valid, False otherwise

    This is a convenience function that returns only the boolean result.
    Use validate_rrule() if you need the error message.
    """
    is_valid, _ = validate_rrule(rule_string)
    return is_valid


def validate_rrule_and_generate_next(
    rule_string: str, start_date: datetime
) -> tuple[bool, str, datetime | None]:
    """
    Validate an RRULE and generate the next occurrence after the start date.

    Args:
        rule_string: The RRULE string to validate
        start_date: The reference start date for the recurrence

    Returns:
        Tuple of (is_valid, error_message, next_occurrence)
        - is_valid: True if the RRULE is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
        - next_occurrence: The next occurrence datetime, or None if invalid/no more occurrences

    Examples:
        >>> start = datetime(2025, 1, 1, 10, 0)
        >>> validate_rrule_and_generate_next("FREQ=DAILY", start)
        (True, "", datetime(2025, 1, 2, 10, 0))

        >>> validate_rrule_and_generate_next("FREQ=WEEKLY;BYDAY=MO", start)
        (True, "", datetime(2025, 1, 6, 10, 0))  # Next Monday
    """
    # First validate the RRULE
    is_valid, error = validate_rrule(rule_string)
    if not is_valid:
        return False, error, None

    try:
        # Parse RRULE with the actual start date
        dtstart_str = start_date.strftime("%Y%m%dT%H%M%SZ")
        rrule = rrulestr(f"DTSTART:{dtstart_str}\nRRULE:{rule_string}")

        # Get the next occurrence after start_date
        next_occurrence = rrule.after(start_date, inc=False)

        return True, "", next_occurrence

    except (ValueError, AttributeError) as e:
        return False, f"Failed to generate next occurrence: {str(e)}", None
