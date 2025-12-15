"""Task data model."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique integer identifier (sequential, starts at 1)
        title: Task title (1-200 characters, required)
        description: Optional description (0-1000 characters)
        completed: Completion status (default: False)
        created_at: UTC timestamp when task was created (ISO 8601)
        updated_at: UTC timestamp of last modification (ISO 8601)
    """

    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    @staticmethod
    def generate_timestamp() -> str:
        """Generate current UTC timestamp in ISO 8601 format.

        Returns:
            Timestamp string in format: YYYY-MM-DDTHH:MM:SS.ffffffZ
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
