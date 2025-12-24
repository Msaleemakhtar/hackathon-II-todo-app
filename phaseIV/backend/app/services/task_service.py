"""Task service with CRUD operations for TaskPhaseIII."""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.task import TaskPhaseIII

logger = logging.getLogger(__name__)


class TaskService:
    """Service layer for task management operations."""

    @staticmethod
    async def create_task(
        db: AsyncSession,
        user_id: str,
        title: str,
        description: str | None = None,
    ) -> TaskPhaseIII:
        """Create a new task."""
        task = TaskPhaseIII(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task created: task_id={task.id}, user_id={user_id}")
        return task

    @staticmethod
    async def get_task(
        db: AsyncSession,
        task_id: int,
        user_id: str,
    ) -> TaskPhaseIII | None:
        """Get a task by ID (with user ownership validation)."""
        task = await db.get(TaskPhaseIII, task_id)
        if task and task.user_id == user_id:
            return task
        return None

    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        user_id: str,
        status: str = "all",
    ) -> list[TaskPhaseIII]:
        """List tasks with optional status filter."""
        query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

        if status == "pending":
            query = query.where(TaskPhaseIII.completed.is_(False))
        elif status == "completed":
            query = query.where(TaskPhaseIII.completed.is_(True))

        query = query.order_by(TaskPhaseIII.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> TaskPhaseIII | None:
        """Update a task."""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        task.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task updated: task_id={task_id}, user_id={user_id}")
        return task

    @staticmethod
    async def complete_task(
        db: AsyncSession,
        task_id: int,
        user_id: str,
    ) -> TaskPhaseIII | None:
        """Mark a task as completed."""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return None

        task.completed = True
        task.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        logger.info(f"Task completed: task_id={task_id}, user_id={user_id}")
        return task

    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: int,
        user_id: str,
    ) -> bool:
        """Delete a task."""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return False

        await db.delete(task)
        await db.commit()
        logger.info(f"Task deleted: task_id={task_id}, user_id={user_id}")
        return True


# Global service instance
task_service = TaskService()
