from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, TypedDict


NodeName = Literal[
    "load_preferences",
    "research_agent",
    "dedupe_urls",
    "extraction_agent",
    "filter_rules",
    "dedupe_jobs",
    "rank_jobs",
    "persist",
    "finalize",
    "error_handler",
]


class PipelineError(TypedDict):
    node: NodeName
    error_type: str
    message: str
    retryable: bool
    attempts: int
    timestamp: str


class OrchestrationConfig(TypedDict):
    max_retries: int
    node_timeout_seconds: float


class OrchestrationState(TypedDict):
    pipeline_run_id: str
    current_step: NodeName | None
    completed_steps: list[NodeName]
    status: str
    preferences: dict
    candidate_urls: list[dict]
    extracted_jobs: list[dict]
    filtered_jobs: list[dict]
    deduped_jobs: list[dict]
    ranked_jobs: list[dict]
    persisted_count: int
    errors: list[PipelineError]
    config: OrchestrationConfig


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_initial_state(
    pipeline_run_id: str,
    *,
    config: OrchestrationConfig | None = None,
    current_step: NodeName | None = None,
    completed_steps: list[NodeName] | None = None,
    preferences: dict | None = None,
    candidate_urls: list[dict] | None = None,
    extracted_jobs: list[dict] | None = None,
    filtered_jobs: list[dict] | None = None,
    deduped_jobs: list[dict] | None = None,
    ranked_jobs: list[dict] | None = None,
) -> OrchestrationState:
    return OrchestrationState(
        pipeline_run_id=pipeline_run_id,
        current_step=current_step,
        completed_steps=completed_steps or [],
        status="running",
        preferences=preferences or {},
        candidate_urls=candidate_urls or [],
        extracted_jobs=extracted_jobs or [],
        filtered_jobs=filtered_jobs or [],
        deduped_jobs=deduped_jobs or [],
        ranked_jobs=ranked_jobs or [],
        persisted_count=0,
        errors=[],
        config=config or OrchestrationConfig(max_retries=2, node_timeout_seconds=5.0),
    )

