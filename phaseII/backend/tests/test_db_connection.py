"""Simple test to verify database connection with PostgreSQL."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import User


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test that we can connect to the database and run a simple query."""
    # Run a simple query to test the connection
    result = await db_session.execute(select(User).limit(1))
    users = result.scalars().all()
    
    # This test passes if no exception is raised during connection
    # The result may be empty if there are no users, which is fine
    assert True  # Connection successful if we get here