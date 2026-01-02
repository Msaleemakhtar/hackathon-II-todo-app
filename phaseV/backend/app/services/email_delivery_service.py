"""Email delivery service for task reminder notifications."""

import asyncio
import logging
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Optional

import aiosmtplib
from aiokafka import AIOKafkaConsumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings
from app.kafka import config as kafka_config
from app.kafka.events import ReminderSentEvent

logger = logging.getLogger(__name__)


class EmailDeliveryService:
    """
    Kafka consumer service that delivers email notifications for task reminders.

    Architecture:
    - Consumes ReminderSentEvent from task-reminders topic
    - Fetches user email from Better Auth user table
    - Sends formatted HTML email via SMTP
    - Handles errors with retry logic
    """

    def __init__(self):
        """Initialize email delivery service."""
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._db_engine: Optional[AsyncEngine] = None
        self._running = False

        # SMTP configuration from environment
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_from_email = settings.smtp_from_email
        self.smtp_from_name = settings.smtp_from_name

        logger.info(
            f"Email Delivery Service initialized (SMTP: {self.smtp_host}:{self.smtp_port}, "
            f"From: {self.smtp_from_name} <{self.smtp_from_email}>)"
        )

    async def start(self) -> None:
        """Start the email delivery service (Kafka consumer + database connection)."""
        if self._running:
            logger.warning("Email delivery service already running")
            return

        try:
            # Initialize database engine
            self._db_engine = create_async_engine(
                settings.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
            logger.info(f"Database engine initialized: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'database'}")

            # Initialize Kafka consumer
            ssl_context = kafka_config.get_kafka_ssl_context()

            self._consumer = AIOKafkaConsumer(
                "task-reminders",
                bootstrap_servers=kafka_config.KAFKA_BOOTSTRAP_SERVERS,
                security_protocol=kafka_config.KAFKA_SECURITY_PROTOCOL,
                sasl_mechanism=kafka_config.KAFKA_SASL_MECHANISM,
                sasl_plain_username=kafka_config.KAFKA_SASL_USERNAME,
                sasl_plain_password=kafka_config.KAFKA_SASL_PASSWORD,
                ssl_context=ssl_context,
                group_id=settings.email_delivery_group_id,
                **kafka_config.KAFKA_CONSUMER_CONFIG,
            )

            await self._consumer.start()
            logger.info(
                f"Kafka consumer started (topic: task-reminders, group: {settings.email_delivery_group_id})"
            )

            self._running = True

        except Exception as e:
            logger.error(f"Failed to start email delivery service: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the email delivery service gracefully."""
        if not self._running:
            return

        logger.info("Stopping email delivery service...")
        self._running = False

        # Stop Kafka consumer
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped")

        # Dispose database engine
        if self._db_engine:
            await self._db_engine.dispose()
            logger.info("Database engine disposed")

        logger.info("Email delivery service stopped successfully")

    async def health_check(self) -> bool:
        """
        Check service health (Kafka + database + SMTP connectivity).

        Returns:
            True if all dependencies are healthy
        """
        if not self._running:
            return False

        try:
            # Check Kafka consumer
            if not self._consumer or not hasattr(self._consumer, "_client"):
                logger.error("Kafka consumer not initialized")
                return False

            # Check database connectivity
            async with self._db_engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))

            # Check SMTP connectivity (optional test connection)
            # Note: Actual SMTP connection is established per-email send

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return False

    async def consume_events(self) -> None:
        """
        Main event loop: consume ReminderSentEvent from Kafka and deliver emails.

        This is the primary background task for the service.
        """
        logger.info("Starting email delivery event consumer loop")

        try:
            async for message in self._consumer:
                try:
                    # Deserialize event
                    event = ReminderSentEvent.model_validate_json(message.value)
                    logger.info(
                        f"Received ReminderSentEvent for task {event.task_id} (user: {event.user_id})"
                    )

                    # Process reminder email
                    await self._process_reminder(event)

                    # Commit offset after successful processing
                    await self._consumer.commit()
                    logger.debug(f"Committed offset for task {event.task_id}")

                except Exception as e:
                    logger.error(
                        f"Error processing reminder event: {e}",
                        exc_info=True,
                        extra={"message_value": message.value if message else None},
                    )
                    # Do NOT commit offset - retry on next poll
                    # In production, consider dead-letter queue after N retries

        except asyncio.CancelledError:
            logger.info("Email delivery consumer loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in consumer loop: {e}", exc_info=True)
            raise

    async def _process_reminder(self, event: ReminderSentEvent) -> None:
        """
        Process a single reminder event: fetch user email and send notification.

        Args:
            event: ReminderSentEvent with task details and user ID

        Raises:
            Exception: If email delivery fails (will prevent offset commit for retry)
        """
        try:
            # Fetch user email from database via task_id (not hashed user_id)
            user_email = await self._get_user_email_by_task(event.task_id)

            if not user_email:
                logger.warning(
                    f"No email found for task {event.task_id}, skipping reminder"
                )
                return

            # Format email body
            html_body, text_body = self._format_email(event)

            # Send email via SMTP
            await self._send_email(
                to_email=user_email, subject=f"Reminder: {event.task_title}", html=html_body, text=text_body
            )

            logger.info(
                f"✅ Email reminder sent to {user_email} for task {event.task_id} ('{event.task_title}')"
            )

        except Exception as e:
            logger.error(f"Failed to process reminder for task {event.task_id}: {e}", exc_info=True)
            raise

    async def _get_user_email_by_task(self, task_id: int) -> Optional[str]:
        """
        Fetch user email from Better Auth user table via task lookup.

        Args:
            task_id: Task ID to lookup user

        Returns:
            User email address or None if not found
        """
        try:
            async with self._db_engine.begin() as conn:
                from sqlalchemy import text

                # Query task to get the original string user_id (Better Auth ID)
                task_result = await conn.execute(
                    text('SELECT user_id FROM tasks_phaseiii WHERE id = :task_id'),
                    {'task_id': task_id}
                )
                task_row = task_result.first()

                if not task_row:
                    logger.warning(f"Task {task_id} not found in database")
                    return None

                user_id = task_row[0]

                # Query Better Auth user table with the original string user_id
                user_result = await conn.execute(
                    text('SELECT email FROM "user" WHERE id = :user_id'),
                    {'user_id': user_id}
                )
                user_row = user_result.first()

                if user_row:
                    logger.debug(f"Found email for user {user_id} (task {task_id})")
                    return user_row[0]  # email column

                logger.warning(f"User {user_id} not found in Better Auth user table")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch user email for task {task_id}: {e}", exc_info=True)
            return None

    def _format_email(self, event: ReminderSentEvent) -> tuple[str, str]:
        """
        Format HTML and plain text email body from reminder event.

        Args:
            event: ReminderSentEvent with task details

        Returns:
            Tuple of (html_body, text_body)
        """
        # Calculate time until due
        now = datetime.now(timezone.utc)
        time_until_due = event.task_due_date - now if event.task_due_date else None
        minutes_until_due = int(time_until_due.total_seconds() / 60) if time_until_due else 0

        # Priority color mapping
        priority_colors = {"urgent": "#dc2626", "high": "#ea580c", "medium": "#ca8a04", "low": "#16a34a"}

        priority = event.task_priority or "medium"
        priority_color = priority_colors.get(priority, "#6b7280")

        # Format due date
        due_date_formatted = (
            event.task_due_date.strftime("%A, %B %d, %Y at %I:%M %p") if event.task_due_date else "Not set"
        )

        # HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Reminder</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🔔 Task Reminder</h1>
    </div>

    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e5e7eb;">
        <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
            <h2 style="margin-top: 0; color: #1f2937; font-size: 24px;">{event.task_title}</h2>

            {f'<p style="color: #4b5563; font-size: 16px; margin: 15px 0;">{event.task_description}</p>' if event.task_description else ''}

            <div style="margin-top: 25px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Due Date:</td>
                        <td style="padding: 10px 0; color: #1f2937; font-weight: 500;">{due_date_formatted}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Priority:</td>
                        <td style="padding: 10px 0;">
                            <span style="display: inline-block; padding: 4px 12px; background-color: {priority_color}; color: white; border-radius: 12px; font-size: 14px; font-weight: 600; text-transform: uppercase;">
                                {priority}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; color: #6b7280; font-weight: 600;">Time Remaining:</td>
                        <td style="padding: 10px 0; color: #dc2626; font-weight: 700; font-size: 18px;">{minutes_until_due} minutes</td>
                    </tr>
                </table>
            </div>
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
            <p style="margin: 0; color: #1e40af; font-size: 14px;">
                <strong>💡 Tip:</strong> Complete this task before the deadline to stay on track!
            </p>
        </div>
    </div>

    <div style="margin-top: 20px; text-align: center; color: #9ca3af; font-size: 12px;">
        <p>Sent by <strong>Todo App - Phase V</strong></p>
        <p style="margin-top: 5px;">Hackathon II Event-Driven Notifications</p>
    </div>
</body>
</html>
"""

        # Plain text fallback
        text_body = f"""
🔔 TASK REMINDER

Task: {event.task_title}
{'Description: ' + event.task_description if event.task_description else ''}

Due Date: {due_date_formatted}
Priority: {priority.upper()}
Time Remaining: {minutes_until_due} minutes

---
Sent by Todo App - Phase V
Hackathon II Event-Driven Notifications
"""

        return html_body, text_body

    async def _send_email(self, to_email: str, subject: str, html: str, text: str) -> None:
        """
        Send email via SMTP with retry logic.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html: HTML email body
            text: Plain text email body

        Raises:
            Exception: If email sending fails after retries
        """
        message = EmailMessage()
        message["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Set plain text and HTML content
        message.set_content(text)
        message.add_alternative(html, subtype="html")

        # Retry configuration
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Connect to SMTP server and send
                smtp_client = aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=False,  # Start with plaintext, upgrade with STARTTLS
                )

                async with smtp_client:
                    await smtp_client.connect()
                    await smtp_client.starttls()  # Upgrade to TLS
                    await smtp_client.login(self.smtp_username, self.smtp_password)
                    await smtp_client.send_message(message)

                logger.info(f"Email sent successfully to {to_email} (attempt {attempt}/{max_retries})")
                return

            except Exception as e:
                logger.warning(
                    f"Email send attempt {attempt}/{max_retries} failed: {e}",
                    exc_info=attempt == max_retries,  # Full traceback only on final failure
                )

                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Final attempt failed - raise exception to prevent offset commit
                    raise Exception(f"Failed to send email to {to_email} after {max_retries} attempts") from e


# Global email delivery service instance
email_delivery_service = EmailDeliveryService()
