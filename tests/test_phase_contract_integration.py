from app.schemas.orchestration import OrchestrationStartRequest
from app.services.orchestration_service import run_mock_orchestration


def test_phase_2a_2b_2c_contract_chain():
    payload = OrchestrationStartRequest(
        pipeline_run_id="integration-run-001",
        preferences={
            "roles": ["LLM Engineer", "Automation Engineer"],
            "keywords": ["python", "automation"],
            "companies_to_avoid": [],
        },
        config={"max_retries": 1, "node_timeout_seconds": 1.0},
    )
    result = run_mock_orchestration(payload)
    assert result.pipeline_run_id == "integration-run-001"
    assert result.status == "completed"
    assert result.persisted_count >= 1
    assert "finalize" in result.completed_steps

