from datetime import datetime

from pydantic import BaseModel, Field


class OrchestrationConfigSchema(BaseModel):
    max_retries: int = Field(default=2, ge=0, le=10)
    node_timeout_seconds: float = Field(default=5.0, gt=0.0, le=120.0)


class OrchestrationStartRequest(BaseModel):
    pipeline_run_id: str = Field(min_length=1, max_length=80)
    preferences: dict = Field(default_factory=dict)
    config: OrchestrationConfigSchema = Field(default_factory=OrchestrationConfigSchema)


class OrchestrationErrorSchema(BaseModel):
    node: str
    error_type: str
    message: str
    retryable: bool
    attempts: int
    timestamp: datetime


class OrchestrationRunResponse(BaseModel):
    pipeline_run_id: str
    status: str
    current_step: str | None
    persisted_count: int
    completed_steps: list[str]
    errors: list[OrchestrationErrorSchema]

