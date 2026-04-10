import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class CandidateURLStatus(str, enum.Enum):
    pending = "pending"
    extracted = "extracted"
    failed = "failed"
    skipped = "skipped"


class CandidateURL(TimestampMixin, Base):
    __tablename__ = "candidate_urls"
    __table_args__ = (
        UniqueConstraint(
            "pipeline_run_id",
            "canonical_url",
            name="uq_candidate_urls_pipeline_run_canonical_url",
        ),
        UniqueConstraint(
            "pipeline_run_id", "source_url", name="uq_candidate_urls_pipeline_run_source_url"
        ),
        Index("ix_candidate_urls_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pipeline_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    discovery_query: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[CandidateURLStatus] = mapped_column(
        Enum(CandidateURLStatus, name="candidate_url_status"),
        nullable=False,
        default=CandidateURLStatus.pending,
    )

    pipeline_run = relationship("PipelineRun", back_populates="candidate_urls")

