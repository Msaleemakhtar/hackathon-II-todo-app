"""Test script to verify AI agent integration with MCP tools."""

import asyncio
import logging

from app.services.agent_service import agent_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agent():
    """Test AI agent with natural language task management."""
    test_user_id = "test_agent_user_001"

    print("\n" + "=" * 60)
    print("TESTING AI AGENT INTEGRATION")
    print("=" * 60 + "\n")

    # Test 1: Natural language task creation
    print("Test 1: Create task via natural language")
    print("-" * 60)
    try:
        response = await agent_service.process_message(
            user_message="Add a task: Buy groceries tomorrow",
            conversation_history=[],
            user_id=test_user_id,
        )
        print(f"✓ Agent response: {response['content']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()

    # Test 2: List tasks
    print("Test 2: List tasks via natural language")
    print("-" * 60)
    try:
        response = await agent_service.process_message(
            user_message="Show me all my tasks",
            conversation_history=[],
            user_id=test_user_id,
        )
        print(f"✓ Agent response: {response['content']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()

    # Test 3: Update task
    print("Test 3: Update task via natural language")
    print("-" * 60)
    try:
        response = await agent_service.process_message(
            user_message="Update task 1 to 'Buy groceries and cook dinner'",
            conversation_history=[],
            user_id=test_user_id,
        )
        print(f"✓ Agent response: {response['content']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()

    print("=" * 60)
    print("AI AGENT INTEGRATION TEST COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_agent())
