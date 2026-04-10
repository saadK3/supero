import uuid
from types import SimpleNamespace

from app.workers import scheduler


def test_scheduler_cycle_queues_active_preferences(monkeypatch):
    prefs = [SimpleNamespace(id=uuid.uuid4()), SimpleNamespace(id=uuid.uuid4())]
    queued_items = []

    class FakeDB:
        def close(self):
            return None

    monkeypatch.setattr(scheduler, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(scheduler, "get_redis", lambda: object())
    monkeypatch.setattr(scheduler, "get_active_preferences", lambda db: prefs)

    def fake_create_pipeline_run(db, payload):
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(scheduler, "create_pipeline_run", fake_create_pipeline_run)

    def fake_enqueue(redis_client, queue_name, pipeline_run_id, trigger_type):
        queued_items.append((queue_name, pipeline_run_id, trigger_type))
        return len(queued_items)

    monkeypatch.setattr(scheduler, "enqueue_pipeline_run", fake_enqueue)

    count = scheduler.run_scheduled_cycle()
    assert count == 2
    assert len(queued_items) == 2
    assert all(item[2] == "scheduled" for item in queued_items)

