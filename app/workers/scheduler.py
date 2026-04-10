import argparse
import time

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.db.session import SessionLocal, get_redis
from app.schemas.pipeline import PipelineRunCreate, TriggerType
from app.services.pipeline_service import create_pipeline_run, get_active_preferences
from app.services.queue_service import enqueue_pipeline_run


def run_scheduled_cycle() -> int:
    db = SessionLocal()
    redis_client = get_redis()
    queued_count = 0
    try:
        preferences = get_active_preferences(db)
        for preference in preferences:
            run = create_pipeline_run(
                db,
                PipelineRunCreate(
                    user_preference_id=preference.id,
                    trigger_type=TriggerType.scheduled,
                    scheduled_key=f"interval-{settings.scheduler_interval_minutes}m",
                ),
            )
            enqueue_pipeline_run(
                redis_client=redis_client,
                queue_name=settings.pipeline_queue_name,
                pipeline_run_id=run.id,
                trigger_type=TriggerType.scheduled.value,
            )
            queued_count += 1
        logger.info("Scheduler cycle complete. queued_runs=%s", queued_count)
        return queued_count
    finally:
        db.close()


def start_scheduler_loop() -> None:
    configure_logging()
    logger.info(
        "Scheduler started. interval_minutes=%s queue=%s",
        settings.scheduler_interval_minutes,
        settings.pipeline_queue_name,
    )
    while True:
        run_scheduled_cycle()
        time.sleep(settings.scheduler_interval_minutes * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline scheduler worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one scheduler cycle and exit.",
    )
    args = parser.parse_args()

    if not settings.scheduler_enabled and not args.once:
        raise SystemExit(
            "Scheduler is disabled. Set SCHEDULER_ENABLED=true or use --once."
        )

    if args.once:
        configure_logging()
        run_scheduled_cycle()
        return

    start_scheduler_loop()


if __name__ == "__main__":
    main()

