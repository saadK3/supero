from app.api.routes import health as health_routes
from app.main import app


def test_liveness_returns_ok(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "timestamp" in payload


def test_readiness_returns_ok_when_dependencies_are_up(client, monkeypatch):
    monkeypatch.setattr(health_routes, "check_database", lambda db: True)
    monkeypatch.setattr(health_routes, "check_redis", lambda redis_client: True)

    app.dependency_overrides[health_routes.get_db] = lambda: object()
    app.dependency_overrides[health_routes.get_redis] = lambda: object()

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["services"] == {"database": "ok", "redis": "ok"}

    app.dependency_overrides = {}


def test_readiness_returns_degraded_when_one_dependency_is_down(client, monkeypatch):
    monkeypatch.setattr(health_routes, "check_database", lambda db: True)
    monkeypatch.setattr(health_routes, "check_redis", lambda redis_client: False)

    app.dependency_overrides[health_routes.get_db] = lambda: object()
    app.dependency_overrides[health_routes.get_redis] = lambda: object()

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["services"] == {"database": "ok", "redis": "down"}

    app.dependency_overrides = {}
