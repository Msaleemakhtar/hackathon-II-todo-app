"""Task service layer for business logic."""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.task import TaskPhaseIII


class TaskService:
    """Service for task CRUD operations."""

    def __init__(self, session: AsyncSession):
        """Initialize task service with database session."""
        self.session = session

    async def create_task(
        self, user_id: str, title: str, description: str | None = None
    ) -> TaskPhaseIII:
        """
        Create a new task.

        Args:
            user_id: User ID from JWT token
            title: Task title (1-200 characters)
            description: Optional task description (≤1000 characters)

        Returns:
            Created task object
        """
        task = TaskPhaseIII(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def list_tasks(
        self, user_id: str, status: str = "all"
    ) -> list[TaskPhaseIII]:
        """
        List tasks for a user with optional status filter.

        Args:
            user_id: User ID from JWT token
            status: Filter by status ("all", "pending", "completed")

        Returns:
            List of tasks
        """
        query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(~TaskPhaseIII.completed)
        elif status == "completed":
            query = query.where(TaskPhaseIII.completed)

        # Order by creation date (newest first)
        query = query.order_by(TaskPhaseIII.created_at.desc())

        result = await self.session.exec(query)
        tasks = result.all()

        return list(tasks)

    async def get_task(self, user_id: str, task_id: int) -> TaskPhaseIII | None:
        """
        Get a single task by ID (with user ownership check).

        Args:
            user_id: User ID from JWT token
            task_id: Task ID

        Returns:
            Task object if found and owned by user, None otherwise
        """
        query = select(TaskPhaseIII).where(
            TaskPhaseIII.id == task_id, TaskPhaseIII.user_id == user_id
        )

        result = await self.session.exec(query)
        task = result.first()

        return task

    async def complete_task(self, user_id: str, task_id: int) -> TaskPhaseIII | None:
        """
        Mark a task as completed.

        Args:
            user_id: User ID from JWT token
            task_id: Task ID

        Returns:
            Updated task if found, None if not found
        """
        task = await self.get_task(user_id, task_id)

        if not task:
            return None

        task.completed = True
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, user_id: str, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            user_id: User ID from JWT token
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        task = await self.get_task(user_id, task_id)

        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()

        return True

    async def update_task(
        self,
        user_id: str,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> TaskPhaseIII | None:
        """
        Update task fields.

        Args:
            user_id: User ID from JWT token
            task_id: Task ID
            title: Optional new title
            description: Optional new description

        Returns:
            Updated task if found, None if not found
        """
        task = await self.get_task(user_id, task_id)

        if not task:
            return None

        # Update provided fields
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        task.updated_at = datetime.utcnow()

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task
