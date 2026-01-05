"""Test complete recurring task flow: Complete task → Event → New task created."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import get_session
from app.models.task import TaskPhaseIII
from app.services import task_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_recurring_task_flow():
    """
    Test the complete recurring task flow:
    1. Find an existing recurring task
    2. Mark it as completed
    3. Wait for recurring service to process event
    4. Verify new task instance was created
    """
    async for session in get_session():
        try:
            # Find a recurring task to complete (one of the duplicate tasks)
            query = (
                select(TaskPhaseIII)
                .where(TaskPhaseIII.recurrence_rule.isnot(None))
                .where(TaskPhaseIII.completed == False)
                .limit(1)
            )
            result = await session.execute(query)
            task = result.scalars().first()

            if not task:
                logger.error("❌ No recurring tasks found to test!")
                return

            logger.info(f"📋 Found recurring task to complete:")
            logger.info(f"   ID: {task.id}")
            logger.info(f"   Title: {task.title}")
            logger.info(f"   Recurrence: {task.recurrence_rule}")
            logger.info(f"   Due Date: {task.due_date}")

            original_task_count = (
                await session.execute(select(TaskPhaseIII))
            ).scalars().all()
            original_count = len(original_task_count)
            logger.info(f"📊 Total tasks before completion: {original_count}")

            # Mark task as completed
            logger.info(f"\n🔄 Marking task {task.id} as completed...")
            updated_task = await task_service.update_task(
                session=session,
                task=task,
                completed=True,
            )

            logger.info(f"✅ Task {updated_task.id} marked as completed!")
            logger.info(
                f"   TaskCompletedEvent should be published to 'task-recurrence' topic"
            )

            # Wait for recurring service to process event
            logger.info(f"\n⏳ Waiting 10 seconds for recurring service to process event...")
            await asyncio.sleep(10)

            # Check if new task was created
            logger.info(f"\n🔍 Checking for new task instance...")
            new_task_count = await session.execute(select(TaskPhaseIII))
            new_count = len(new_task_count.scalars().all())

            logger.info(f"📊 Total tasks after completion: {new_count}")

            if new_count > original_count:
                logger.info(f"✅ SUCCESS! New task instance created!")
                logger.info(f"   Tasks before: {original_count}")
                logger.info(f"   Tasks after: {new_count}")
                logger.info(f"   New tasks: {new_count - original_count}")

                # Find the new task
                new_task_query = (
                    select(TaskPhaseIII)
                    .where(TaskPhaseIII.user_id == task.user_id)
                    .where(TaskPhaseIII.title == task.title)
                    .where(TaskPhaseIII.completed == False)
                    .order_by(TaskPhaseIII.created_at.desc())
                )
                new_result = await session.execute(new_task_query)
                new_task = new_result.scalars().first()

                if new_task:
                    logger.info(f"\n📋 New recurring task details:")
                    logger.info(f"   ID: {new_task.id}")
                    logger.info(f"   Title: {new_task.title}")
                    logger.info(f"   Due Date: {new_task.due_date}")
                    logger.info(f"   Recurrence: {new_task.recurrence_rule}")
                    logger.info(f"   Created: {new_task.created_at}")

            else:
                logger.warning(f"⚠️  No new task created!")
                logger.warning(f"   Tasks before: {original_count}")
                logger.warning(f"   Tasks after: {new_count}")
                logger.warning(
                    f"\n💡 Check recurring-service logs: kubectl logs -n todo-phasev deployment/recurring-service -f"
                )

            await session.commit()

        except Exception as e:
            logger.error(f"❌ Error in test: {e}", exc_info=True)
            await session.rollback()

        return


if __name__ == "__main__":
    asyncio.run(test_recurring_task_flow())
