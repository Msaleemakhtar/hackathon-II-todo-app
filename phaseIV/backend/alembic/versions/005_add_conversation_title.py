"""Add title to conversations

Revision ID: 005_add_conversation_title
Revises: 004_add_jwks_table
Create Date: 2025-12-21

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "005_add_conversation_title"
down_revision = "004_add_jwks_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add title column to conversations table
    op.add_column("conversations", sa.Column("title", sa.String(), nullable=True))


def downgrade() -> None:
    # Remove title column
    op.drop_column("conversations", "title")
