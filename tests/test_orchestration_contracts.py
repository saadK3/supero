from app.schemas.orchestration import OrchestrationRunResponse, OrchestrationStartRequest


def test_orchestration_start_contract_defaults():
    payload = OrchestrationStartRequest(pipeline_run_id="run-123")
    assert payload.config.max_retries == 2
    assert payload.config.node_timeout_seconds == 5.0
    assert payload.preferences == {}


def test_orchestration_response_contract():
    response = OrchestrationRunResponse(
        pipeline_run_id="run-123",
        status="completed",
        current_step="finalize",
        persisted_count=3,
        completed_steps=["load_preferences", "finalize"],
        errors=[],
    )
    assert response.pipeline_run_id == "run-123"
    assert response.status == "completed"

