"""Unit tests for Task data model."""

import re

from src.models.task import Task


def test_task_dataclass_instantiation():
    """Test Task dataclass can be instantiated with all fields."""
    task = Task(
        id=1,
        title="Buy groceries",
        description="Milk and eggs",
        completed=False,
        created_at="2025-12-04T10:15:30.123456Z",
        updated_at="2025-12-04T10:15:30.123456Z",
    )

    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk and eggs"
    assert task.completed is False
    assert task.created_at == "2025-12-04T10:15:30.123456Z"
    assert task.updated_at == "2025-12-04T10:15:30.123456Z"


def test_task_generate_timestamp_format():
    """Test Task.generate_timestamp() returns ISO 8601 format with microseconds."""
    timestamp = Task.generate_timestamp()

    # Pattern: YYYY-MM-DDTHH:MM:SS.ffffffZ
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
    assert re.match(pattern, timestamp), f"Timestamp {timestamp} does not match ISO 8601 format"


def test_task_timestamp_utc_timezone():
    """Test timestamp uses UTC timezone (Z suffix)."""
    timestamp = Task.generate_timestamp()
    assert timestamp.endswith("Z"), f"Timestamp {timestamp} should end with 'Z' for UTC"


def test_task_equality():
    """Test two tasks with same data are equal."""
    task1 = Task(
        id=1,
        title="Test",
        description="",
        completed=False,
        created_at="2025-12-04T10:00:00.000000Z",
        updated_at="2025-12-04T10:00:00.000000Z",
    )
    task2 = Task(
        id=1,
        title="Test",
        description="",
        completed=False,
        created_at="2025-12-04T10:00:00.000000Z",
        updated_at="2025-12-04T10:00:00.000000Z",
    )

    assert task1 == task2


def test_task_repr():
    """Test Task has string representation."""
    task = Task(
        id=1,
        title="Test",
        description="",
        completed=False,
        created_at="2025-12-04T10:00:00.000000Z",
        updated_at="2025-12-04T10:00:00.000000Z",
    )

    repr_str = repr(task)
    assert "Task" in repr_str
    assert "id=1" in repr_str
