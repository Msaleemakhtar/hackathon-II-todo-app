"""Search service layer for Phase V full-text keyword search."""

import logging

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.task import TaskPhaseIII

logger = logging.getLogger(__name__)


async def search_tasks(
    session: AsyncSession, user_id: str, query: str, limit: int = 50
) -> list[TaskPhaseIII]:
    """
    Search tasks using PostgreSQL full-text search with ranking.

    Implements T040-T047:
    - T041: Full-text search query using PostgreSQL tsvector and plainto_tsquery
    - T042: Result ranking with ts_rank (title matches weighted higher)
    - T043: Empty query handling (return all tasks)
    - T044: No-match handling (return empty array)
    - T045: Query length validation (reject queries >500 characters)
    - T047: Result limit (50 tasks) for performance

    Args:
        session: Database session
        user_id: User ID
        query: Search query string
        limit: Maximum number of results (default: 50)

    Returns:
        List of tasks ranked by relevance
    """
    try:
        # T045: Implement query length validation (reject queries >500 characters)
        if query and len(query) > 500:
            logger.warning(f"Search query too long ({len(query)} characters), rejecting")
            return []  # T044: Return empty array

        # T043: Implement empty query handling (return all tasks)
        if not query or query.strip() == "":
            logger.info(f"Empty search query for user {user_id}, returning all tasks")
            stmt = (
                select(TaskPhaseIII)
                .where(TaskPhaseIII.user_id == user_id)
                .order_by(TaskPhaseIII.created_at.desc())
                .limit(limit)  # T047: Add result limit
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            return list(tasks)

        # T041: Full-text search query using PostgreSQL tsvector and plainto_tsquery
        # plainto_tsquery handles natural language queries better than to_tsquery
        tsquery = func.plainto_tsquery("english", query)

        # T042: Result ranking with ts_rank (title matches weighted higher)
        # search_vector is auto-updated by database trigger with weighted content:
        # - Title has weight 'A' (highest)
        # - Description has weight 'B'
        stmt = (
            select(
                TaskPhaseIII,
                func.ts_rank(TaskPhaseIII.search_vector, tsquery).label("rank"),
            )
            .where(
                TaskPhaseIII.user_id == user_id,
                TaskPhaseIII.search_vector.op("@@")(tsquery),  # Full-text match operator
            )
            .order_by(text("rank DESC"))  # Order by relevance (highest first)
            .limit(limit)  # T047: Add result limit (50 tasks)
        )

        result = await session.execute(stmt)
        rows = result.all()

        # Extract tasks and update search_rank
        tasks = []
        for task, rank in rows:
            task.search_rank = rank
            tasks.append(task)

        logger.info(f"search_tasks: user={user_id}, query='{query}', results={len(tasks)}")

        # T044: No-match handling (return empty array if no results)
        return tasks

    except Exception as e:
        logger.error(f"Search query failed: {e}", exc_info=True)
        return []  # T044: Return empty array on error


def validate_search_query(query: str) -> tuple[bool, str]:
    """
    Validate search query.

    Args:
        query: Search query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or len(query.strip()) == 0:
        return False, "Search query cannot be empty"

    if len(query) > 200:
        return False, "Search query must be 200 characters or less"

    # Basic validation: at least one alphanumeric character
    if not any(c.isalnum() for c in query):
        return False, "Search query must contain at least one alphanumeric character"

    return True, ""
