"""Initial schema: tasks_phaseiii, conversations, messages

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-17

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tasks_phaseiii table
    op.create_table(
        "tasks_phaseiii",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tasks_phaseiii_user_id", "tasks_phaseiii", ["user_id"], unique=False)
    op.create_index(
        "idx_tasks_phaseiii_user_completed",
        "tasks_phaseiii",
        ["user_id", "completed"],
        unique=False,
    )

    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_conversations_user_id", "conversations", ["user_id"], unique=False)

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_messages_conversation_id", "messages", ["conversation_id"], unique=False)
    op.create_index("idx_messages_user_id", "messages", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_messages_user_id", table_name="messages")
    op.drop_index("idx_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("idx_conversations_user_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("idx_tasks_phaseiii_user_completed", table_name="tasks_phaseiii")
    op.drop_index("idx_tasks_phaseiii_user_id", table_name="tasks_phaseiii")
    op.drop_table("tasks_phaseiii")
