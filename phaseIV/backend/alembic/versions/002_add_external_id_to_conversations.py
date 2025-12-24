"""Add external_id to conversations

Revision ID: 002_add_external_id
Revises: 001_initial_schema
Create Date: 2025-12-20

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_add_external_id"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add external_id column to conversations table
    op.add_column("conversations", sa.Column("external_id", sa.String(), nullable=True))
    # Create index on external_id for faster lookups
    op.create_index("idx_conversations_external_id", "conversations", ["external_id"], unique=False)


def downgrade() -> None:
    # Remove index and column
    op.drop_index("idx_conversations_external_id", table_name="conversations")
    op.drop_column("conversations", "external_id")
