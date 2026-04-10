import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.api.routes import pipeline as pipeline_routes
from app.main import app
from app.schemas.pipeline import TriggerType


def _fake_preference(preference_id: uuid.UUID):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=preference_id,
        profile_name="default",
        roles=["LLM Engineer"],
        keywords=["python"],
        work_modes=["remote"],
        preferred_locations=["US"],
        salary_min=60000,
        fresher_friendly=True,
        companies_to_avoid=[],
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def _fake_run(run_id: uuid.UUID, preference_id: uuid.UUID):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=run_id,
        user_preference_id=preference_id,
        search_job_id=None,
        status="queued",
        trigger_type=TriggerType.manual,
        started_at=None,
        finished_at=None,
        error_message=None,
        stats={},
        scheduled_key=None,
        created_at=now,
        updated_at=now,
    )


def test_create_preference_endpoint(client, monkeypatch):
    fake_id = uuid.uuid4()
    monkeypatch.setattr(
        pipeline_routes,
        "upsert_user_preference",
        lambda db, payload, preference_id=None: _fake_preference(fake_id),
    )
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()

    response = client.post(
        "/api/v1/pipeline/preferences",
        json={
            "profile_name": "default",
            "roles": ["LLM Engineer"],
            "keywords": ["python"],
            "work_modes": ["remote"],
            "preferred_locations": ["US"],
            "salary_min": 60000,
            "fresher_friendly": True,
            "companies_to_avoid": [],
            "is_active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["id"] == str(fake_id)
    app.dependency_overrides = {}


def test_create_pipeline_run_endpoint_enqueues(client, monkeypatch):
    pref_id = uuid.uuid4()
    run_id = uuid.uuid4()
    monkeypatch.setattr(
        pipeline_routes,
        "create_pipeline_run",
        lambda db, payload: _fake_run(run_id, pref_id),
    )
    monkeypatch.setattr(
        pipeline_routes,
        "enqueue_pipeline_run",
        lambda redis_client, queue_name, pipeline_run_id, trigger_type: 3,
    )
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()
    app.dependency_overrides[pipeline_routes.get_redis] = lambda: object()

    response = client.post(
        "/api/v1/pipeline/runs",
        json={"user_preference_id": str(pref_id), "trigger_type": "manual"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["run"]["id"] == str(run_id)
    assert payload["queue_depth"] == 3
    app.dependency_overrides = {}


def test_orchestration_mock_run_endpoint(client, monkeypatch):
    monkeypatch.setattr(
        pipeline_routes,
        "run_mock_orchestration",
        lambda payload: {
            "pipeline_run_id": payload.pipeline_run_id,
            "status": "completed",
            "current_step": "finalize",
            "persisted_count": 2,
            "completed_steps": ["load_preferences", "finalize"],
            "errors": [],
        },
    )

    response = client.post(
        "/api/v1/pipeline/orchestration/mock-run",
        json={"pipeline_run_id": "run-e2e", "preferences": {}, "config": {}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

