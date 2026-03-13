"""add media_url and media_type to news

Revision ID: 010
Revises: 008
Create Date: 2026-03-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "010"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.add_column("news", sa.Column("media_url", sa.String(), nullable=True))
  op.add_column("news", sa.Column("media_type", sa.String(), nullable=True))


def downgrade() -> None:
  op.drop_column("news", "media_type")
  op.drop_column("news", "media_url")

