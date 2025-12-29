"""add_advanced_task_fields_and_tables

Revision ID: dd759de1dae9
Revises: 005_add_conversation_title
Create Date: 2025-12-30 02:22:38.079037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dd759de1dae9'
down_revision: Union[str, Sequence[str], None] = '005_add_conversation_title'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add Phase V advanced task management features."""

    # Step 1: Create priority_level ENUM type
    priority_level_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='priority_level')
    priority_level_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_category_user_name'),
        sa.CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name='check_color_format'
        )
    )
    op.create_index('idx_categories_user_id', 'categories', ['user_id'])

    # Step 3: Create tags_phasev table
    op.create_table(
        'tags_phasev',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_tag_user_name'),
        sa.CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name='check_tag_color_format'
        )
    )
    op.create_index('idx_tags_user_id', 'tags_phasev', ['user_id'])

    # Step 4: Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('task_id', 'tag_id'),
        sa.ForeignKeyConstraint(
            ['task_id'],
            ['tasks_phaseiii.id'],
            name='fk_task',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['tag_id'],
            ['tags_phasev.id'],
            name='fk_tag',
            ondelete='CASCADE'
        )
    )
    op.create_index('idx_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('idx_task_tags_tag_id', 'task_tags', ['tag_id'])

    # Step 5: Add new columns to tasks_phaseiii table
    op.add_column('tasks_phaseiii',
                  sa.Column('priority', sa.String(length=10),
                           nullable=False, server_default='medium'))
    op.add_column('tasks_phaseiii',
                  sa.Column('due_date', sa.TIMESTAMP(), nullable=True))
    op.add_column('tasks_phaseiii',
                  sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('tasks_phaseiii',
                  sa.Column('recurrence_rule', sa.Text(), nullable=True))
    op.add_column('tasks_phaseiii',
                  sa.Column('reminder_sent', sa.Boolean(),
                           nullable=False, server_default='false'))
    op.add_column('tasks_phaseiii',
                  sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))
    op.add_column('tasks_phaseiii',
                  sa.Column('search_rank', sa.REAL(), nullable=True))

    # Step 6: Convert priority column from VARCHAR to priority_level ENUM
    # First drop the default, then convert type, then re-add default
    op.alter_column('tasks_phaseiii', 'priority', server_default=None)
    op.execute("ALTER TABLE tasks_phaseiii ALTER COLUMN priority TYPE priority_level USING priority::priority_level")
    op.execute("ALTER TABLE tasks_phaseiii ALTER COLUMN priority SET DEFAULT 'medium'::priority_level")

    # Step 7: Add foreign key constraint for category_id
    op.create_foreign_key(
        'fk_category',
        'tasks_phaseiii',
        'categories',
        ['category_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Step 8: Create indexes on new columns
    op.create_index('idx_tasks_category_id', 'tasks_phaseiii', ['category_id'])
    op.create_index(
        'idx_tasks_due_date',
        'tasks_phaseiii',
        ['due_date'],
        postgresql_where=sa.text('due_date IS NOT NULL')
    )
    op.create_index('idx_tasks_priority', 'tasks_phaseiii', ['priority'])
    op.create_index(
        'idx_tasks_search_vector',
        'tasks_phaseiii',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Step 9: Initialize search_vector for existing tasks
    op.execute("""
        UPDATE tasks_phaseiii
        SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
    """)

    # Step 10: Create trigger function for auto-updating search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION update_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Step 11: Create trigger for search_vector updates
    op.execute("""
        CREATE TRIGGER tasks_search_vector_update
        BEFORE INSERT OR UPDATE OF title, description ON tasks_phaseiii
        FOR EACH ROW EXECUTE FUNCTION update_search_vector();
    """)

    # Step 12: Create trigger function for auto-updating updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Step 13: Create trigger for updated_at updates
    op.execute("""
        CREATE TRIGGER tasks_updated_at_trigger
        BEFORE UPDATE ON tasks_phaseiii
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Downgrade schema - Remove Phase V advanced features."""

    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks_phaseiii")
    op.execute("DROP TRIGGER IF EXISTS tasks_updated_at_trigger ON tasks_phaseiii")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_search_vector()")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop indexes
    op.drop_index('idx_tasks_search_vector', 'tasks_phaseiii')
    op.drop_index('idx_tasks_priority', 'tasks_phaseiii')
    op.drop_index('idx_tasks_due_date', 'tasks_phaseiii')
    op.drop_index('idx_tasks_category_id', 'tasks_phaseiii')

    # Drop foreign key constraint
    op.drop_constraint('fk_category', 'tasks_phaseiii', type_='foreignkey')

    # Drop new columns from tasks_phaseiii
    op.drop_column('tasks_phaseiii', 'search_rank')
    op.drop_column('tasks_phaseiii', 'search_vector')
    op.drop_column('tasks_phaseiii', 'reminder_sent')
    op.drop_column('tasks_phaseiii', 'recurrence_rule')
    op.drop_column('tasks_phaseiii', 'category_id')
    op.drop_column('tasks_phaseiii', 'due_date')
    op.drop_column('tasks_phaseiii', 'priority')

    # Drop junction table indexes
    op.drop_index('idx_task_tags_tag_id', 'task_tags')
    op.drop_index('idx_task_tags_task_id', 'task_tags')

    # Drop tables
    op.drop_table('task_tags')

    # Drop tags table indexes
    op.drop_index('idx_tags_user_id', 'tags_phasev')
    op.drop_table('tags_phasev')

    # Drop categories table indexes
    op.drop_index('idx_categories_user_id', 'categories')
    op.drop_table('categories')

    # Drop ENUM type
    priority_level_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='priority_level')
    priority_level_enum.drop(op.get_bind(), checkfirst=True)
