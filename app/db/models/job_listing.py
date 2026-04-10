import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class RemoteType(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"
    unknown = "unknown"


class ExperienceLevel(str, enum.Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"
    executive = "executive"
    unknown = "unknown"


class JobListing(TimestampMixin, Base):
    __tablename__ = "job_listings"
    __table_args__ = (
        UniqueConstraint("source", "source_url", name="uq_job_listings_source_source_url"),
        Index("ix_job_listings_posted_date", "posted_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    search_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("search_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote_type: Mapped[RemoteType] = mapped_column(
        Enum(RemoteType, name="remote_type"), nullable=False, default=RemoteType.unknown
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experience_level"),
        nullable=False,
        default=ExperienceLevel.unknown,
    )
    salary_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    apply_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    match_reasons: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    search_job = relationship("SearchJob", back_populates="job_listings")
