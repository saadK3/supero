import enum
import uuid

from sqlalchemy import Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.base_mixins import TimestampMixin


class ExtractionStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    skipped = "skipped"


class ExtractionLog(TimestampMixin, Base):
    __tablename__ = "extraction_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, name="extraction_status"), nullable=False
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
