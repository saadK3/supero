import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class WorkMode(str, Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"


class TriggerType(str, Enum):
    manual = "manual"
    scheduled = "scheduled"


class PipelineStatus(str, Enum):
    queued = "queued"
    running = "running"
    partial = "partial"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class UserPreferenceUpsert(BaseModel):
    profile_name: str = Field(min_length=1, max_length=120)
    roles: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    work_modes: list[WorkMode] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    salary_min: int | None = Field(default=None, ge=0)
    fresher_friendly: bool = True
    companies_to_avoid: list[str] = Field(default_factory=list)
    is_active: bool = True


class UserPreferenceRead(BaseModel):
    id: uuid.UUID
    profile_name: str
    roles: list[str]
    keywords: list[str]
    work_modes: list[WorkMode]
    preferred_locations: list[str]
    salary_min: int | None
    fresher_friendly: bool
    companies_to_avoid: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PipelineRunCreate(BaseModel):
    user_preference_id: uuid.UUID
    trigger_type: TriggerType = TriggerType.manual
    search_job_id: uuid.UUID | None = None
    scheduled_key: str | None = Field(default=None, max_length=80)


class PipelineRunRead(BaseModel):
    id: uuid.UUID
    user_preference_id: uuid.UUID
    search_job_id: uuid.UUID | None
    status: PipelineStatus
    trigger_type: TriggerType
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    stats: dict
    scheduled_key: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PipelineRunEnqueueResponse(BaseModel):
    run: PipelineRunRead
    queue_name: str
    queue_depth: int

