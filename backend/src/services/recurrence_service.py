"""
Recurrence service for handling recurring tasks using iCal RRULE format.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from dateutil.rrule import rrulestr, rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.task import Task, TaskCreate


class RecurrenceService:
    """Service for managing recurring tasks and generating task instances."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def expand_recurring_task(
        self,
        task_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Task]:
        """
        Generate task instances from a recurring task's RRULE within a date range.

        Args:
            task_id: The parent recurring task ID
            start_date: Start of date range (defaults to today)
            end_date: End of date range (defaults to 90 days from start)

        Returns:
            List of generated task instances
        """
        # Fetch the parent recurring task
        result = await self.session.exec(
            select(Task).where(Task.id == task_id)
        )
        parent_task = result.first()

        if not parent_task:
            raise ValueError(f"Task with id {task_id} not found")

        if not parent_task.recurrence_rule:
            raise ValueError(f"Task {task_id} is not a recurring task")

        # Set default date range: today to 90 days from now
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = start_date + timedelta(days=90)

        # Parse RRULE and generate occurrences
        occurrences = self._generate_occurrences(
            parent_task.recurrence_rule,
            start_date,
            end_date,
            dtstart=parent_task.due_date or start_date
        )

        # Create task instances for each occurrence
        created_instances = []
        for occurrence_date in occurrences:
            # Check if instance already exists for this date
            existing = await self._get_existing_instance(task_id, occurrence_date)
            if existing:
                created_instances.append(existing)
                continue

            # Create new task instance
            instance = Task(
                title=parent_task.title,
                description=parent_task.description,
                priority=parent_task.priority,
                status=parent_task.status,
                user_id=parent_task.user_id,
                parent_task_id=task_id,
                is_recurring_instance=True,
                occurrence_date=occurrence_date,
                due_date=occurrence_date,
                recurrence_rule=None,  # Instances don't have their own recurrence
            )

            self.session.add(instance)
            created_instances.append(instance)

        await self.session.commit()

        # Refresh instances to get their IDs
        for instance in created_instances:
            await self.session.refresh(instance)

        return created_instances

    async def get_next_occurrence(
        self,
        task_id: int,
        after_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date for a recurring task.

        Args:
            task_id: The recurring task ID
            after_date: Calculate next occurrence after this date (defaults to now)

        Returns:
            The next occurrence date, or None if no more occurrences
        """
        result = await self.session.exec(
            select(Task).where(Task.id == task_id)
        )
        task = result.first()

        if not task or not task.recurrence_rule:
            return None

        if after_date is None:
            after_date = datetime.now()

        dtstart = task.due_date or after_date
        occurrences = self._generate_occurrences(
            task.recurrence_rule,
            after_date,
            after_date + timedelta(days=365),  # Look ahead 1 year max
            dtstart=dtstart,
            count=1
        )

        return occurrences[0] if occurrences else None

    async def update_recurrence_pattern(
        self,
        task_id: int,
        rrule_string: str
    ) -> Task:
        """
        Update a task's recurrence pattern and regenerate future instances.

        Args:
            task_id: The recurring task ID
            rrule_string: The new RRULE string

        Returns:
            The updated task
        """
        result = await self.session.exec(
            select(Task).where(Task.id == task_id)
        )
        task = result.first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Validate RRULE
        try:
            self._parse_rrule(rrule_string, dtstart=datetime.now())
        except Exception as e:
            raise ValueError(f"Invalid RRULE: {str(e)}")

        # Update the recurrence rule
        task.recurrence_rule = rrule_string
        self.session.add(task)

        # Delete future instances (keep completed ones)
        await self._delete_future_instances(task_id)

        await self.session.commit()
        await self.session.refresh(task)

        # Generate new instances
        await self.expand_recurring_task(task_id)

        return task

    async def delete_recurring_series(self, task_id: int) -> None:
        """
        Delete a recurring task and all its instances.

        Args:
            task_id: The parent recurring task ID
        """
        # Delete all instances
        result = await self.session.exec(
            select(Task).where(Task.parent_task_id == task_id)
        )
        instances = result.all()

        for instance in instances:
            await self.session.delete(instance)

        # Delete parent task
        result = await self.session.exec(
            select(Task).where(Task.id == task_id)
        )
        parent = result.first()
        if parent:
            await self.session.delete(parent)

        await self.session.commit()

    async def delete_instance_and_following(
        self,
        instance_id: int
    ) -> None:
        """
        Delete a specific instance and all following instances.

        Args:
            instance_id: The task instance ID
        """
        result = await self.session.exec(
            select(Task).where(Task.id == instance_id)
        )
        instance = result.first()

        if not instance or not instance.is_recurring_instance:
            raise ValueError("Task is not a recurring instance")

        # Delete this instance and all following instances
        result = await self.session.exec(
            select(Task).where(
                Task.parent_task_id == instance.parent_task_id,
                Task.occurrence_date >= instance.occurrence_date
            )
        )
        instances = result.all()

        for inst in instances:
            await self.session.delete(inst)

        await self.session.commit()

    # Helper methods

    def _generate_occurrences(
        self,
        rrule_string: str,
        start_date: datetime,
        end_date: datetime,
        dtstart: datetime,
        count: Optional[int] = None
    ) -> List[datetime]:
        """Generate occurrence dates from an RRULE string."""
        try:
            # Parse the RRULE
            rule = self._parse_rrule(rrule_string, dtstart)

            # Generate occurrences within the date range
            if count:
                occurrences = list(rule[:count])
            else:
                occurrences = list(rule.between(start_date, end_date, inc=True))

            return occurrences
        except Exception as e:
            raise ValueError(f"Failed to parse RRULE: {str(e)}")

    def _parse_rrule(self, rrule_string: str, dtstart: datetime):
        """Parse an RRULE string into a dateutil.rrule object."""
        # If it's a full RRULE string (starts with RRULE:)
        if rrule_string.startswith("RRULE:"):
            return rrulestr(rrule_string, dtstart=dtstart)
        else:
            # Assume it's just the rule part without RRULE: prefix
            return rrulestr(f"RRULE:{rrule_string}", dtstart=dtstart)

    async def _get_existing_instance(
        self,
        parent_task_id: int,
        occurrence_date: datetime
    ) -> Optional[Task]:
        """Check if a task instance already exists for a given date."""
        # Compare dates only (ignore time)
        occurrence_day = occurrence_date.replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.session.exec(
            select(Task).where(
                Task.parent_task_id == parent_task_id,
                Task.occurrence_date >= occurrence_day,
                Task.occurrence_date < occurrence_day + timedelta(days=1)
            )
        )
        return result.first()

    async def _delete_future_instances(self, parent_task_id: int) -> None:
        """Delete all future (not completed) instances of a recurring task."""
        now = datetime.now()
        result = await self.session.exec(
            select(Task).where(
                Task.parent_task_id == parent_task_id,
                Task.occurrence_date >= now,
                Task.status != "completed"
            )
        )
        instances = result.all()

        for instance in instances:
            await self.session.delete(instance)


def create_rrule_string(
    frequency: str,
    interval: int = 1,
    days_of_week: Optional[List[int]] = None,
    day_of_month: Optional[int] = None,
    end_date: Optional[datetime] = None,
    count: Optional[int] = None
) -> str:
    """
    Helper function to create an RRULE string from human-readable parameters.

    Args:
        frequency: One of 'daily', 'weekly', 'monthly', 'yearly'
        interval: Repeat every N periods (e.g., every 2 weeks)
        days_of_week: For weekly: list of weekdays (0=Monday, 6=Sunday)
        day_of_month: For monthly: day of the month (1-31)
        end_date: Stop repeating after this date
        count: Stop after N occurrences

    Returns:
        RRULE string
    """
    freq_map = {
        'daily': 'DAILY',
        'weekly': 'WEEKLY',
        'monthly': 'MONTHLY',
        'yearly': 'YEARLY'
    }

    if frequency.lower() not in freq_map:
        raise ValueError(f"Invalid frequency: {frequency}")

    parts = [f"FREQ={freq_map[frequency.lower()]}"]

    if interval > 1:
        parts.append(f"INTERVAL={interval}")

    if days_of_week and frequency.lower() == 'weekly':
        # Convert to iCal format (MO, TU, WE, TH, FR, SA, SU)
        day_names = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
        days_str = ','.join([day_names[d] for d in days_of_week if 0 <= d <= 6])
        if days_str:
            parts.append(f"BYDAY={days_str}")

    if day_of_month and frequency.lower() == 'monthly':
        parts.append(f"BYMONTHDAY={day_of_month}")

    if end_date:
        # Format: YYYYMMDDTHHMMSSZ
        end_str = end_date.strftime("%Y%m%dT%H%M%SZ")
        parts.append(f"UNTIL={end_str}")
    elif count:
        parts.append(f"COUNT={count}")

    return ';'.join(parts)
