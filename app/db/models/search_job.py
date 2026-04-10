import enum
import uuid

from sqlalchemy import Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class SearchJobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class SearchJob(TimestampMixin, Base):
    __tablename__ = "search_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SearchJobStatus] = mapped_column(
        Enum(SearchJobStatus, name="search_job_status"),
        nullable=False,
        default=SearchJobStatus.pending,
    )

    job_listings = relationship("JobListing", back_populates="search_job")
    pipeline_runs = relationship("PipelineRun", back_populates="search_job")
