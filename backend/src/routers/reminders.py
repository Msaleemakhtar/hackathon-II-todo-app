"""API router for reminder management endpoints using user_id in path."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.schemas.reminder import ReminderCreate, ReminderRead, ReminderUpdate
from src.services.notification_service import NotificationService

router = APIRouter()


@router.get("/{user_id}/reminders", response_model=List[ReminderRead])
async def list_reminders(
    user_id: str,
    request: Request,
    upcoming_only: bool = Query(
        True,
        description="Only return upcoming reminders (not yet sent)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get all reminders for a user.

    **User Story 1 (P1)**: User can view their reminders.

    Args:
        user_id: ID of the user
        request: FastAPI request object (contains auth user)
        upcoming_only: Whether to include only upcoming reminders
        db: Database session

    Returns:
        List of reminders

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Get reminders using notification service
    notification_service = NotificationService(db)
    reminders = await notification_service.get_all(
        user_id=user_id,
        include_sent=not upcoming_only
    )

    return reminders


@router.post("/{user_id}/reminders", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    user_id: str,
    reminder_data: ReminderCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new reminder for a task.

    **User Story 1 (P1)**: User can set reminders for tasks.

    Args:
        user_id: ID of the user
        reminder_data: Reminder creation data
        request: FastAPI request object (contains auth user)
        db: Database session

    Returns:
        Created reminder

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 400 if validation fails
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Create reminder using notification service
    notification_service = NotificationService(db)
    try:
        reminder = await notification_service.create(
            user_id=user_id,
            task_id=reminder_data.task_id,
            remind_at=reminder_data.remind_at,
            channel=reminder_data.channel,
            message=reminder_data.message
        )
        return reminder
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}/reminders/{reminder_id}", response_model=ReminderRead)
async def get_reminder(
    user_id: str,
    reminder_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific reminder by ID.

    Args:
        user_id: ID of the user
        reminder_id: ID of the reminder
        request: FastAPI request object (contains auth user)
        db: Database session

    Returns:
        Reminder details

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if reminder not found
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Get reminder using notification service
    notification_service = NotificationService(db)
    reminder = await notification_service.get(reminder_id, user_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )

    return reminder


@router.put("/{user_id}/reminders/{reminder_id}", response_model=ReminderRead)
async def update_reminder(
    user_id: str,
    reminder_id: int,
    reminder_data: ReminderUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing reminder.

    Args:
        user_id: ID of the user
        reminder_id: ID of the reminder
        reminder_data: Updated reminder data
        request: FastAPI request object (contains auth user)
        db: Database session

    Returns:
        Updated reminder

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if reminder not found
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Get reminder using notification service
    notification_service = NotificationService(db)
    reminder = await notification_service.get(reminder_id, user_id)

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )

    # Update reminder fields
    if reminder_data.remind_at is not None:
        reminder.remind_at = reminder_data.remind_at
    if reminder_data.channel is not None:
        reminder.channel = reminder_data.channel
    if reminder_data.message is not None:
        reminder.message = reminder_data.message
    if reminder_data.snoozed_until is not None:
        reminder.snoozed_until = reminder_data.snoozed_until

    # Commit changes
    await db.commit()
    await db.refresh(reminder)

    return reminder


@router.delete("/{user_id}/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    user_id: str,
    reminder_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete a reminder.

    Args:
        user_id: ID of the user
        reminder_id: ID of the reminder
        request: FastAPI request object (contains auth user)
        db: Database session

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if reminder not found
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Delete reminder using notification service
    notification_service = NotificationService(db)
    deleted = await notification_service.cancel(reminder_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )


@router.post("/{user_id}/reminders/{reminder_id}/snooze", response_model=ReminderRead)
async def snooze_reminder(
    user_id: str,
    reminder_id: int,
    request: Request,
    minutes: int = Query(15, description="Number of minutes to snooze", ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
):
    """Snooze a reminder for a specified number of minutes.

    **User Story 1 (P1)**: User can snooze reminders.

    Args:
        user_id: ID of the user
        reminder_id: ID of the reminder
        request: FastAPI request object (contains auth user)
        minutes: Number of minutes to snooze (1-1440, default: 15)
        db: Database session

    Returns:
        Updated reminder with new remind_at time

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if reminder not found
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Snooze reminder using notification service
    notification_service = NotificationService(db)
    reminder = await notification_service.snooze(
        reminder_id,
        user_id,
        snooze_minutes=minutes
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder {reminder_id} not found"
        )

    return reminder
