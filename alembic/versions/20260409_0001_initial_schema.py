"""Initial schema for phase 1 foundation.

Revision ID: 20260409_0001
Revises:
Create Date: 2026-04-09
"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260409_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


search_job_status = sa.Enum(
    "pending", "running", "completed", "failed", name="search_job_status"
)
remote_type = sa.Enum("remote", "hybrid", "onsite", "unknown", name="remote_type")
experience_level = sa.Enum(
    "intern", "junior", "mid", "senior", "lead", "executive", "unknown", name="experience_level"
)
extraction_status = sa.Enum("success", "failed", "skipped", name="extraction_status")


def upgrade() -> None:
    op.create_table(
        "search_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("status", search_job_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_search_jobs")),
    )

    op.create_table(
        "job_listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("search_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("remote_type", remote_type, nullable=False),
        sa.Column("experience_level", experience_level, nullable=False),
        sa.Column("salary_text", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("posted_date", sa.Date(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["search_job_id"],
            ["search_jobs.id"],
            name=op.f("fk_job_listings_search_job_id_search_jobs"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_listings")),
        sa.UniqueConstraint(
            "source", "source_url", name="uq_job_listings_source_source_url"
        ),
    )
    op.create_index(
        "ix_job_listings_posted_date", "job_listings", ["posted_date"], unique=False
    )

    op.create_table(
        "extraction_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("status", extraction_status, nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_extraction_logs")),
    )
    op.create_index(
        op.f("ix_extraction_logs_source_url"),
        "extraction_logs",
        ["source_url"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_extraction_logs_source_url"), table_name="extraction_logs")
    op.drop_table("extraction_logs")
    op.drop_index("ix_job_listings_posted_date", table_name="job_listings")
    op.drop_table("job_listings")
    op.drop_table("search_jobs")

    bind = op.get_bind()
    extraction_status.drop(bind, checkfirst=True)
    experience_level.drop(bind, checkfirst=True)
    remote_type.drop(bind, checkfirst=True)
    search_job_status.drop(bind, checkfirst=True)
