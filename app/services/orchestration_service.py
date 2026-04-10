from app.orchestration.adapters.mock_adapters import (
    MockExtractionAdapter,
    MockPersistenceAdapter,
    MockResearchAdapter,
)
from app.orchestration.runner import run_orchestration
from app.orchestration.state import create_initial_state
from app.schemas.orchestration import OrchestrationRunResponse, OrchestrationStartRequest


def run_mock_orchestration(payload: OrchestrationStartRequest) -> OrchestrationRunResponse:
    initial = create_initial_state(
        pipeline_run_id=payload.pipeline_run_id,
        config={
            "max_retries": payload.config.max_retries,
            "node_timeout_seconds": payload.config.node_timeout_seconds,
        },
        preferences=payload.preferences,
    )
    final_state = run_orchestration(
        initial,
        research_adapter=MockResearchAdapter(),
        extraction_adapter=MockExtractionAdapter(),
        persistence_adapter=MockPersistenceAdapter(),
    )
    return OrchestrationRunResponse(
        pipeline_run_id=final_state["pipeline_run_id"],
        status=final_state["status"],
        current_step=final_state["current_step"],
        persisted_count=final_state["persisted_count"],
        completed_steps=final_state["completed_steps"],
        errors=final_state["errors"],
    )

