"""add video_url and image_url to news

Revision ID: 007
Revises: 006
Create Date: 2026-03-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("news", sa.Column("video_url", sa.String(), nullable=True))
    op.add_column("news", sa.Column("image_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("news", "image_url")
    op.drop_column("news", "video_url")
