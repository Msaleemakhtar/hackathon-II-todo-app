#!/usr/bin/env python3
"""Test TaskUpdatedEvent schema fix.

This test verifies that TaskUpdatedEvent can be created with the correct
schema (updated_fields as a dict) and validates the fix for the background
loop crash issue.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.kafka.events import TaskUpdatedEvent


def test_correct_schema():
    """Test TaskUpdatedEvent creation with correct schema."""
    print("Testing TaskUpdatedEvent with correct schema (updated_fields dict)...")

    try:
        event = TaskUpdatedEvent(
            user_id=1,
            task_id=100,
            updated_fields={
                "title": "Updated Task Title",
                "priority": "high",
                "completed": True,
            },
        )

        print(f"✅ Event created successfully")
        print(f"   - Event ID: {event.event_id}")
        print(f"   - Event Type: {event.event_type}")
        print(f"   - Task ID: {event.task_id}")
        print(f"   - Updated Fields: {event.updated_fields}")
        print(f"   - Timestamp: {event.timestamp}")

        # Verify schema
        assert event.event_type == "task.updated", "Event type should be 'task.updated'"
        assert isinstance(
            event.updated_fields, dict
        ), "updated_fields should be a dict"
        assert (
            event.updated_fields["title"] == "Updated Task Title"
        ), "Title should match"
        assert event.updated_fields["priority"] == "high", "Priority should match"
        assert event.updated_fields["completed"] is True, "Completed should match"

        print("✅ All schema validations passed")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_empty_updated_fields():
    """Test TaskUpdatedEvent with empty updated_fields dict."""
    print("\nTesting TaskUpdatedEvent with empty updated_fields...")

    try:
        event = TaskUpdatedEvent(
            user_id=1,
            task_id=101,
            updated_fields={},
        )

        print(f"✅ Event created successfully with empty updated_fields")
        print(f"   - Event ID: {event.event_id}")
        print(f"   - Updated Fields: {event.updated_fields}")

        assert event.updated_fields == {}, "Updated fields should be empty dict"
        print("✅ Empty updated_fields validation passed")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_json_serialization():
    """Test that TaskUpdatedEvent can be serialized to JSON."""
    print("\nTesting TaskUpdatedEvent JSON serialization...")

    try:
        event = TaskUpdatedEvent(
            user_id=1,
            task_id=102,
            updated_fields={
                "title": "Test Task",
                "description": "Test Description",
                "priority": "medium",
            },
        )

        # Serialize to JSON
        event_json = event.model_dump_json()
        print(f"✅ Event serialized to JSON successfully")
        print(f"   JSON: {event_json[:100]}...")

        # Verify it's valid JSON
        import json

        parsed = json.loads(event_json)
        assert "updated_fields" in parsed, "JSON should contain updated_fields"
        assert parsed["updated_fields"]["title"] == "Test Task"
        print("✅ JSON serialization validation passed")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all schema validation tests."""
    print("=" * 70)
    print("TaskUpdatedEvent Schema Validation Tests")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Correct Schema Test", test_correct_schema()))
    results.append(("Empty Updated Fields Test", test_empty_updated_fields()))
    results.append(("JSON Serialization Test", test_json_serialization()))

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All tests passed! Schema fix is working correctly.")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
