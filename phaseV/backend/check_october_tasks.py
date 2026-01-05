#!/usr/bin/env python3
"""Check database for tasks with October 2024 due dates."""

import asyncio
import sys
from datetime import datetime

import asyncpg


async def check_october_tasks():
    """Connect to Neon database and check for old October tasks."""

    # Database connection string
    db_url = "postgresql://neondb_owner:npg_zTkq1ABHR8uC@ep-green-shape-advm09wo-pooler.c-2.us-east-1.aws.neon.tech/neondb?ssl=require"

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✓ Connected to Neon database")

        # Query for October 2024 tasks
        query = """
            SELECT id, title, due_date, created_at, recurrence_rule, completed
            FROM tasks_phaseiii
            WHERE due_date >= '2024-10-01' AND due_date < '2024-11-01'
            ORDER BY created_at DESC
        """

        rows = await conn.fetch(query)

        print(f"\n{'='*80}")
        print(f"Found {len(rows)} tasks with October 2024 due dates:")
        print(f"{'='*80}\n")

        if rows:
            for row in rows:
                print(f"ID: {row['id']}")
                print(f"Title: {row['title']}")
                print(f"Due Date: {row['due_date']}")
                print(f"Created At: {row['created_at']}")
                print(f"Recurrence: {row['recurrence_rule'] or 'None'}")
                print(f"Completed: {row['completed']}")
                print(f"{'-'*80}")
        else:
            print("✓ No October tasks found!")

        # Also check for any tasks in general
        total_query = "SELECT COUNT(*) FROM tasks_phaseiii"
        total_count = await conn.fetchval(total_query)
        print(f"\nTotal tasks in database: {total_count}")

        # Check recent tasks
        recent_query = """
            SELECT id, title, due_date, created_at
            FROM tasks_phaseiii
            ORDER BY created_at DESC
            LIMIT 5
        """
        recent_rows = await conn.fetch(recent_query)

        if recent_rows:
            print(f"\n{'='*80}")
            print("5 Most Recent Tasks:")
            print(f"{'='*80}\n")
            for row in recent_rows:
                print(f"ID: {row['id']} | Title: {row['title']}")
                print(f"Due: {row['due_date']} | Created: {row['created_at']}")
                print(f"{'-'*80}")

        await conn.close()
        print("\n✓ Database connection closed")

        return len(rows)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return -1


if __name__ == "__main__":
    result = asyncio.run(check_october_tasks())
    sys.exit(0 if result >= 0 else 1)
