# Complete Feature Specification - Remaining Implementation
**Project:** Todo App - Advanced Features & Optimization
**Date:** 2025-12-13
**Status:** Ready for Implementation
**Estimated Duration:** 2-3 weeks

---

## Table of Contents
1. [Phase 1.2 - Time Reminders & Notifications](#phase-12-time-reminders--notifications)
2. [Phase 2 - Performance Optimization](#phase-2-performance-optimization)
3. [Phase 3 - UX Enhancements](#phase-3-ux-enhancements)
4. [Phase 4 - Monitoring & Analytics](#phase-4-monitoring--analytics)

---

# Phase 1.2 - Time Reminders & Notifications

## Overview
Enable users to set reminders for tasks and receive notifications via browser push notifications and email fallback.

## 1.1 Database Schema

### Reminder Model
**File:** `backend/src/models/reminder.py`

```python
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import Field, Relationship, SQLModel

class ReminderBase(SQLModel):
    task_id: int = Field(foreign_key="tasks.id", ondelete="CASCADE", index=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    remind_at: datetime = Field(index=True)
    channel: str = Field(max_length=20)  # "browser", "email", or "both"
    is_sent: bool = Field(default=False, index=True)
    sent_at: Optional[datetime] = None
    message: Optional[str] = Field(default=None, max_length=500)
    snoozed_until: Optional[datetime] = None

class Reminder(ReminderBase, table=True):
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="reminders")
    user: "User" = Relationship(back_populates="reminders")

class ReminderRead(ReminderBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ReminderCreate(SQLModel):
    task_id: int
    remind_at: datetime
    channel: str = "browser"
    message: Optional[str] = None

class ReminderUpdate(SQLModel):
    remind_at: Optional[datetime] = None
    channel: Optional[str] = None
    message: Optional[str] = None
    snoozed_until: Optional[datetime] = None
```

### Migration
**File:** `backend/alembic/versions/xxx_add_reminders_table.py`

```python
def upgrade():
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('message', sa.String(length=500), nullable=True),
        sa.Column('snoozed_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('ix_reminders_remind_at', 'reminders', ['remind_at'])
    op.create_index('ix_reminders_is_sent', 'reminders', ['is_sent'])
    op.create_index('ix_reminders_pending', 'reminders', ['is_sent', 'remind_at'])
```

## 1.2 Backend Implementation

### Notification Service
**File:** `backend/src/services/notification_service.py`

```python
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import aiosmtplib
from email.message import EmailMessage

from ..models.reminder import Reminder, ReminderCreate
from ..models.task import Task
from ..core.config import settings

class NotificationService:
    """Service for managing task reminders and notifications."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reminder(
        self,
        reminder_data: ReminderCreate,
        user_id: str
    ) -> Reminder:
        """Create a new reminder for a task."""
        # Validate task exists and belongs to user
        task_result = await self.session.exec(
            select(Task).where(Task.id == reminder_data.task_id, Task.user_id == user_id)
        )
        task = task_result.first()
        if not task:
            raise ValueError(f"Task {reminder_data.task_id} not found for user {user_id}")

        # Create reminder
        reminder = Reminder(
            **reminder_data.model_dump(),
            user_id=user_id
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def get_pending_reminders(
        self,
        before: Optional[datetime] = None
    ) -> List[Reminder]:
        """Get all pending reminders that should be sent."""
        if before is None:
            before = datetime.utcnow()

        stmt = select(Reminder).where(
            Reminder.is_sent == False,
            Reminder.remind_at <= before,
            (Reminder.snoozed_until == None) | (Reminder.snoozed_until <= before)
        )
        result = await self.session.exec(stmt)
        return result.all()

    async def get_user_reminders(
        self,
        user_id: str,
        upcoming_only: bool = True
    ) -> List[Reminder]:
        """Get reminders for a specific user."""
        stmt = select(Reminder).where(Reminder.user_id == user_id)

        if upcoming_only:
            stmt = stmt.where(
                Reminder.is_sent == False,
                Reminder.remind_at > datetime.utcnow()
            )

        stmt = stmt.order_by(Reminder.remind_at)
        result = await self.session.exec(stmt)
        return result.all()

    async def mark_as_sent(self, reminder_id: int) -> Reminder:
        """Mark a reminder as sent."""
        result = await self.session.exec(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = result.first()
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        reminder.is_sent = True
        reminder.sent_at = datetime.utcnow()
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def snooze_reminder(
        self,
        reminder_id: int,
        minutes: int
    ) -> Reminder:
        """Snooze a reminder for specified minutes."""
        result = await self.session.exec(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = result.first()
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        reminder.snoozed_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def cancel_reminder(self, reminder_id: int, user_id: str) -> None:
        """Cancel (delete) a reminder."""
        result = await self.session.exec(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            )
        )
        reminder = result.first()
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        await self.session.delete(reminder)
        await self.session.commit()

    async def send_browser_notification(self, reminder: Reminder) -> bool:
        """
        Send browser push notification.
        Note: Requires web push setup with VAPID keys.
        """
        # This is a placeholder - actual implementation requires:
        # 1. pywebpush library
        # 2. VAPID keys configured
        # 3. User's push subscription stored in database

        # For now, we'll log the notification
        print(f"[BROWSER PUSH] Reminder {reminder.id}: {reminder.message}")
        return True

    async def send_email_notification(self, reminder: Reminder) -> bool:
        """Send email notification using SMTP."""
        try:
            # Get task details
            task_result = await self.session.exec(
                select(Task).where(Task.id == reminder.task_id)
            )
            task = task_result.first()
            if not task:
                return False

            # Get user email
            from ..models.user import User
            user_result = await self.session.exec(
                select(User).where(User.id == reminder.user_id)
            )
            user = user_result.first()
            if not user or not user.email:
                return False

            # Create email
            msg = EmailMessage()
            msg['Subject'] = f'Task Reminder: {task.title}'
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = user.email

            body = f"""
Hello {user.name or 'there'},

This is a reminder about your task:

Task: {task.title}
{f'Description: {task.description}' if task.description else ''}
Priority: {task.priority}
Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}

{reminder.message or 'Stay on track with your tasks!'}

Best regards,
Todo App Team
            """
            msg.set_content(body)

            # Send email
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )

            return True
        except Exception as e:
            print(f"Error sending email notification: {str(e)}")
            return False


async def process_pending_reminders(session: AsyncSession):
    """
    Background task to process pending reminders.
    Should be called by a scheduler (e.g., APScheduler) every minute.
    """
    service = NotificationService(session)
    pending = await service.get_pending_reminders()

    for reminder in pending:
        try:
            success = False

            if reminder.channel in ['browser', 'both']:
                success = await service.send_browser_notification(reminder)

            if reminder.channel in ['email', 'both'] or (reminder.channel == 'browser' and not success):
                success = await service.send_email_notification(reminder)

            if success:
                await service.mark_as_sent(reminder.id)
        except Exception as e:
            print(f"Error processing reminder {reminder.id}: {str(e)}")
```

### Background Worker Setup
**File:** `backend/src/workers/scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel.ext.asyncio.session import AsyncSession
from ..core.database import get_db
from ..services.notification_service import process_pending_reminders

scheduler = AsyncIOScheduler()

async def reminder_job():
    """Job to process reminders every minute."""
    async with get_db() as session:
        await process_pending_reminders(session)

def start_scheduler():
    """Start the background scheduler."""
    # Run every minute
    scheduler.add_job(reminder_job, 'interval', minutes=1, id='process_reminders')
    scheduler.start()
    print("Reminder scheduler started")

def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    print("Reminder scheduler stopped")
```

**Update main.py:**
```python
from contextlib import asynccontextmanager
from .workers.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
```

### API Endpoints
**File:** `backend/src/routers/reminders.py`

```python
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.models.reminder import ReminderCreate, ReminderRead, ReminderUpdate
from src.services.notification_service import NotificationService

router = APIRouter()

@router.post(
    "/{user_id}/reminders",
    response_model=ReminderRead,
    status_code=status.HTTP_201_CREATED
)
async def create_reminder(
    user_id: str,
    request: Request,
    reminder_data: ReminderCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new reminder for a task."""
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    service = NotificationService(db)
    reminder = await service.create_reminder(reminder_data, current_user_id)
    return reminder

@router.get(
    "/{user_id}/reminders",
    response_model=List[ReminderRead]
)
async def list_reminders(
    user_id: str,
    request: Request,
    upcoming_only: bool = Query(True, description="Only show upcoming reminders"),
    db: AsyncSession = Depends(get_db),
):
    """Get all reminders for the authenticated user."""
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    service = NotificationService(db)
    reminders = await service.get_user_reminders(current_user_id, upcoming_only)
    return reminders

@router.post(
    "/{user_id}/reminders/{reminder_id}/snooze",
    response_model=ReminderRead
)
async def snooze_reminder(
    user_id: str,
    reminder_id: int,
    request: Request,
    minutes: int = Query(15, ge=1, le=1440, description="Snooze duration in minutes"),
    db: AsyncSession = Depends(get_db),
):
    """Snooze a reminder for specified minutes."""
    await validate_path_user_id(request, user_id, db)

    service = NotificationService(db)
    reminder = await service.snooze_reminder(reminder_id, minutes)
    return reminder

@router.delete(
    "/{user_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_reminder(
    user_id: str,
    reminder_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Cancel/delete a reminder."""
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    service = NotificationService(db)
    await service.cancel_reminder(reminder_id, current_user_id)
```

### Environment Configuration
**Update `backend/.env.example`:**
```bash
# SMTP Configuration for Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@todoapp.com
SMTP_USE_TLS=true

# Web Push Configuration (for browser notifications)
VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_CLAIMS={"sub": "mailto:admin@todoapp.com"}
```

## 1.3 Frontend Implementation

### Notification Hook
**File:** `frontend/src/hooks/useNotifications.ts`

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';

export interface Reminder {
  id: number;
  task_id: number;
  remind_at: string;
  channel: 'browser' | 'email' | 'both';
  is_sent: boolean;
  message?: string;
  snoozed_until?: string;
}

export function useNotifications() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Request browser notification permission
  const requestPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        toast.success('Browser notifications enabled');
        return true;
      } else if (permission === 'denied') {
        toast.error('Browser notifications blocked. Please enable in settings.');
        return false;
      }
    } else {
      toast.error('Browser notifications not supported');
      return false;
    }
  };

  // Get user reminders
  const { data: reminders, isLoading } = useQuery({
    queryKey: ['reminders', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      const response = await apiClient.get<Reminder[]>(
        `/v1/${user.id}/reminders?upcoming_only=true`
      );
      return response.data;
    },
    enabled: !!user?.id,
    staleTime: 30 * 1000, // 30 seconds
  });

  // Create reminder
  const createReminder = useMutation({
    mutationFn: async (data: {
      task_id: number;
      remind_at: Date;
      channel: 'browser' | 'email' | 'both';
      message?: string;
    }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post<Reminder>(
        `/v1/${user.id}/reminders`,
        {
          task_id: data.task_id,
          remind_at: data.remind_at.toISOString(),
          channel: data.channel,
          message: data.message,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
      toast.success('Reminder set successfully');
    },
    onError: () => {
      toast.error('Failed to set reminder');
    },
  });

  // Snooze reminder
  const snoozeReminder = useMutation({
    mutationFn: async ({ reminderId, minutes }: { reminderId: number; minutes: number }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post<Reminder>(
        `/v1/${user.id}/reminders/${reminderId}/snooze?minutes=${minutes}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
      toast.success('Reminder snoozed');
    },
    onError: () => {
      toast.error('Failed to snooze reminder');
    },
  });

  // Delete reminder
  const deleteReminder = useMutation({
    mutationFn: async (reminderId: number) => {
      if (!user?.id) throw new Error('User not authenticated');
      await apiClient.delete(`/v1/${user.id}/reminders/${reminderId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
      toast.success('Reminder cancelled');
    },
    onError: () => {
      toast.error('Failed to cancel reminder');
    },
  });

  return {
    reminders: reminders || [],
    isLoading,
    requestPermission,
    createReminder: createReminder.mutateAsync,
    snoozeReminder: snoozeReminder.mutateAsync,
    deleteReminder: deleteReminder.mutateAsync,
  };
}
```

### Notification Bell Component
**File:** `frontend/src/components/notifications/NotificationBell.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Bell } from 'lucide-react';
import { useNotifications } from '@/hooks/useNotifications';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { formatDistanceToNow } from 'date-fns';

export function NotificationBell() {
  const { reminders, snoozeReminder, deleteReminder } = useNotifications();
  const [open, setOpen] = useState(false);

  const upcomingCount = reminders.filter(
    r => !r.is_sent && new Date(r.remind_at) > new Date()
  ).length;

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger className="relative p-2 hover:bg-gray-100 rounded-full transition-colors">
        <Bell className="h-5 w-5 text-gray-600" />
        {upcomingCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
          >
            {upcomingCount}
          </Badge>
        )}
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-80">
        <div className="p-2 border-b">
          <h3 className="font-semibold">Upcoming Reminders</h3>
        </div>

        {reminders.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            No upcoming reminders
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto">
            {reminders.map((reminder) => (
              <div
                key={reminder.id}
                className="p-3 hover:bg-gray-50 border-b last:border-b-0"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      Task Reminder
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(reminder.remind_at), {
                        addSuffix: true,
                      })}
                    </p>
                    {reminder.message && (
                      <p className="text-xs text-gray-600 mt-1">{reminder.message}</p>
                    )}
                  </div>

                  <div className="flex gap-1">
                    <button
                      onClick={() => snoozeReminder({ reminderId: reminder.id, minutes: 15 })}
                      className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200"
                    >
                      Snooze
                    </button>
                    <button
                      onClick={() => deleteReminder(reminder.id)}
                      className="text-xs px-2 py-1 rounded bg-red-100 hover:bg-red-200 text-red-600"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### Reminder Selector Component
**File:** `frontend/src/components/tasks/ReminderSelector.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Bell } from 'lucide-react';

interface ReminderSelectorProps {
  dueDate?: Date;
  onReminderSet: (reminderDate: Date, channel: 'browser' | 'email' | 'both') => void;
}

export function ReminderSelector({ dueDate, onReminderSet }: ReminderSelectorProps) {
  const [enabled, setEnabled] = useState(false);
  const [reminderTime, setReminderTime] = useState('1_hour_before');
  const [channel, setChannel] = useState<'browser' | 'email' | 'both'>('browser');
  const [customDate, setCustomDate] = useState('');

  const calculateReminderDate = (): Date => {
    const base = dueDate || new Date();

    switch (reminderTime) {
      case '5_min_before':
        return new Date(base.getTime() - 5 * 60 * 1000);
      case '15_min_before':
        return new Date(base.getTime() - 15 * 60 * 1000);
      case '1_hour_before':
        return new Date(base.getTime() - 60 * 60 * 1000);
      case '1_day_before':
        return new Date(base.getTime() - 24 * 60 * 60 * 1000);
      case 'custom':
        return customDate ? new Date(customDate) : new Date();
      default:
        return new Date(base.getTime() - 60 * 60 * 1000);
    }
  };

  const handleApply = () => {
    const reminderDate = calculateReminderDate();
    onReminderSet(reminderDate, channel);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="enable-reminder"
          checked={enabled}
          onChange={(e) => setEnabled(e.target.checked)}
          className="rounded border-gray-300"
        />
        <Label htmlFor="enable-reminder" className="flex items-center gap-2 cursor-pointer">
          <Bell className="h-4 w-4" />
          Set Reminder
        </Label>
      </div>

      {enabled && (
        <>
          <div>
            <Label htmlFor="reminder-time">Remind me</Label>
            <select
              id="reminder-time"
              value={reminderTime}
              onChange={(e) => setReminderTime(e.target.value)}
              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="5_min_before">5 minutes before</option>
              <option value="15_min_before">15 minutes before</option>
              <option value="1_hour_before">1 hour before</option>
              <option value="1_day_before">1 day before</option>
              <option value="custom">Custom time...</option>
            </select>
          </div>

          {reminderTime === 'custom' && (
            <div>
              <Label htmlFor="custom-date">Custom reminder time</Label>
              <input
                type="datetime-local"
                id="custom-date"
                value={customDate}
                onChange={(e) => setCustomDate(e.target.value)}
                className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <div>
            <Label htmlFor="channel">Notification method</Label>
            <select
              id="channel"
              value={channel}
              onChange={(e) => setChannel(e.target.value as any)}
              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="browser">Browser notification</option>
              <option value="email">Email</option>
              <option value="both">Both</option>
            </select>
          </div>

          <div className="pt-2 border-t">
            <p className="text-sm text-gray-600">
              Preview: You'll be reminded{' '}
              {reminderTime === 'custom'
                ? 'at your custom time'
                : reminderTime.replace('_', ' ')}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
```

### Service Worker for Push Notifications
**File:** `frontend/public/sw.js`

```javascript
// Service Worker for Push Notifications

self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(clients.claim());
});

self.addEventListener('push', (event) => {
  console.log('Push notification received', event);

  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Task Reminder';
  const options = {
    body: data.body || 'You have a task reminder',
    icon: '/icon-192.png',
    badge: '/badge-72.png',
    data: {
      taskId: data.taskId,
      url: data.url || '/my-tasks',
    },
    actions: [
      { action: 'view', title: 'View Task' },
      { action: 'snooze', title: 'Snooze 15min' },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'snooze') {
    // Handle snooze action
    fetch(`/api/reminders/${event.notification.data.reminderId}/snooze?minutes=15`, {
      method: 'POST',
    });
  } else {
    // Open the app
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});
```

### Update CreateTaskForm with Reminder
**Update:** `frontend/src/components/tasks/CreateTaskForm.tsx`

Add after the Recurrence section:

```typescript
import { ReminderSelector } from './ReminderSelector';
import { useNotifications } from '@/hooks/useNotifications';

// Inside component:
const { createReminder } = useNotifications();
const [reminderDate, setReminderDate] = useState<Date | null>(null);
const [reminderChannel, setReminderChannel] = useState<'browser' | 'email' | 'both'>('browser');

// In handleSubmit, after task creation:
if (reminderDate && createdTask) {
  await createReminder({
    task_id: createdTask.id,
    remind_at: reminderDate,
    channel: reminderChannel,
  });
}

// In JSX, after recurrence section:
<div className="space-y-2">
  <ReminderSelector
    dueDate={dueDate ? new Date(dueDate) : undefined}
    onReminderSet={(date, channel) => {
      setReminderDate(date);
      setReminderChannel(channel);
    }}
  />
</div>
```

## 1.4 Dependencies

### Backend
Add to `backend/requirements.txt`:
```txt
APScheduler>=3.10.0
aiosmtplib>=3.0.0
pywebpush>=1.14.0  # For browser push notifications
```

### Frontend
Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "date-fns": "^3.0.0"
  }
}
```

## 1.5 Acceptance Criteria

- [ ] User can set reminder when creating a task
- [ ] User can choose reminder time (5min, 15min, 1hr, 1day before, or custom)
- [ ] User can select notification channel (browser, email, or both)
- [ ] Browser notification appears at scheduled time (if permission granted)
- [ ] Email notification sent as fallback or when selected
- [ ] Notification bell shows count of upcoming reminders
- [ ] User can snooze notification (5min, 15min, 1hr)
- [ ] User can dismiss/cancel reminders
- [ ] Clicking notification opens task detail
- [ ] Background worker processes reminders every minute
- [ ] Performance: <100ms to fetch upcoming reminders

---

# Phase 2 - Performance Optimization

## 2.1 Backend Optimizations

### Database Indexes

**File:** `backend/alembic/versions/xxx_add_performance_indexes.py`

```python
def upgrade():
    # Task performance indexes
    op.create_index(
        'idx_tasks_user_status',
        'tasks',
        ['user_id', 'status'],
        postgresql_where=sa.text("status != 'deleted'")
    )
    op.create_index(
        'idx_tasks_user_priority',
        'tasks',
        ['user_id', 'priority']
    )
    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date'],
        postgresql_where=sa.text('due_date IS NOT NULL')
    )
    op.create_index(
        'idx_tasks_user_created',
        'tasks',
        ['user_id', sa.desc('created_at')]
    )

    # Full-text search index (PostgreSQL)
    op.execute("""
        CREATE INDEX idx_tasks_search
        ON tasks
        USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')))
    """)

    # Tag indexes
    op.create_index(
        'idx_tags_user_name',
        'tags',
        ['user_id', 'name'],
        unique=True
    )

    # Composite index for common queries
    op.create_index(
        'idx_tasks_user_status_priority',
        'tasks',
        ['user_id', 'status', 'priority']
    )
```

### Fix N+1 Queries with Eager Loading

**File:** `backend/src/services/task_service.py`

```python
from sqlmodel import selectinload

async def get_tasks(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    sort: Optional[str] = None,
) -> tuple[List[Task], int]:
    """Get tasks with eager loading to prevent N+1 queries."""

    # Base query with eager loading
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .options(selectinload(Task.tags))  # Eager load tags
        .options(selectinload(Task.category))  # Eager load category if exists
    )

    # Apply filters...
    # (rest of implementation)

    # Execute with eager loading
    result = await db.exec(stmt)
    tasks = result.all()

    return tasks, total
```

### Redis Caching Layer

**File:** `backend/src/core/cache.py`

```python
from typing import Optional, Any
import json
import redis.asyncio as redis
from functools import wraps
from .config import settings

# Redis client
redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

def cache_result(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:"
            cache_key += ":".join(str(arg) for arg in args)
            cache_key += ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            # Try to get from cache
            redis_conn = await get_redis()
            cached = await redis_conn.get(cache_key)

            if cached is not None:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_conn.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator

async def invalidate_cache(pattern: str):
    """Invalidate all cache keys matching pattern."""
    redis_conn = await get_redis()
    keys = await redis_conn.keys(pattern)
    if keys:
        await redis_conn.delete(*keys)
```

**Usage in task_service.py:**
```python
from ..core.cache import cache_result, invalidate_cache

@cache_result(ttl=60, key_prefix="tasks")
async def get_tasks(db: AsyncSession, user_id: str, **filters):
    # Implementation...
    pass

async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str):
    # Create task...

    # Invalidate cache
    await invalidate_cache(f"tasks:get_tasks:{user_id}:*")

    return task
```

### Connection Pool Tuning

**File:** `backend/src/core/config.py`

```python
class Settings(BaseSettings):
    # Database connection pool settings
    DATABASE_POOL_MIN_SIZE: int = 5  # Minimum connections
    DATABASE_POOL_MAX_SIZE: int = 20  # Maximum connections
    DATABASE_POOL_MAX_QUERIES: int = 50000  # Recycle after N queries
    DATABASE_POOL_MAX_INACTIVE: int = 300  # Close after 5min inactive
    DATABASE_POOL_TIMEOUT: int = 30  # Connection timeout

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10
```

**Update database.py:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_MIN_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX_SIZE - settings.DATABASE_POOL_MIN_SIZE,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Verify connection before use
)
```

### Response Compression

**File:** `backend/src/main.py`

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=6  # Balance between speed and compression
)
```

### Field Selection for Partial Responses

**File:** `backend/src/schemas/task.py`

```python
class TaskMinimal(SQLModel):
    """Minimal task representation for list views."""
    id: int
    title: str
    status: str
    priority: str

class TaskSummary(SQLModel):
    """Summary task representation."""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    completed: bool

class TaskFull(TaskRead):
    """Full task representation with all relationships."""
    tags: List[Tag] = []
    category: Optional[Category] = None
```

**Update router:**
```python
@router.get("/{user_id}/tasks", response_model=PaginatedTasks)
async def list_tasks(
    fields: Optional[str] = Query(None, description="Comma-separated fields to return"),
    # ... other params
):
    if fields == "minimal":
        # Return TaskMinimal
        pass
    elif fields == "summary":
        # Return TaskSummary
        pass
    else:
        # Return TaskFull
        pass
```

## 2.2 Frontend Optimizations

### Virtual Scrolling

**Install dependency:**
```bash
cd frontend && bun add @tanstack/react-virtual
```

**File:** `frontend/src/components/tasks/TaskList.tsx`

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';

export function TaskList({ tasks }: { tasks: Task[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120, // Estimated height of TaskCard
    overscan: 5, // Render 5 extra items above/below viewport
  });

  return (
    <div
      ref={parentRef}
      className="h-screen overflow-auto"
      style={{ contain: 'strict' }} // Performance optimization
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const task = tasks[virtualRow.index];
          return (
            <div
              key={virtualRow.key}
              data-index={virtualRow.index}
              ref={virtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <TaskCard task={task} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### Code Splitting & Lazy Loading

**File:** `frontend/src/app/my-tasks/page.tsx`

```typescript
import { lazy, Suspense } from 'react';
import { TaskSkeleton } from '@/components/tasks/TaskSkeleton';

// Lazy load heavy components
const TaskDetailModal = lazy(() => import('@/components/tasks/TaskDetailModal'));
const EditTaskModal = lazy(() => import('@/components/tasks/EditTaskModal'));
const CreateTaskModal = lazy(() => import('@/components/tasks/CreateTaskModal'));

export default function MyTasksPage() {
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  return (
    <>
      {/* Main content */}
      <TaskList tasks={tasks} />

      {/* Lazy loaded modals */}
      {showDetailModal && (
        <Suspense fallback={<TaskSkeleton />}>
          <TaskDetailModal task={selectedTask} onClose={() => setShowDetailModal(false)} />
        </Suspense>
      )}

      {showEditModal && (
        <Suspense fallback={<TaskSkeleton />}>
          <EditTaskModal task={selectedTask} onClose={() => setShowEditModal(false)} />
        </Suspense>
      )}
    </>
  );
}
```

### Optimize React Query Configuration

**File:** `frontend/src/hooks/useTasks.ts`

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['tasks', user?.id, debouncedSearchTerm, filters],
  queryFn: async () => {
    // Fetch logic
  },
  // Optimized configuration
  staleTime: 2 * 60 * 1000, // 2 minutes - data stays fresh
  cacheTime: 10 * 60 * 1000, // 10 minutes - keep in cache
  refetchOnWindowFocus: false, // Don't refetch on window focus
  refetchOnMount: false, // Don't refetch on mount if data exists
  keepPreviousData: true, // Smooth transitions when filtering
  retry: 1, // Only retry once on failure
  retryDelay: 1000, // Wait 1s before retry
  select: (data) => ({
    // Transform data once, not on every render
    tasks: data.items,
    total: data.total,
    hasMore: data.page < data.pages,
  }),
});
```

### Request Batching

**File:** `frontend/src/lib/api-batch.ts`

```typescript
class ApiBatcher {
  private queue: Array<{
    key: string;
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }> = [];
  private timer: NodeJS.Timeout | null = null;

  async request<T>(endpoint: string): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push({ key: endpoint, resolve, reject });

      if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), 50); // 50ms batch window
      }
    });
  }

  private async flush() {
    const batch = this.queue.splice(0);
    this.timer = null;

    if (batch.length === 0) return;

    try {
      // Single request for all batched items
      const endpoints = batch.map((b) => b.key);
      const response = await apiClient.post('/api/batch', { requests: endpoints });
      const results = response.data;

      batch.forEach((item, i) => {
        if (results[i].error) {
          item.reject(results[i].error);
        } else {
          item.resolve(results[i].data);
        }
      });
    } catch (error) {
      batch.forEach((item) => item.reject(error));
    }
  }
}

export const apiBatcher = new ApiBatcher();

// Usage
const tags = await apiBatcher.request('/api/tags');
const categories = await apiBatcher.request('/api/categories');
// Both requests combined into single HTTP call
```

### Image & Asset Optimization

**File:** `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },
  compress: true,
  swcMinify: true,
  experimental: {
    optimizeCss: true,
  },
  // Bundle analyzer (development only)
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
          lib: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              const packageName = module.context.match(
                /[\\/]node_modules[\\/](.*?)([\\/]|$)/
              )[1];
              return `npm.${packageName.replace('@', '')}`;
            },
          },
        },
      };
    }
    return config;
  },
};

module.exports = nextConfig;
```

## 2.3 Acceptance Criteria

- [ ] Database queries use appropriate indexes (verify with EXPLAIN)
- [ ] N+1 queries eliminated (max 3 queries for task list)
- [ ] Redis caching reduces DB load by 70%+
- [ ] Task list renders smoothly with 10,000+ tasks (virtual scrolling)
- [ ] Initial bundle size < 200KB gzipped
- [ ] Modal components lazy-loaded (not in initial bundle)
- [ ] API responses compressed with GZip
- [ ] Search debounced (no request until 300ms after typing stops)
- [ ] React Query cache prevents duplicate requests
- [ ] Lighthouse performance score > 90

---

# Phase 3 - UX Enhancements

## 3.1 Keyboard Shortcuts

**File:** `frontend/src/hooks/useKeyboardShortcuts.ts`

```typescript
import { useEffect } from 'react';

interface ShortcutHandlers {
  onSearch?: () => void;
  onNewTask?: () => void;
  onComplete?: () => void;
  onClose?: () => void;
  onDelete?: () => void;
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isModifier = e.metaKey || e.ctrlKey;
      const target = e.target as HTMLElement;
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName);

      // Cmd/Ctrl + K: Quick search
      if (isModifier && e.key === 'k') {
        e.preventDefault();
        handlers.onSearch?.();
      }

      // Cmd/Ctrl + N: New task
      if (isModifier && e.key === 'n' && !isInput) {
        e.preventDefault();
        handlers.onNewTask?.();
      }

      // Cmd/Ctrl + Enter: Mark complete
      if (isModifier && e.key === 'Enter') {
        e.preventDefault();
        handlers.onComplete?.();
      }

      // Escape: Close modal
      if (e.key === 'Escape') {
        handlers.onClose?.();
      }

      // Delete/Backspace: Delete selected
      if ((e.key === 'Delete' || e.key === 'Backspace') && !isInput) {
        e.preventDefault();
        handlers.onDelete?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
}

// Usage
function MyTasksPage() {
  useKeyboardShortcuts({
    onSearch: () => setSearchOpen(true),
    onNewTask: () => setCreateModalOpen(true),
    onComplete: () => selectedTask && toggleComplete(selectedTask.id),
    onClose: () => setModalOpen(false),
  });
}
```

**Keyboard Shortcuts Help Modal:**
**File:** `frontend/src/components/KeyboardShortcutsHelp.tsx`

```typescript
import { Command } from 'lucide-react';

export function KeyboardShortcutsHelp() {
  const shortcuts = [
    { keys: ['⌘', 'K'], description: 'Quick search' },
    { keys: ['⌘', 'N'], description: 'New task' },
    { keys: ['⌘', '↵'], description: 'Mark complete' },
    { keys: ['ESC'], description: 'Close modal' },
    { keys: ['⌫'], description: 'Delete selected' },
  ];

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-3 flex items-center gap-2">
        <Command className="h-4 w-4" />
        Keyboard Shortcuts
      </h3>
      <div className="space-y-2">
        {shortcuts.map((shortcut, i) => (
          <div key={i} className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{shortcut.description}</span>
            <div className="flex gap-1">
              {shortcut.keys.map((key, j) => (
                <kbd
                  key={j}
                  className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono"
                >
                  {key}
                </kbd>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 3.2 Drag & Drop Reordering

**Install dependencies:**
```bash
cd frontend && bun add @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

**File:** `frontend/src/components/tasks/DraggableTaskList.tsx`

```typescript
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical } from 'lucide-react';

function SortableTaskCard({ task }: { task: Task }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="relative">
      <div className="absolute left-2 top-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing">
        <GripVertical
          className="h-5 w-5 text-gray-400 hover:text-gray-600"
          {...attributes}
          {...listeners}
        />
      </div>
      <div className="pl-10">
        <TaskCard task={task} />
      </div>
    </div>
  );
}

export function DraggableTaskList({ tasks }: { tasks: Task[] }) {
  const [items, setItems] = useState(tasks);
  const { updateTaskOrder } = useTasks();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        const newItems = arrayMove(items, oldIndex, newIndex);

        // Persist new order to backend
        updateTaskOrder(newItems.map(item => item.id));

        return newItems;
      });
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={items} strategy={verticalListSortingStrategy}>
        <div className="space-y-2">
          {items.map((task) => (
            <SortableTaskCard key={task.id} task={task} />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
```

**Backend support for ordering:**
```python
# Add to Task model
class TaskBase(SQLModel):
    # ... existing fields
    sort_order: int = Field(default=0, index=True)

# API endpoint
@router.post("/{user_id}/tasks/reorder")
async def reorder_tasks(
    user_id: str,
    request: Request,
    task_ids: List[int],
    db: AsyncSession = Depends(get_db),
):
    """Update task order based on new positions."""
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Update sort_order for each task
    for index, task_id in enumerate(task_ids):
        result = await db.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        )
        task = result.first()
        if task:
            task.sort_order = index
            db.add(task)

    await db.commit()
```

## 3.3 PWA & Offline Support

**File:** `frontend/src/app/manifest.json`

```json
{
  "name": "Todo App - Advanced Task Management",
  "short_name": "TodoApp",
  "description": "Advanced task management with recurring tasks, reminders, and offline support",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4f46e5",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshot-1.png",
      "sizes": "1280x720",
      "type": "image/png"
    }
  ],
  "categories": ["productivity", "utilities"],
  "shortcuts": [
    {
      "name": "New Task",
      "short_name": "New",
      "description": "Create a new task",
      "url": "/my-tasks?action=new",
      "icons": [{ "src": "/icon-new.png", "sizes": "96x96" }]
    }
  ]
}
```

**Service Worker:**
**File:** `frontend/public/sw.js` (enhanced version)

```javascript
const CACHE_NAME = 'todo-app-v1';
const RUNTIME_CACHE = 'runtime-cache';

const PRECACHE_URLS = [
  '/',
  '/my-tasks',
  '/offline.html',
];

// Install - precache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// Activate - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim();
});

// Fetch - network first, then cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls: Network first, cache as fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful GET requests
          if (request.method === 'GET' && response.ok) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline fallback
          return caches.match(request).then((cached) => {
            if (cached) {
              return cached;
            }
            // Return offline page for navigation
            if (request.mode === 'navigate') {
              return caches.match('/offline.html');
            }
            return new Response('Offline', { status: 503 });
          });
        })
    );
  }
  // Static assets: Cache first
  else {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) {
          // Return cached version and update in background
          fetch(request).then((response) => {
            if (response.ok) {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(request, response);
              });
            }
          });
          return cached;
        }
        return fetch(request).then((response) => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-tasks') {
    event.waitUntil(syncTasks());
  }
});

async function syncTasks() {
  // Sync pending task updates when back online
  const pending = await getPendingUpdates();
  for (const update of pending) {
    try {
      await fetch(update.url, {
        method: update.method,
        body: JSON.stringify(update.data),
        headers: update.headers,
      });
      await removePendingUpdate(update.id);
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
}
```

**Offline Page:**
**File:** `frontend/public/offline.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Offline - Todo App</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      text-align: center;
      padding: 20px;
    }
    .container {
      max-width: 400px;
    }
    h1 { font-size: 48px; margin: 0 0 16px; }
    p { font-size: 18px; opacity: 0.9; }
    button {
      margin-top: 24px;
      padding: 12px 24px;
      font-size: 16px;
      background: white;
      color: #667eea;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    }
    button:hover { opacity: 0.9; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📴</h1>
    <h2>You're Offline</h2>
    <p>No internet connection. Your tasks are saved locally and will sync when you're back online.</p>
    <button onclick="window.location.reload()">Try Again</button>
  </div>
</body>
</html>
```

**Register Service Worker:**
**File:** `frontend/src/app/layout.tsx`

```typescript
useEffect(() => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('SW registered:', registration);
      })
      .catch((error) => {
        console.error('SW registration failed:', error);
      });
  }
}, []);
```

## 3.4 Accessibility Improvements

**File:** `frontend/src/components/tasks/TaskCard.tsx` (enhanced)

```typescript
export function TaskCard({ task }: { task: Task }) {
  return (
    <article
      role="article"
      aria-label={`Task: ${task.title}`}
      tabIndex={0}
      className="task-card"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onTaskClick(task);
        }
      }}
    >
      <header>
        <h3 id={`task-title-${task.id}`}>{task.title}</h3>
      </header>

      <button
        aria-label={`Mark task "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
        aria-pressed={task.completed}
        onClick={toggleComplete}
        className="checkbox-button"
      >
        {task.completed ? <CheckCircle2 /> : <Circle />}
      </button>

      <div role="group" aria-label="Task metadata">
        <Badge aria-label={`Priority: ${task.priority}`}>
          {task.priority}
        </Badge>
        <Badge aria-label={`Status: ${task.status}`}>
          {task.status}
        </Badge>
      </div>

      {task.due_date && (
        <time
          dateTime={task.due_date}
          aria-label={`Due date: ${formatDate(task.due_date)}`}
        >
          {formatDate(task.due_date)}
        </time>
      )}

      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {statusMessage}
      </div>
    </article>
  );
}
```

**Skip Links:**
**File:** `frontend/src/components/layout/SkipLinks.tsx`

```typescript
export function SkipLinks() {
  return (
    <div className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50">
      <a
        href="#main-content"
        className="bg-blue-600 text-white px-4 py-2 rounded-md"
      >
        Skip to main content
      </a>
      <a
        href="#task-list"
        className="bg-blue-600 text-white px-4 py-2 rounded-md ml-2"
      >
        Skip to task list
      </a>
    </div>
  );
}
```

**Focus Management:**
**File:** `frontend/src/hooks/useFocusManagement.ts`

```typescript
import { useEffect, useRef } from 'react';

export function useFocusManagement(isOpen: boolean) {
  const previousFocus = useRef<HTMLElement | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Save current focus
      previousFocus.current = document.activeElement as HTMLElement;

      // Focus modal
      modalRef.current?.focus();

      // Trap focus within modal
      const handleTabKey = (e: KeyboardEvent) => {
        if (e.key !== 'Tab') return;

        const focusableElements = modalRef.current?.querySelectorAll(
          'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
        );

        if (!focusableElements?.length) return;

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      };

      document.addEventListener('keydown', handleTabKey);

      return () => {
        document.removeEventListener('keydown', handleTabKey);
      };
    } else {
      // Restore focus when modal closes
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  return modalRef;
}
```

## 3.5 Acceptance Criteria

- [ ] Keyboard shortcuts work (Cmd+K, Cmd+N, Cmd+Enter, Esc)
- [ ] Keyboard shortcuts help accessible via "?"
- [ ] Tasks can be reordered via drag-and-drop
- [ ] Task order persisted to backend
- [ ] PWA installable on desktop and mobile
- [ ] App works offline (read-only for tasks)
- [ ] Changes sync when back online
- [ ] All interactive elements keyboard accessible
- [ ] Screen reader announces status changes
- [ ] Focus trapped in modals
- [ ] Skip links available
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] All images have alt text

---

# Phase 4 - Monitoring & Analytics

## 4.1 Performance Monitoring

**File:** `frontend/src/lib/performance.ts`

```typescript
import { getCLS, getFID, getFCP, getLCP, getTTFB, Metric } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
  });

  // Use sendBeacon if available (doesn't block page unload)
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/vitals', body);
  } else {
    fetch('/api/analytics/vitals', {
      body,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
    });
  }
}

export function initPerformanceMonitoring() {
  getCLS(sendToAnalytics);  // Cumulative Layout Shift
  getFID(sendToAnalytics);  // First Input Delay
  getFCP(sendToAnalytics);  // First Contentful Paint
  getLCP(sendToAnalytics);  // Largest Contentful Paint
  getTTFB(sendToAnalytics); // Time to First Byte
}

// Custom performance marks
export function measurePerformance(name: string, start: string, end?: string) {
  if ('performance' in window) {
    if (end) {
      performance.measure(name, start, end);
    } else {
      performance.mark(name);
    }
  }
}

// Usage
measurePerformance('task-list-start');
// ... render task list
measurePerformance('task-list-end');
measurePerformance('task-list-render', 'task-list-start', 'task-list-end');
```

**Backend Analytics Endpoint:**
```python
from pydantic import BaseModel
from datetime import datetime

class WebVital(BaseModel):
    name: str
    value: float
    rating: str
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@router.post("/analytics/vitals")
async def record_web_vital(
    vital: WebVital,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Record Core Web Vitals metrics."""
    # Store in database or send to analytics service
    # Can aggregate and alert on poor performance
    return {"status": "recorded"}
```

## 4.2 Error Tracking (Sentry)

**Install:**
```bash
# Backend
uv add sentry-sdk

# Frontend
cd frontend && bun add @sentry/nextjs
```

**Backend:**
**File:** `backend/src/main.py`

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of requests
    profiles_sample_rate=0.1,  # 10% profiling
    environment=settings.ENVIRONMENT,
    release=settings.VERSION,
    before_send=lambda event, hint: (
        event if settings.ENVIRONMENT != "development" else None
    ),
)
```

**Frontend:**
**File:** `frontend/sentry.client.config.ts`

```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  debug: false,
  environment: process.env.NODE_ENV,

  beforeSend(event, hint) {
    // Don't send errors in development
    if (process.env.NODE_ENV === 'development') {
      return null;
    }
    return event;
  },

  integrations: [
    new Sentry.BrowserTracing({
      tracePropagationTargets: ['localhost', /^https:\/\/api\.todoapp\.com/],
    }),
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

## 4.3 User Analytics

**File:** `frontend/src/lib/analytics.ts`

```typescript
// Privacy-respecting analytics using Plausible
declare global {
  interface Window {
    plausible?: (
      event: string,
      options?: { props: Record<string, any> }
    ) => void;
  }
}

export function trackEvent(
  event: string,
  properties?: Record<string, any>
) {
  if (typeof window === 'undefined') return;

  // Plausible
  if (window.plausible) {
    window.plausible(event, { props: properties });
  }

  // Custom analytics endpoint
  if (properties?.userId) {
    fetch('/api/analytics/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event,
        properties,
        timestamp: new Date().toISOString(),
      }),
    }).catch(() => {
      // Fail silently
    });
  }
}

// Predefined events
export const analytics = {
  taskCreated: (priority: string, hasTags: boolean) =>
    trackEvent('Task Created', { priority, hasTags }),

  taskCompleted: (timeTaken: number) =>
    trackEvent('Task Completed', { timeTaken }),

  recurringTaskCreated: (frequency: string) =>
    trackEvent('Recurring Task Created', { frequency }),

  reminderSet: (channel: string, timeBefore: string) =>
    trackEvent('Reminder Set', { channel, timeBefore }),

  searchPerformed: (resultsCount: number) =>
    trackEvent('Search Performed', { resultsCount }),

  filterApplied: (filterType: string, value: string) =>
    trackEvent('Filter Applied', { filterType, value }),
};
```

**Plausible Script:**
Add to `frontend/src/app/layout.tsx`:

```typescript
<Script
  defer
  data-domain="todoapp.com"
  src="https://plausible.io/js/script.js"
/>
```

## 4.4 Acceptance Criteria

- [ ] Core Web Vitals tracked and reported
- [ ] Performance metrics visible in dashboard
- [ ] Sentry captures frontend errors with source maps
- [ ] Sentry captures backend errors with context
- [ ] Error alerts sent for critical issues
- [ ] User analytics tracks key events (task creation, completion, etc.)
- [ ] Analytics dashboard shows feature usage
- [ ] Privacy policy updated for analytics
- [ ] GDPR-compliant (no PII tracked)
- [ ] Analytics can be disabled by user

---

# Implementation Dependencies

## Backend Dependencies

Add to `backend/requirements.txt`:
```txt
# Performance & Caching
redis>=5.0.0
aiocache>=0.12.0

# Background Jobs
APScheduler>=3.10.0

# Email
aiosmtplib>=3.0.0

# Monitoring
sentry-sdk>=1.40.0

# Push Notifications
pywebpush>=1.14.0
```

## Frontend Dependencies

Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "@tanstack/react-virtual": "^3.0.0",
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.1",
    "web-vitals": "^3.5.0",
    "@sentry/nextjs": "^7.99.0",
    "date-fns": "^3.0.0"
  }
}
```

---

# Testing Strategy

## Unit Tests
- [ ] RecurrenceService tests (RRULE parsing, expansion)
- [ ] NotificationService tests (reminder scheduling)
- [ ] Cache service tests
- [ ] Component unit tests (RecurrenceSelector, ReminderSelector)

## Integration Tests
- [ ] Recurring task creation and expansion
- [ ] Reminder scheduling and delivery
- [ ] Drag-and-drop task reordering
- [ ] Offline mode and sync
- [ ] Performance benchmarks

## E2E Tests
- [ ] Create recurring task flow
- [ ] Set reminder flow
- [ ] Keyboard navigation
- [ ] PWA installation
- [ ] Cross-browser testing

---

# Deployment Checklist

- [ ] Environment variables configured
- [ ] Redis server running
- [ ] Database migrations applied
- [ ] SMTP configured for emails
- [ ] Sentry configured
- [ ] Service worker registered
- [ ] PWA icons generated
- [ ] SSL certificate valid
- [ ] CDN configured for static assets
- [ ] Background worker running
- [ ] Health check endpoint
- [ ] Monitoring dashboards set up
- [ ] Backup strategy in place

---

# Success Metrics

## Performance Targets
- Backend API: <100ms (p95), <200ms (p99)
- Frontend TTI: <3s on 3G
- LCP: <2.5s
- FID: <100ms
- CLS: <0.1
- Bundle size: <200KB gzipped

## Feature Adoption
- 30% of users create recurring tasks
- 50% of users set reminders
- 20% of users install PWA
- 80% of users use keyboard shortcuts

## Reliability
- 99.9% uptime
- <1% error rate
- 99% reminder delivery success

---

**End of Specification**
