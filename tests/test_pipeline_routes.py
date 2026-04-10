import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.api.routes import pipeline as pipeline_routes
from app.main import app
from app.schemas.pipeline import TriggerType, WorkMode


def _fake_preference(preference_id: uuid.UUID):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=preference_id,
        profile_name="default",
        roles=["LLM Engineer"],
        keywords=["python"],
        work_modes=["remote"],
        preferred_locations=["US"],
        salary_min=50000,
        fresher_friendly=True,
        companies_to_avoid=["Bad Co"],
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


def test_upsert_preference_route(client, monkeypatch):
    fake_id = uuid.uuid4()
    fake_preference = _fake_preference(fake_id)
    monkeypatch.setattr(
        pipeline_routes,
        "upsert_user_preference",
        lambda db, payload, preference_id=None: fake_preference,
    )
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()

    response = client.post(
        "/api/v1/pipeline/preferences",
        json={
            "profile_name": "default",
            "roles": ["LLM Engineer"],
            "keywords": ["python"],
            "work_modes": [WorkMode.remote.value],
            "preferred_locations": ["US"],
            "salary_min": 50000,
            "fresher_friendly": True,
            "companies_to_avoid": ["Bad Co"],
            "is_active": True,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == str(fake_id)
    assert payload["work_modes"] == ["remote"]
    app.dependency_overrides = {}


def test_get_preference_route(client, monkeypatch):
    fake_id = uuid.uuid4()
    fake_preference = _fake_preference(fake_id)
    monkeypatch.setattr(
        pipeline_routes, "get_user_preference", lambda db, preference_id: fake_preference
    )
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()

    response = client.get(f"/api/v1/pipeline/preferences/{fake_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(fake_id)
    app.dependency_overrides = {}


def test_create_run_route_enqueues_job(client, monkeypatch):
    preference_id = uuid.uuid4()
    run_id = uuid.uuid4()
    fake_run = _fake_run(run_id, preference_id)

    monkeypatch.setattr(pipeline_routes, "create_pipeline_run", lambda db, payload: fake_run)
    monkeypatch.setattr(
        pipeline_routes,
        "enqueue_pipeline_run",
        lambda redis_client, queue_name, pipeline_run_id, trigger_type: 4,
    )
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()
    app.dependency_overrides[pipeline_routes.get_redis] = lambda: object()

    response = client.post(
        "/api/v1/pipeline/runs",
        json={"user_preference_id": str(preference_id), "trigger_type": "manual"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["run"]["id"] == str(run_id)
    assert payload["queue_depth"] == 4
    app.dependency_overrides = {}


def test_get_run_route(client, monkeypatch):
    preference_id = uuid.uuid4()
    run_id = uuid.uuid4()
    fake_run = _fake_run(run_id, preference_id)
    monkeypatch.setattr(pipeline_routes, "get_pipeline_run", lambda db, run_id: fake_run)
    app.dependency_overrides[pipeline_routes.get_db] = lambda: object()

    response = client.get(f"/api/v1/pipeline/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(run_id)
    app.dependency_overrides = {}

