"""Tests for database models."""
import pytest
from datetime import datetime

from app.models.task import TaskPhaseIII
from app.models.conversation import Conversation
from app.models.message import Message


@pytest.mark.asyncio
async def test_task_creation(test_session):
    """Test creating a TaskPhaseIII model."""
    task = TaskPhaseIII(
        user_id="test_user_123",
        title="Test Task",
        description="Test description",
        completed=False
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.id is not None
    assert task.user_id == "test_user_123"
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.completed is False
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


@pytest.mark.asyncio
async def test_task_without_description(test_session):
    """Test creating a task without description."""
    task = TaskPhaseIII(
        user_id="test_user_123",
        title="Test Task",
        completed=False
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.id is not None
    assert task.description is None


@pytest.mark.asyncio
async def test_conversation_creation(test_session):
    """Test creating a Conversation model."""
    conversation = Conversation(
        user_id="test_user_123"
    )

    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)

    assert conversation.id is not None
    assert conversation.user_id == "test_user_123"
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


@pytest.mark.asyncio
async def test_message_creation(test_session):
    """Test creating a Message model."""
    # First create a conversation
    conversation = Conversation(user_id="test_user_123")
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)

    # Then create a message
    message = Message(
        conversation_id=conversation.id,
        user_id="test_user_123",
        role="user",
        content="Hello, AI!"
    )

    test_session.add(message)
    await test_session.commit()
    await test_session.refresh(message)

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.user_id == "test_user_123"
    assert message.role == "user"
    assert message.content == "Hello, AI!"
    assert isinstance(message.created_at, datetime)


@pytest.mark.asyncio
async def test_multiple_tasks_for_user(test_session):
    """Test creating multiple tasks for the same user."""
    tasks = [
        TaskPhaseIII(user_id="test_user_123", title=f"Task {i}", completed=False)
        for i in range(3)
    ]

    for task in tasks:
        test_session.add(task)

    await test_session.commit()

    # Verify all tasks were created
    for task in tasks:
        await test_session.refresh(task)
        assert task.id is not None
