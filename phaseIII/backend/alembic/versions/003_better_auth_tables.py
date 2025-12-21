"""Add Better Auth tables: user, session, account, verification

Revision ID: 003_better_auth_tables
Revises: 002_add_external_id_to_conversations
Create Date: 2025-12-20

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "003_better_auth_tables"
down_revision = "002_add_external_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table (Better Auth core entity)
    op.create_table(
        "user",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("emailVerified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_email", "user", ["email"], unique=True)

    # Create session table (Better Auth session management)
    op.create_table(
        "session",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("userId", sa.String(), nullable=False),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("ipAddress", sa.String(), nullable=True),
        sa.Column("userAgent", sa.String(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_session_userId", "session", ["userId"], unique=False)
    op.create_index("idx_session_token", "session", ["token"], unique=True)

    # Create account table (Authentication provider information)
    op.create_table(
        "account",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("userId", sa.String(), nullable=False),
        sa.Column("accountId", sa.String(), nullable=False),
        sa.Column("providerId", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("accessToken", sa.String(), nullable=True),
        sa.Column("refreshToken", sa.String(), nullable=True),
        sa.Column("expiresAt", sa.DateTime(), nullable=True),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_account_userId", "account", ["userId"], unique=False)
    op.create_index("idx_account_provider", "account", ["providerId", "accountId"], unique=True)

    # Create verification table (Email verification tokens)
    op.create_table(
        "verification",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("expiresAt", sa.DateTime(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_verification_identifier", "verification", ["identifier"], unique=False)


def downgrade() -> None:
    # Drop verification table
    op.drop_index("idx_verification_identifier", table_name="verification")
    op.drop_table("verification")

    # Drop account table
    op.drop_index("idx_account_provider", table_name="account")
    op.drop_index("idx_account_userId", table_name="account")
    op.drop_table("account")

    # Drop session table
    op.drop_index("idx_session_token", table_name="session")
    op.drop_index("idx_session_userId", table_name="session")
    op.drop_table("session")

    # Drop user table
    op.drop_index("idx_user_email", table_name="user")
    op.drop_table("user")
