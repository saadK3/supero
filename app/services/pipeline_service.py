import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.pipeline_run import PipelineRun, PipelineRunStatus, PipelineTriggerType
from app.db.models.user_preference import UserPreference
from app.db.repositories.pipeline_run_repository import (
    create_pipeline_run_record,
    get_pipeline_run_by_id,
)
from app.db.repositories.user_preference_repository import (
    create_user_preference,
    get_user_preference_by_id,
    list_active_user_preferences,
    update_user_preference,
)
from app.schemas.pipeline import PipelineRunCreate, UserPreferenceUpsert


def upsert_user_preference(
    db: Session, payload: UserPreferenceUpsert, preference_id: uuid.UUID | None = None
) -> UserPreference:
    values = {
        "profile_name": payload.profile_name,
        "roles": payload.roles,
        "keywords": payload.keywords,
        "work_modes": [mode.value for mode in payload.work_modes],
        "preferred_locations": payload.preferred_locations,
        "salary_min": payload.salary_min,
        "fresher_friendly": payload.fresher_friendly,
        "companies_to_avoid": payload.companies_to_avoid,
        "is_active": payload.is_active,
    }
    if preference_id is None:
        return create_user_preference(db, values)

    preference = get_user_preference_by_id(db, preference_id)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found."
        )
    return update_user_preference(db, preference, values)


def get_user_preference(db: Session, preference_id: uuid.UUID) -> UserPreference:
    preference = get_user_preference_by_id(db, preference_id)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found."
        )
    return preference


def get_active_preferences(db: Session) -> list[UserPreference]:
    return list_active_user_preferences(db)


def create_pipeline_run(db: Session, payload: PipelineRunCreate) -> PipelineRun:
    preference = get_user_preference_by_id(db, payload.user_preference_id)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found."
        )

    return create_pipeline_run_record(
        db,
        {
            "user_preference_id": payload.user_preference_id,
            "search_job_id": payload.search_job_id,
            "trigger_type": PipelineTriggerType(payload.trigger_type.value),
            "status": PipelineRunStatus.queued,
            "scheduled_key": payload.scheduled_key,
            "stats": {},
        },
    )


def get_pipeline_run(db: Session, pipeline_run_id: uuid.UUID) -> PipelineRun:
    run = get_pipeline_run_by_id(db, pipeline_run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run not found."
        )
    return run

