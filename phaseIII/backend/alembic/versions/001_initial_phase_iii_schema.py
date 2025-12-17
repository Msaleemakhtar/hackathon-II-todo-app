"""Initial Phase III schema

Revision ID: 001
Revises:
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial Phase III schema."""
    # Create tasks_phaseiii table
    op.create_table(
        'tasks_phaseiii',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create messages table with FK to conversations
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_tasks_phaseiii_user_id', 'tasks_phaseiii', ['user_id'])
    op.create_index('idx_tasks_phaseiii_created_at', 'tasks_phaseiii', ['created_at'])
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])


def downgrade():
    """Drop Phase III schema."""
    # Drop in reverse order (FK constraints)
    op.drop_index('idx_messages_user_id', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_index('idx_tasks_phaseiii_created_at', table_name='tasks_phaseiii')
    op.drop_index('idx_tasks_phaseiii_user_id', table_name='tasks_phaseiii')

    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('tasks_phaseiii')
