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

import logging
import re
from datetime import datetime, timezone
from typing import Optional

from dateutil.rrule import rrulestr

logger = logging.getLogger(__name__)

# Whitelist of allowed RRULE patterns (simple patterns for MVP)
ALLOWED_RRULE_PATTERNS = [
    r"^FREQ=DAILY(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Daily recurrence
    r"^FREQ=WEEKLY(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Weekly (any day)
    r"^FREQ=WEEKLY;BYDAY=[A-Z,]+(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Weekly with specific days
    r"^FREQ=MONTHLY(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Monthly (any day)
    r"^FREQ=MONTHLY;BYMONTHDAY=\d+(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Monthly by day
    r"^FREQ=MONTHLY;BYDAY=[+-]?\d[A-Z]{2}(;COUNT=\d+)?(;INTERVAL=\d+)?$",  # Monthly by weekday
    r"^FREQ=YEARLY(;COUNT=\d+)?$",  # Yearly (any day/month)
    r"^FREQ=YEARLY;BYMONTH=\d+;BYMONTHDAY=\d+(;COUNT=\d+)?$",  # Yearly with specific date
]

# Natural language to RRULE translation mapping
NATURAL_LANGUAGE_TO_RRULE = {
    # Simple frequencies
    "daily": "FREQ=DAILY",
    "weekly": "FREQ=WEEKLY",
    "monthly": "FREQ=MONTHLY",
    "yearly": "FREQ=YEARLY",
    "annually": "FREQ=YEARLY",

    # Phrases
    "every day": "FREQ=DAILY",
    "every week": "FREQ=WEEKLY",
    "every month": "FREQ=MONTHLY",
    "every year": "FREQ=YEARLY",

    # Intervals
    "every 2 days": "FREQ=DAILY;INTERVAL=2",
    "every two days": "FREQ=DAILY;INTERVAL=2",
    "every 2 weeks": "FREQ=WEEKLY;INTERVAL=2",
    "every two weeks": "FREQ=WEEKLY;INTERVAL=2",
    "biweekly": "FREQ=WEEKLY;INTERVAL=2",

    # Weekdays
    "every monday": "FREQ=WEEKLY;BYDAY=MO",
    "every tuesday": "FREQ=WEEKLY;BYDAY=TU",
    "every wednesday": "FREQ=WEEKLY;BYDAY=WE",
    "every thursday": "FREQ=WEEKLY;BYDAY=TH",
    "every friday": "FREQ=WEEKLY;BYDAY=FR",
    "every saturday": "FREQ=WEEKLY;BYDAY=SA",
    "every sunday": "FREQ=WEEKLY;BYDAY=SU",
    "mondays": "FREQ=WEEKLY;BYDAY=MO",
    "tuesdays": "FREQ=WEEKLY;BYDAY=TU",
    "wednesdays": "FREQ=WEEKLY;BYDAY=WE",
    "thursdays": "FREQ=WEEKLY;BYDAY=TH",
    "fridays": "FREQ=WEEKLY;BYDAY=FR",
    "saturdays": "FREQ=WEEKLY;BYDAY=SA",
    "sundays": "FREQ=WEEKLY;BYDAY=SU",

    # Common combinations
    "weekdays": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    "weekends": "FREQ=WEEKLY;BYDAY=SA,SU",
    "every weekday": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    "every weekend": "FREQ=WEEKLY;BYDAY=SA,SU",
    "every monday and friday": "FREQ=WEEKLY;BYDAY=MO,FR",
    "every monday and wednesday": "FREQ=WEEKLY;BYDAY=MO,WE",
    "every tuesday and thursday": "FREQ=WEEKLY;BYDAY=TU,TH",
    "monday wednesday friday": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
    "mon wed fri": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
}


def translate_natural_language_to_rrule(natural_input: str) -> str:
    """
    Translate natural language recurrence pattern to RFC 5545 RRULE format.

    Args:
        natural_input: Natural language recurrence pattern (e.g., "Daily", "Every Monday")

    Returns:
        RFC 5545 RRULE format string (e.g., "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO")
        If no translation found, returns the input unchanged.

    Examples:
        >>> translate_natural_language_to_rrule("Daily")
        'FREQ=DAILY'

        >>> translate_natural_language_to_rrule("Every Monday")
        'FREQ=WEEKLY;BYDAY=MO'

        >>> translate_natural_language_to_rrule("FREQ=DAILY")  # Already RRULE format
        'FREQ=DAILY'
    """
    if not natural_input:
        return natural_input

    # Normalize input for matching
    normalized = natural_input.strip().lower()

    # Check if already in RRULE format (starts with FREQ=)
    if normalized.startswith("freq="):
        logger.debug(f"Input already in RRULE format: {natural_input}")
        return natural_input.strip().upper()

    # Try exact match in translation dictionary
    if normalized in NATURAL_LANGUAGE_TO_RRULE:
        translated = NATURAL_LANGUAGE_TO_RRULE[normalized]
        logger.info(f"Translated '{natural_input}' → '{translated}'")
        return translated

    # No translation found - return original input
    logger.debug(f"No translation found for: {natural_input}")
    return natural_input.strip()


def validate_rrule(rule_string: str) -> tuple[bool, str]:
    """
    Validate an iCalendar RRULE format string against whitelist.

    Supports both natural language (e.g., "Daily", "Weekly") and RFC 5545 format (e.g., "FREQ=DAILY").

    Args:
        rule_string: The RRULE string to validate (can be natural language or RFC 5545 format)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if the RRULE is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_rrule("FREQ=DAILY")
        (True, "")

        >>> validate_rrule("Daily")  # Natural language
        (True, "")

        >>> validate_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        (True, "")

        >>> validate_rrule("Every Monday")  # Natural language
        (True, "")

        >>> validate_rrule("INVALID")
        (False, "Invalid recurrence pattern...")
    """
    if not rule_string or len(rule_string.strip()) == 0:
        return False, "Recurrence rule cannot be empty"

    # NEW: Translate natural language to RRULE format
    translated_rule = translate_natural_language_to_rrule(rule_string)

    # Normalize: remove whitespace, convert to uppercase
    rule_normalized = translated_rule.strip().upper()

    # Check if matches any allowed pattern
    matched_pattern = False
    for pattern in ALLOWED_RRULE_PATTERNS:
        if re.match(pattern, rule_normalized):
            matched_pattern = True
            break

    if not matched_pattern:
        logger.warning(f"RRULE not in whitelist (original: {rule_string}, translated: {translated_rule})")
        return (
            False,
            (
                "Recurrence pattern not recognized. "
                "Supported natural language: Daily, Weekly, Monthly, Every Monday, Weekdays. "
                "Or RFC 5545 format: FREQ=DAILY, FREQ=WEEKLY;BYDAY=MO,WE,FR, "
                "FREQ=MONTHLY;BYMONTHDAY=15, FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"
            ),
        )

    try:
        # Also validate with dateutil to ensure RFC 5545 compliance
        rrulestr(rule_normalized, dtstart=datetime.now(timezone.utc))
        return True, ""
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"RRULE validation failed (original: {rule_string}, translated: {translated_rule}) - {e}")
        return (
            False,
            f"Invalid recurrence pattern. Supported: Daily, Weekly, Monthly, or RFC 5545 format. Error: {str(e)}",
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


def get_next_occurrence(
    rule: str, from_date: Optional[datetime] = None, base_due_date: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate the next occurrence of a recurring task.

    Args:
        rule: iCalendar RRULE string
        from_date: Start date for calculation (defaults to now)
        base_due_date: Original due_date of the completed task (used as dtstart)

    Returns:
        Next occurrence datetime (UTC) or None if invalid/no future occurrences
    """
    is_valid, error = validate_rrule(rule)
    if not is_valid:
        logger.error(f"Invalid RRULE: {rule} - {error}")
        return None

    try:
        # Use base_due_date as dtstart if provided, otherwise use from_date
        dtstart = base_due_date or from_date or datetime.now(timezone.utc)

        # Ensure dtstart is timezone-aware (UTC)
        if dtstart.tzinfo is None:
            dtstart = dtstart.replace(tzinfo=timezone.utc)

        # Parse RRULE
        rrule = rrulestr(rule, dtstart=dtstart)

        # Calculate next occurrence after dtstart
        next_date = rrule.after(dtstart, inc=False)

        if next_date is None:
            logger.info(f"No more occurrences for RRULE: {rule}")
            return None

        # Ensure next_date is timezone-aware (UTC)
        if next_date.tzinfo is None:
            next_date = next_date.replace(tzinfo=timezone.utc)

        # Skip if next occurrence is in the past
        now = datetime.now(timezone.utc)
        if next_date < now:
            logger.warning(f"Next occurrence is in the past: {next_date} (rule: {rule})")
            return None

        return next_date

    except (ValueError, TypeError, AttributeError) as e:
        logger.error(f"Failed to calculate next occurrence for RRULE '{rule}': {e}")
        return None


def parse_rrule_for_display(rule: str) -> str:
    """
    Convert RRULE to human-readable format for display.

    Args:
        rule: iCalendar RRULE string

    Returns:
        Human-readable recurrence description
    """
    if not rule:
        return "No recurrence"

    try:
        # Simple pattern matching for common cases
        if "FREQ=DAILY" in rule:
            if "INTERVAL=2" in rule:
                return "Every 2 days"
            return "Daily"
        elif "FREQ=WEEKLY" in rule:
            if "BYDAY=" in rule:
                days_match = re.search(r"BYDAY=([A-Z,]+)", rule)
                if days_match:
                    days = days_match.group(1).split(",")
                    day_names = {
                        "MO": "Monday",
                        "TU": "Tuesday",
                        "WE": "Wednesday",
                        "TH": "Thursday",
                        "FR": "Friday",
                        "SA": "Saturday",
                        "SU": "Sunday",
                    }
                    readable_days = ", ".join(day_names.get(d, d) for d in days)
                    return f"Weekly on {readable_days}"
            return "Weekly"
        elif "FREQ=MONTHLY" in rule:
            if "BYMONTHDAY=" in rule:
                day_match = re.search(r"BYMONTHDAY=(\d+)", rule)
                if day_match:
                    day = day_match.group(1)
                    return f"Monthly on day {day}"
            return "Monthly"
        elif "FREQ=YEARLY" in rule:
            return "Yearly"

        return rule  # Fallback to raw RRULE
    except Exception:
        return rule
