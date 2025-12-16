"""Add performance indexes for tasks and categories

Revision ID: 4eaae8f8cbbc
Revises: dfd778d535ec
Create Date: 2025-12-13 00:32:02.160913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4eaae8f8cbbc'
down_revision = '0a1b2c3d4e5f'
branch_labels = None
depends_on = None


def upgrade():
    # Add composite index for common query patterns on tasks table
    # This significantly improves performance for filtering tasks by user_id + status
    op.create_index(
        'idx_tasks_user_status',
        'tasks',
        ['user_id', 'status'],
        unique=False
    )

    # Add composite index for user_id + priority filtering
    op.create_index(
        'idx_tasks_user_priority',
        'tasks',
        ['user_id', 'priority'],
        unique=False
    )

    # Add composite index for sorting by due_date
    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date'],
        unique=False
    )

    # Add composite index for category lookups (type + user_id)
    op.create_index(
        'idx_categories_type_user',
        'categories',
        ['type', 'user_id'],
        unique=False
    )

    # Add unique constraint for category validation lookups
    op.create_index(
        'idx_categories_user_type_name',
        'categories',
        ['user_id', 'type', 'name'],
        unique=False
    )


def downgrade():
    # Remove indexes in reverse order
    op.drop_index('idx_categories_user_type_name', table_name='categories')
    op.drop_index('idx_categories_type_user', table_name='categories')
    op.drop_index('idx_tasks_user_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_priority', table_name='tasks')
    op.drop_index('idx_tasks_user_status', table_name='tasks')
