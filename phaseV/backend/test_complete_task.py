"""Simple script to complete a recurring task for testing."""
import asyncio
import asyncpg
import os

async def main():
    # Connect to database
    database_url = "postgresql://neondb_owner:npg_zTkq1ABHR8uC@ep-green-shape-advm09wo-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
    conn = await asyncpg.connect(database_url)

    # Find a recurring task
    task = await conn.fetchrow("""
        SELECT id, user_id, title, due_date, recurrence_rule
        FROM tasks_phaseiii
        WHERE recurrence_rule IS NOT NULL
          AND completed = false
        ORDER BY created_at DESC
        LIMIT 1
    """)

    if not task:
        print("No recurring tasks found!")
        await conn.close()
        return

    print(f"\n📋 Found recurring task:")
    print(f"   ID: {task['id']}")
    print(f"   Title: {task['title']}")
    print(f"   Due Date: {task['due_date']}")
    print(f"   Recurrence: {task['recurrence_rule']}")

    # Count total tasks before
    before_count = await conn.fetchval("SELECT COUNT(*) FROM tasks_phaseiii")
    print(f"\n📊 Total tasks before: {before_count}")

    # Complete the task
    await conn.execute("""
        UPDATE tasks_phaseiii
        SET completed = true, updated_at = NOW()
        WHERE id = $1
    """, task['id'])

    print(f"\n✅ Marked task {task['id']} as completed!")
    print(f"   Now watch recurring-service logs to see if it creates a new task instance.")
    print(f"   Run: kubectl logs -n todo-phasev -l app=recurring-service -f")
    print(f"\n⏳ Waiting 15 seconds for processing...")

    await asyncio.sleep(15)

    # Count total tasks after
    after_count = await conn.fetchval("SELECT COUNT(*) FROM tasks_phaseiii")
    print(f"\n📊 Total tasks after: {after_count}")

    if after_count > before_count:
        print(f"✅ SUCCESS! New task created! (+{after_count - before_count})")

        # Find the new task
        new_task = await conn.fetchrow("""
            SELECT id, title, due_date, recurrence_rule, created_at
            FROM tasks_phaseiii
            WHERE user_id = $1
              AND title = $2
              AND completed = false
            ORDER BY created_at DESC
            LIMIT 1
        """, task['user_id'], task['title'])

        if new_task:
            print(f"\n📋 New recurring task:")
            print(f"   ID: {new_task['id']}")
            print(f"   Due Date: {new_task['due_date']}")
            print(f"   Created: {new_task['created_at']}")
    else:
        print(f"❌ No new task created.")
        print(f"   Check recurring-service logs for errors.")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
