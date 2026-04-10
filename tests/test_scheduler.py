import uuid
from types import SimpleNamespace

from app.workers import scheduler


def test_run_scheduled_cycle_queues_all_active_preferences(monkeypatch):
    prefs = [SimpleNamespace(id=uuid.uuid4()), SimpleNamespace(id=uuid.uuid4())]
    created_runs = []
    enqueued = []

    class FakeDB:
        def close(self):
            return None

    monkeypatch.setattr(scheduler, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(scheduler, "get_redis", lambda: object())
    monkeypatch.setattr(scheduler, "get_active_preferences", lambda db: prefs)

    def fake_create_pipeline_run(db, payload):
        run = SimpleNamespace(id=uuid.uuid4())
        created_runs.append((payload.user_preference_id, payload.trigger_type.value))
        return run

    monkeypatch.setattr(scheduler, "create_pipeline_run", fake_create_pipeline_run)

    def fake_enqueue(redis_client, queue_name, pipeline_run_id, trigger_type):
        enqueued.append((queue_name, pipeline_run_id, trigger_type))
        return 1

    monkeypatch.setattr(scheduler, "enqueue_pipeline_run", fake_enqueue)

    queued_count = scheduler.run_scheduled_cycle()
    assert queued_count == 2
    assert len(created_runs) == 2
    assert all(trigger == "scheduled" for _, trigger in created_runs)
    assert len(enqueued) == 2

