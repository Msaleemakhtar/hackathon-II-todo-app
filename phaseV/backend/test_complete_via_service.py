"""Complete a task using task_service to trigger Kafka event."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, '/app')

from app.database import get_session
from app.services import task_service
from app.models.task import TaskPhaseIII


async def main():
    """Complete a recurring task and check if new instance is created."""
    async for session in get_session():
        try:
            # Get task 246
            task = await session.get(TaskPhaseIII, 246)

            if not task:
                print("Task 246 not found!")
                return

            print(f"\n📋 Found task:")
            print(f"   ID: {task.id}")
            print(f"   Title: {task.title}")
            print(f"   Completed: {task.completed}")
            print(f"   Recurrence: {task.recurrence_rule}")
            print(f"   Due Date: {task.due_date}")

            # Count tasks before
            from sqlalchemy import select, func
            before_count = await session.scalar(select(func.count()).select_from(TaskPhaseIII))
            print(f"\n📊 Total tasks before: {before_count}")

            # Complete the task using task_service (this will publish Kafka event)
            print(f"\n🔄 Completing task {task.id} via task_service...")
            updated_task = await task_service.update_task(
                session=session,
                task=task,
                completed=True,
            )

            print(f"✅ Task {updated_task.id} completed!")
            print(f"   TaskCompletedEvent should be published to 'task-recurrence' topic")

            # Wait for recurring service to process
            print(f"\n⏳ Waiting 15 seconds for recurring service...")
            await asyncio.sleep(15)

            # Count tasks after
            after_count = await session.scalar(select(func.count()).select_from(TaskPhaseIII))
            print(f"\n📊 Total tasks after: {after_count}")

            if after_count > before_count:
                print(f"✅ SUCCESS! New task created! (+{after_count - before_count})")

                # Find the new task
                from sqlalchemy import and_
                new_task_query = (
                    select(TaskPhaseIII)
                    .where(TaskPhaseIII.user_id == task.user_id)
                    .where(TaskPhaseIII.title == task.title)
                    .where(TaskPhaseIII.completed == False)
                    .order_by(TaskPhaseIII.created_at.desc())
                )
                result = await session.execute(new_task_query)
                new_task = result.scalars().first()

                if new_task:
                    print(f"\n📋 New recurring task:")
                    print(f"   ID: {new_task.id}")
                    print(f"   Due Date: {new_task.due_date}")
                    print(f"   Created: {new_task.created_at}")
            else:
                print(f"❌ No new task created!")
                print(f"   Check recurring-service logs:")
                print(f"   kubectl logs -n todo-phasev -l app=recurring-service --tail=50")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()

        return

if __name__ == "__main__":
    asyncio.run(main())
