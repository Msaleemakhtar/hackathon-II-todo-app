"""Initial migration with all tables

Revision ID: 0a1b2c3d4e5f
Revises:
Create Date: 2025-12-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0a1b2c3d4e5f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'user_id', name='uq_tag_name_user')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)
    op.create_index(op.f('ix_tags_user_id'), 'tags', ['user_id'], unique=False)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('recurrence_rule', sa.String(), nullable=True),
        sa.Column('parent_task_id', sa.Integer(), nullable=True),
        sa.Column('is_recurring_instance', sa.Boolean(), nullable=False),
        sa.Column('occurrence_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_completed'), 'tasks', ['completed'], unique=False)
    op.create_index(op.f('ix_tasks_created_at'), 'tasks', ['created_at'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_tasks_is_recurring_instance'), 'tasks', ['is_recurring_instance'], unique=False)
    op.create_index(op.f('ix_tasks_occurrence_date'), 'tasks', ['occurrence_date'], unique=False)
    op.create_index(op.f('ix_tasks_parent_task_id'), 'tasks', ['parent_task_id'], unique=False)
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_title'), 'tasks', ['title'], unique=False)
    op.create_index(op.f('ix_tasks_updated_at'), 'tasks', ['updated_at'], unique=False)
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)

    # Create task_tag_link table
    op.create_table(
        'task_tag_link',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('is_sent', sa.Boolean(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('message', sa.String(length=500), nullable=True),
        sa.Column('snoozed_until', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminders_is_sent'), 'reminders', ['is_sent'], unique=False)
    op.create_index(op.f('ix_reminders_remind_at'), 'reminders', ['remind_at'], unique=False)
    op.create_index(op.f('ix_reminders_task_id'), 'reminders', ['task_id'], unique=False)
    op.create_index(op.f('ix_reminders_user_id'), 'reminders', ['user_id'], unique=False)

    # Create task_orders table
    op.create_table(
        'task_orders',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('task_id')
    )
    op.create_index(op.f('ix_task_orders_sort_order'), 'task_orders', ['sort_order'], unique=False)
    op.create_index(op.f('ix_task_orders_user_id'), 'task_orders', ['user_id'], unique=False)

    # Create user_subscriptions table
    op.create_table(
        'user_subscriptions',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(length=500), nullable=False),
        sa.Column('p256dh_key', sa.String(length=200), nullable=False),
        sa.Column('auth_key', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('endpoint')
    )
    op.create_index(op.f('ix_user_subscriptions_is_active'), 'user_subscriptions', ['is_active'], unique=False)
    op.create_index(op.f('ix_user_subscriptions_user_id'), 'user_subscriptions', ['user_id'], unique=False)

    # Create web_vitals table
    op.create_table(
        'web_vitals',
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('rating', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_web_vitals_timestamp'), 'web_vitals', ['timestamp'], unique=False)
    op.create_index(op.f('ix_web_vitals_user_id'), 'web_vitals', ['user_id'], unique=False)

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('properties', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_events_event_name'), 'analytics_events', ['event_name'], unique=False)
    op.create_index(op.f('ix_analytics_events_timestamp'), 'analytics_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_analytics_events_user_id'), 'analytics_events', ['user_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_table('analytics_events')
    op.drop_table('web_vitals')
    op.drop_table('user_subscriptions')
    op.drop_table('task_orders')
    op.drop_table('reminders')
    op.drop_table('task_tag_link')
    op.drop_table('tasks')
    op.drop_table('tags')
    op.drop_table('categories')
    op.drop_table('users')