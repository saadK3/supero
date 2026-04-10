import uuid

from fastapi import APIRouter, Depends, Query, status
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db, get_redis
from app.schemas.pipeline import (
    PipelineRunCreate,
    PipelineRunEnqueueResponse,
    PipelineRunRead,
    UserPreferenceRead,
    UserPreferenceUpsert,
)
from app.services.pipeline_service import (
    create_pipeline_run,
    get_pipeline_run,
    get_user_preference,
    upsert_user_preference,
)
from app.services.queue_service import enqueue_pipeline_run

router = APIRouter(prefix="/pipeline")


@router.post(
    "/preferences",
    response_model=UserPreferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def upsert_preference(
    payload: UserPreferenceUpsert,
    preference_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> UserPreferenceRead:
    preference = upsert_user_preference(db, payload, preference_id=preference_id)
    return UserPreferenceRead.model_validate(preference, from_attributes=True)


@router.get("/preferences/{preference_id}", response_model=UserPreferenceRead)
def get_preference(preference_id: uuid.UUID, db: Session = Depends(get_db)) -> UserPreferenceRead:
    preference = get_user_preference(db, preference_id)
    return UserPreferenceRead.model_validate(preference, from_attributes=True)


@router.post(
    "/runs",
    response_model=PipelineRunEnqueueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    payload: PipelineRunCreate,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
) -> PipelineRunEnqueueResponse:
    run = create_pipeline_run(db, payload)
    queue_depth = enqueue_pipeline_run(
        redis_client=redis_client,
        queue_name=settings.pipeline_queue_name,
        pipeline_run_id=run.id,
        trigger_type=run.trigger_type.value,
    )
    return PipelineRunEnqueueResponse(
        run=PipelineRunRead.model_validate(run, from_attributes=True),
        queue_name=settings.pipeline_queue_name,
        queue_depth=queue_depth,
    )


@router.get("/runs/{run_id}", response_model=PipelineRunRead)
def get_run(run_id: uuid.UUID, db: Session = Depends(get_db)) -> PipelineRunRead:
    run = get_pipeline_run(db, run_id)
    return PipelineRunRead.model_validate(run, from_attributes=True)

