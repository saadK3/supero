from __future__ import annotations

from app.orchestration.adapters.mock_adapters import (
    MockExtractionAdapter,
    MockPersistenceAdapter,
    MockResearchAdapter,
)
from app.orchestration.graph import build_pipeline_graph
from app.orchestration.state import OrchestrationConfig, OrchestrationState, create_initial_state


def run_orchestration(
    state: OrchestrationState,
    *,
    research_adapter=None,
    extraction_adapter=None,
    persistence_adapter=None,
) -> OrchestrationState:
    graph = build_pipeline_graph(
        research_adapter=research_adapter or MockResearchAdapter(),
        extraction_adapter=extraction_adapter or MockExtractionAdapter(),
        persistence_adapter=persistence_adapter or MockPersistenceAdapter(),
    )
    return graph.invoke(state)


def run_orchestration_from_scratch(
    pipeline_run_id: str,
    *,
    config: OrchestrationConfig | None = None,
    preferences: dict | None = None,
) -> OrchestrationState:
    state = create_initial_state(
        pipeline_run_id,
        config=config,
        preferences=preferences,
    )
    return run_orchestration(state)

