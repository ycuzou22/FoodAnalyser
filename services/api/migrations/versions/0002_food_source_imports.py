"""Traçabilité des imports CIQUAL / Open Food Facts (licence, version, volumes, rejets).

Révision : 0002
Précédente : 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "food_source_imports",
        sa.Column(
            "source",
            postgresql.ENUM(name="food_source", create_type=False),  # type créé par 0001
            nullable=False,
        ),
        sa.Column("source_version", sa.String(length=100), nullable=False),
        sa.Column("license", sa.String(length=100), nullable=False),
        sa.Column("attribution", sa.Text(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_read", sa.Integer(), nullable=False),
        sa.Column("rows_inserted", sa.Integer(), nullable=False),
        sa.Column("rows_updated", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("rejections", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_source_imports")),
    )


def downgrade() -> None:
    op.drop_table("food_source_imports")
