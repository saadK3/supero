from app.orchestration.adapters.mock_adapters import (
    MockExtractionAdapter,
    MockPersistenceAdapter,
    MockResearchAdapter,
)
from app.orchestration.runner import run_orchestration, run_orchestration_from_scratch
from app.orchestration.state import create_initial_state


def test_graph_runs_end_to_end_with_mock_adapters():
    state = run_orchestration_from_scratch(
        "run-001",
        preferences={
            "roles": ["LLM Engineer", "Automation Engineer"],
            "keywords": ["python", "automation"],
            "companies_to_avoid": [],
        },
    )
    assert state["status"] == "completed"
    assert "finalize" in state["completed_steps"]
    assert state["persisted_count"] >= 1
    assert not state["errors"]


def test_graph_retries_then_succeeds():
    initial = create_initial_state(
        "run-002",
        config={"max_retries": 2, "node_timeout_seconds": 1.0},
        preferences={"roles": ["LLM Engineer"], "keywords": ["python"]},
    )
    state = run_orchestration(
        initial,
        research_adapter=MockResearchAdapter(fail_times=1),
        extraction_adapter=MockExtractionAdapter(),
        persistence_adapter=MockPersistenceAdapter(),
    )
    assert state["status"] == "completed"
    assert state["persisted_count"] >= 1


def test_graph_timeout_moves_to_structured_error_path():
    initial = create_initial_state(
        "run-003",
        config={"max_retries": 1, "node_timeout_seconds": 0.01},
        preferences={"roles": ["LLM Engineer"], "keywords": ["python"]},
    )
    state = run_orchestration(
        initial,
        research_adapter=MockResearchAdapter(sleep_seconds=0.1),
        extraction_adapter=MockExtractionAdapter(),
        persistence_adapter=MockPersistenceAdapter(),
    )
    assert state["status"] == "failed"
    assert state["errors"]
    assert state["errors"][0]["node"] == "research_agent"
    assert "error_handler" in state["completed_steps"]
    assert "finalize" in state["completed_steps"]


def test_graph_resumes_from_mid_pipeline_state():
    resume_state = create_initial_state(
        "run-004",
        current_step="extraction_agent",
        completed_steps=["load_preferences", "research_agent", "dedupe_urls"],
        preferences={"roles": ["LLM Engineer"], "keywords": ["python"]},
        candidate_urls=[
            {
                "source": "mock_board",
                "source_url": "https://jobs.example.com/llm-engineer-1",
                "canonical_url": "https://jobs.example.com/llm-engineer-1",
                "discovery_query": "LLM Engineer",
            }
        ],
    )
    state = run_orchestration(
        resume_state,
        research_adapter=MockResearchAdapter(),
        extraction_adapter=MockExtractionAdapter(),
        persistence_adapter=MockPersistenceAdapter(),
    )
    assert state["status"] == "completed"
    assert "extraction_agent" in state["completed_steps"]
    assert state["persisted_count"] == 1

