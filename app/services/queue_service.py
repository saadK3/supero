import json
import uuid
from datetime import datetime, timezone

from redis import Redis


def enqueue_pipeline_run(
    redis_client: Redis,
    queue_name: str,
    pipeline_run_id: uuid.UUID,
    trigger_type: str,
) -> int:
    payload = {
        "pipeline_run_id": str(pipeline_run_id),
        "trigger_type": trigger_type,
        "enqueued_at": datetime.now(timezone.utc).isoformat(),
    }
    return int(redis_client.rpush(queue_name, json.dumps(payload)))

