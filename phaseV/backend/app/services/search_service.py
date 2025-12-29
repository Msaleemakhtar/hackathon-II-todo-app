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

    Args:
        session: Database session
        user_id: User ID
        query: Search query string
        limit: Maximum number of results (default: 50, max: 100)

    Returns:
        List of tasks ranked by relevance
    """
    # Sanitize and validate limit
    limit = min(max(1, limit), 100)

    # Prepare search query for ts_query (convert spaces to AND operator)
    # This allows multi-word searches where all words must be present
    search_terms = query.strip().split()
    if not search_terms:
        return []

    # Build tsquery: "word1 & word2 & word3"
    tsquery_str = " & ".join(search_terms)

    # Execute full-text search with ranking
    # ts_rank returns relevance score (higher = more relevant)
    stmt = (
        select(
            TaskPhaseIII,
            func.ts_rank(TaskPhaseIII.search_vector, func.to_tsquery("english", tsquery_str)).label(
                "rank"
            ),
        )
        .where(
            TaskPhaseIII.user_id == user_id,
            TaskPhaseIII.search_vector.op("@@")(func.to_tsquery("english", tsquery_str)),
        )
        .order_by(text("rank DESC"))
        .limit(limit)
    )

    result = await session.execute(stmt)
    rows = result.all()

    # Extract tasks and update search_rank
    tasks = []
    for task, rank in rows:
        task.search_rank = rank
        tasks.append(task)

    logger.info(f"search_tasks: user={user_id}, query='{query}', results={len(tasks)}")

    return tasks


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
