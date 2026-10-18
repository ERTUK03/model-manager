"""create model_history table

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-03 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("user_email", sa.String(length=254), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_model_history_model_id", "model_history", ["model_id"])
    op.create_index("ix_model_history_created_at", "model_history", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_model_history_created_at", table_name="model_history")
    op.drop_index("ix_model_history_model_id", table_name="model_history")
    op.drop_table("model_history")
