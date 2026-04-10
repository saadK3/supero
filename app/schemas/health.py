from datetime import datetime

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    database: str = Field(examples=["ok", "down"])
    redis: str = Field(examples=["ok", "down"])


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok", "degraded"])
    timestamp: datetime
    services: ServiceStatus | None = None

