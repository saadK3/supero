import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class PipelineRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    partial = "partial"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PipelineTriggerType(str, enum.Enum):
    manual = "manual"
    scheduled = "scheduled"


class PipelineRun(TimestampMixin, Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_preference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_preferences.id", ondelete="CASCADE"),
        nullable=False,
    )
    search_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("search_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[PipelineRunStatus] = mapped_column(
        Enum(PipelineRunStatus, name="pipeline_run_status"),
        nullable=False,
        default=PipelineRunStatus.queued,
    )
    trigger_type: Mapped[PipelineTriggerType] = mapped_column(
        Enum(PipelineTriggerType, name="pipeline_trigger_type"),
        nullable=False,
        default=PipelineTriggerType.manual,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    scheduled_key: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user_preference = relationship("UserPreference", back_populates="pipeline_runs")
    search_job = relationship("SearchJob", back_populates="pipeline_runs")
    candidate_urls = relationship("CandidateURL", back_populates="pipeline_run")

