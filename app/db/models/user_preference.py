import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class UserPreference(TimestampMixin, Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_name: Mapped[str] = mapped_column(String(120), nullable=False, default="default")
    roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    keywords: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    work_modes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    salary_min: Mapped[int | None] = mapped_column(nullable=True)
    fresher_friendly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    companies_to_avoid: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    pipeline_runs = relationship("PipelineRun", back_populates="user_preference")

