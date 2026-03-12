"""create news table

Revision ID: 006
Revises: 005
Create Date: 2026-03-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title_ru", sa.String(), nullable=False),
        sa.Column("title_kz", sa.String(), nullable=False, server_default=""),
        sa.Column("content_ru", sa.String(), nullable=False),
        sa.Column("content_kz", sa.String(), nullable=False, server_default=""),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("news")
