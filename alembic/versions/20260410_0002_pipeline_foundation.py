"""Add pipeline foundation entities and extend job listings.

Revision ID: 20260410_0002
Revises: 20260409_0001
Create Date: 2026-04-10
"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260410_0002"
down_revision: Union[str, None] = "20260409_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


pipeline_run_status = postgresql.ENUM(
    "queued",
    "running",
    "partial",
    "completed",
    "failed",
    "cancelled",
    name="pipeline_run_status",
    create_type=False,
)
pipeline_trigger_type = postgresql.ENUM(
    "manual", "scheduled", name="pipeline_trigger_type", create_type=False
)
candidate_url_status = postgresql.ENUM(
    "pending",
    "extracted",
    "failed",
    "skipped",
    name="candidate_url_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE pipeline_run_status AS ENUM
            ('queued', 'running', 'partial', 'completed', 'failed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE pipeline_trigger_type AS ENUM ('manual', 'scheduled');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE candidate_url_status AS ENUM ('pending', 'extracted', 'failed', 'skipped');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END$$;
        """
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_name", sa.String(length=120), nullable=False),
        sa.Column("roles", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("work_modes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "preferred_locations", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("fresher_friendly", sa.Boolean(), nullable=False),
        sa.Column("companies_to_avoid", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_preferences")),
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_preference_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("search_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            pipeline_run_status,
            server_default="queued",
            nullable=False,
        ),
        sa.Column(
            "trigger_type",
            pipeline_trigger_type,
            server_default="manual",
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "stats",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("scheduled_key", sa.String(length=80), nullable=True),
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
            name=op.f("fk_pipeline_runs_search_job_id_search_jobs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_preference_id"],
            ["user_preferences.id"],
            name=op.f("fk_pipeline_runs_user_preference_id_user_preferences"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pipeline_runs")),
    )

    op.create_table(
        "candidate_urls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pipeline_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("discovery_query", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            candidate_url_status,
            server_default="pending",
            nullable=False,
        ),
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
            ["pipeline_run_id"],
            ["pipeline_runs.id"],
            name=op.f("fk_candidate_urls_pipeline_run_id_pipeline_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidate_urls")),
        sa.UniqueConstraint(
            "pipeline_run_id",
            "canonical_url",
            name="uq_candidate_urls_pipeline_run_canonical_url",
        ),
        sa.UniqueConstraint(
            "pipeline_run_id",
            "source_url",
            name="uq_candidate_urls_pipeline_run_source_url",
        ),
    )
    op.create_index("ix_candidate_urls_status", "candidate_urls", ["status"], unique=False)

    op.add_column("job_listings", sa.Column("apply_url", sa.Text(), nullable=True))
    op.add_column("job_listings", sa.Column("fit_score", sa.Numeric(precision=5, scale=2)))
    op.add_column(
        "job_listings",
        sa.Column(
            "match_reasons",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("job_listings", "match_reasons")
    op.drop_column("job_listings", "fit_score")
    op.drop_column("job_listings", "apply_url")

    op.drop_index("ix_candidate_urls_status", table_name="candidate_urls")
    op.drop_table("candidate_urls")
    op.drop_table("pipeline_runs")
    op.drop_table("user_preferences")

    op.execute("DROP TYPE IF EXISTS candidate_url_status")
    op.execute("DROP TYPE IF EXISTS pipeline_trigger_type")
    op.execute("DROP TYPE IF EXISTS pipeline_run_status")
