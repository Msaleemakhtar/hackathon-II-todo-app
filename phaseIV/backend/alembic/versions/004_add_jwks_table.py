"""Add jwks table for Better Auth JWT plugin

Revision ID: 004_add_jwks_table
Revises: 003_better_auth_tables
Create Date: 2025-12-20

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_add_jwks_table"
down_revision = "003_better_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jwks table (JSON Web Key Set for Better Auth JWT plugin)
    op.create_table(
        "jwks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("publicKey", sa.String(), nullable=False),
        sa.Column("privateKey", sa.String(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jwks")
