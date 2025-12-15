"""
Notification service for sending task reminders via browser push and email.

This service handles:
- Creating and managing task reminders
- Sending browser push notifications
- Sending email notifications
- Snozing and canceling reminders
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reminder import Reminder
from ..models.user_subscription import UserSubscription

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing task reminders and sending notifications."""

    def __init__(self, db_session: AsyncSession):
        """Initialize the notification service.

        Args:
            db_session: Async database session for data access
        """
        self.db = db_session

    async def create(
        self,
        user_id: str,
        task_id: int,
        remind_at: datetime,
        channel: str,
        message: Optional[str] = None
    ) -> Reminder:
        """Create a new reminder for a task.

        Args:
            user_id: ID of the user creating the reminder
            task_id: ID of the task to remind about
            remind_at: When to send the reminder
            channel: Notification channel ("browser", "email", or "both")
            message: Optional custom message for the reminder

        Returns:
            Created Reminder instance

        Raises:
            ValueError: If channel is invalid or remind_at is in the past
        """
        # Validate channel
        if channel not in ["browser", "email", "both"]:
            raise ValueError(f"Invalid channel: {channel}. Must be 'browser', 'email', or 'both'")

        # Validate remind_at is in the future
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        remind_at_naive = remind_at.replace(tzinfo=None) if remind_at.tzinfo else remind_at
        if remind_at_naive <= now:
            raise ValueError("Reminder time must be in the future")

        # Create reminder
        reminder = Reminder(
            user_id=user_id,
            task_id=task_id,
            remind_at=remind_at_naive,
            channel=channel,
            message=message,
            is_sent=False,
            created_at=now,
            updated_at=now
        )

        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)

        logger.info(f"Created reminder {reminder.id} for user {user_id}, task {task_id}")
        return reminder

    async def get(self, reminder_id: int, user_id: str) -> Optional[Reminder]:
        """Get a reminder by ID for a specific user.

        Args:
            reminder_id: ID of the reminder to retrieve
            user_id: ID of the user (for authorization)

        Returns:
            Reminder instance if found, None otherwise
        """
        statement = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self, user_id: str, include_sent: bool = False) -> List[Reminder]:
        """Get all reminders for a user.

        Args:
            user_id: ID of the user
            include_sent: Whether to include already sent reminders

        Returns:
            List of Reminder instances
        """
        statement = select(Reminder).where(Reminder.user_id == user_id)

        if not include_sent:
            statement = statement.where(Reminder.is_sent == False)

        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def mark_as_sent(self, reminder_id: int, user_id: str) -> Optional[Reminder]:
        """Mark a reminder as sent.

        Args:
            reminder_id: ID of the reminder
            user_id: ID of the user (for authorization)

        Returns:
            Updated Reminder instance if found, None otherwise
        """
        reminder = await self.get(reminder_id, user_id)
        if not reminder:
            return None

        reminder.is_sent = True
        reminder.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        reminder.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.db.commit()
        await self.db.refresh(reminder)

        logger.info(f"Marked reminder {reminder_id} as sent")
        return reminder

    async def snooze(
        self,
        reminder_id: int,
        user_id: str,
        snooze_minutes: int = 10
    ) -> Optional[Reminder]:
        """Snooze a reminder for a specified duration.

        Args:
            reminder_id: ID of the reminder
            user_id: ID of the user (for authorization)
            snooze_minutes: How many minutes to snooze (default: 10)

        Returns:
            Updated Reminder instance if found, None otherwise
        """
        reminder = await self.get(reminder_id, user_id)
        if not reminder:
            return None

        # Calculate new reminder time
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        snooze_until = now + timedelta(minutes=snooze_minutes)
        reminder.snoozed_until = snooze_until
        reminder.remind_at = snooze_until
        reminder.updated_at = now

        await self.db.commit()
        await self.db.refresh(reminder)

        logger.info(f"Snoozed reminder {reminder_id} until {snooze_until}")
        return reminder

    async def cancel(self, reminder_id: int, user_id: str) -> bool:
        """Cancel (delete) a reminder.

        Args:
            reminder_id: ID of the reminder
            user_id: ID of the user (for authorization)

        Returns:
            True if reminder was deleted, False if not found
        """
        reminder = await self.get(reminder_id, user_id)
        if not reminder:
            return False

        await self.db.delete(reminder)
        await self.db.commit()

        logger.info(f"Cancelled reminder {reminder_id}")
        return True

    async def send_browser_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a browser push notification to a user.

        Args:
            user_id: ID of the user to notify
            title: Notification title
            body: Notification body text
            data: Optional additional data to include

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            # Import pywebpush
            from pywebpush import webpush, WebPushException
            import json
            import os

            # Get VAPID configuration
            vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
            vapid_claims = {
                "sub": f"mailto:{os.getenv('VAPID_CLAIM_EMAIL', 'admin@example.com')}"
            }

            if not vapid_private_key:
                logger.error("VAPID_PRIVATE_KEY not configured")
                return False

            # Get user subscriptions
            statement = select(UserSubscription).where(
                UserSubscription.user_id == user_id,
                UserSubscription.is_active == True
            )
            result = await self.db.execute(statement)
            subscriptions = list(result.scalars().all())

            if not subscriptions:
                logger.warning(f"No active subscriptions found for user {user_id}")
                return False

            # Prepare notification payload
            notification_data = {
                "title": title,
                "body": body,
                "data": data or {}
            }

            # Send to all user subscriptions
            success_count = 0
            for subscription in subscriptions:
                try:
                    # Build subscription info for webpush
                    subscription_info = {
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh_key,
                            "auth": subscription.auth_key
                        }
                    }

                    # Send push notification
                    webpush(
                        subscription_info=subscription_info,
                        data=json.dumps(notification_data),
                        vapid_private_key=vapid_private_key,
                        vapid_claims=vapid_claims
                    )

                    success_count += 1
                    logger.info(f"Sent browser notification to subscription {subscription.id}")

                except WebPushException as e:
                    logger.error(f"Failed to send push notification to subscription {subscription.id}: {e}")

                    # If subscription is expired/invalid, mark as inactive
                    if e.response and e.response.status_code in [404, 410]:
                        subscription.is_active = False
                        subscription.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        await self.db.commit()

                except Exception as e:
                    logger.error(f"Unexpected error sending push notification: {e}")

            return success_count > 0

        except Exception as e:
            logger.error(f"Error in send_browser_notification: {e}")
            return False

    async def send_email_notification(
        self,
        user_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send an email notification to a user.

        Args:
            user_email: Email address of the recipient
            subject: Email subject line
            body: Email body text

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os

            # Get SMTP configuration from environment
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)

            if not smtp_username or not smtp_password:
                logger.error("SMTP credentials not configured")
                return False

            # Create email message
            message = MIMEMultipart("alternative")
            message["From"] = smtp_from_email
            message["To"] = user_email
            message["Subject"] = subject

            # Add plain text body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            # Add HTML body (simple formatting)
            html_body = f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                  <h2 style="color: #333;">Task Reminder</h2>
                  <p>{body.replace(chr(10), '<br>')}</p>
                  <hr style="border: 1px solid #eee; margin: 20px 0;">
                  <p style="color: #666; font-size: 12px;">
                    This is an automated reminder from your Task Management System.
                  </p>
                </div>
              </body>
            </html>
            """
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

            # Send email with retry logic
            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    # Connect and send
                    async with aiosmtplib.SMTP(
                        hostname=smtp_host,
                        port=smtp_port,
                        use_tls=False
                    ) as smtp:
                        # Start TLS
                        await smtp.starttls()
                        # Login
                        await smtp.login(smtp_username, smtp_password)
                        # Send message
                        await smtp.send_message(message)

                    logger.info(f"Email sent successfully to {user_email}")
                    return True

                except aiosmtplib.SMTPException as e:
                    logger.warning(f"SMTP error on attempt {attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to send email after {max_retries} attempts")
                        return False

                except Exception as e:
                    logger.error(f"Unexpected error sending email: {e}")
                    return False

        except Exception as e:
            logger.error(f"Error in send_email_notification: {e}")
            return False
