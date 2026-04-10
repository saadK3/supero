import uuid

from sqlalchemy.orm import Session

from app.db.models.pipeline_run import PipelineRun


def get_pipeline_run_by_id(db: Session, pipeline_run_id: uuid.UUID) -> PipelineRun | None:
    return db.get(PipelineRun, pipeline_run_id)


def create_pipeline_run_record(db: Session, values: dict) -> PipelineRun:
    run = PipelineRun(**values)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

