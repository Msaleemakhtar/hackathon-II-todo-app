"""Timezone utilities for handling UTC datetimes consistently."""
from datetime import datetime, timezone


def get_utc_now():
    """
    Get the current UTC time as a timezone-aware datetime and return
    it as a naive datetime that represents UTC time.

    This ensures consistent UTC handling by returning a naive datetime
    that represents the current UTC time, which when stored in the
    properly configured database, will be interpreted correctly.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)