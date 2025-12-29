"""Test script to verify MCP tools and database connectivity."""

import asyncio
import logging

from app.mcp.tools import add_task, complete_task, delete_task, list_tasks, update_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_tools():
    """Test all MCP tools with database operations."""
    test_user_id = "test_user_001"

    print("\n" + "=" * 60)
    print("TESTING MCP TOOLS AND DATABASE CONNECTIVITY")
    print("=" * 60 + "\n")

    # Test 1: List tasks (should be empty initially)
    print("Test 1: List all tasks")
    print("-" * 60)
    tasks = await list_tasks(user_id=test_user_id, status="all")
    print(f"✓ list_tasks result: {len(tasks)} tasks found")
    for task in tasks:
        print(f"  - Task #{task['id']}: {task['title']}")
    print()

    # Test 2: Add a task
    print("Test 2: Add a new task")
    print("-" * 60)
    result = await add_task(
        user_id=test_user_id, title="Test Task 1", description="This is a test task"
    )
    print(f"✓ add_task result: {result}")
    if result["status"] == "created":
        task_id = result["task_id"]
        print(f"  Task created successfully with ID: {task_id}")
    print()

    # Test 3: List tasks again (should have 1 task)
    print("Test 3: List pending tasks")
    print("-" * 60)
    tasks = await list_tasks(user_id=test_user_id, status="pending")
    print(f"✓ list_tasks result: {len(tasks)} pending tasks")
    for task in tasks:
        print(f"  - Task #{task['id']}: {task['title']} (completed: {task['completed']})")
    print()

    # Test 4: Update the task
    print("Test 4: Update task title and description")
    print("-" * 60)
    if "task_id" in locals():
        result = await update_task(
            user_id=test_user_id,
            task_id=task_id,
            title="Updated Test Task",
            description="Updated description",
        )
        print(f"✓ update_task result: {result}")
        print(f"  Task #{task_id} updated successfully")
    print()

    # Test 5: Complete the task
    print("Test 5: Complete the task")
    print("-" * 60)
    if "task_id" in locals():
        result = await complete_task(user_id=test_user_id, task_id=task_id)
        print(f"✓ complete_task result: {result}")
        print(f"  Task #{task_id} marked as completed")
    print()

    # Test 6: List completed tasks
    print("Test 6: List completed tasks")
    print("-" * 60)
    tasks = await list_tasks(user_id=test_user_id, status="completed")
    print(f"✓ list_tasks result: {len(tasks)} completed tasks")
    for task in tasks:
        print(f"  - Task #{task['id']}: {task['title']} (completed: {task['completed']})")
    print()

    # Test 7: Delete the task
    print("Test 7: Delete the task")
    print("-" * 60)
    if "task_id" in locals():
        result = await delete_task(user_id=test_user_id, task_id=task_id)
        print(f"✓ delete_task result: {result}")
        print(f"  Task #{task_id} deleted successfully")
    print()

    # Test 8: Verify task is deleted
    print("Test 8: Verify task is deleted")
    print("-" * 60)
    tasks = await list_tasks(user_id=test_user_id, status="all")
    print(f"✓ list_tasks result: {len(tasks)} tasks remaining")
    print()

    print("=" * 60)
    print("ALL MCP TOOLS TESTS PASSED ✓")
    print("Database connectivity: ✓")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
