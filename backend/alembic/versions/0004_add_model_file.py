"""add file columns to ml_models

Revision ID: 0004
Revises: 0003
Create Date: 2026-01-04 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ml_models") as batch:
        batch.add_column(sa.Column("file_key", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("file_name", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("file_size", sa.BigInteger(), nullable=True))
        batch.add_column(sa.Column("file_sha256", sa.String(length=64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("ml_models") as batch:
        batch.drop_column("file_sha256")
        batch.drop_column("file_size")
        batch.drop_column("file_name")
        batch.drop_column("file_key")
