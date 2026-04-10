from sqlalchemy.orm import Session

from app.db.models.pipeline_run import PipelineRun, PipelineRunStatus
from app.db.models.user_preference import UserPreference
from app.schemas.pipeline import PipelineRunCreate, UserPreferenceUpsert


def upsert_user_preference(
    db: Session, payload: UserPreferenceUpsert, preference_id: str | None = None
) -> UserPreference:
    preference = None
    if preference_id:
        preference = db.get(UserPreference, preference_id)

    if preference is None:
        preference = UserPreference()
        db.add(preference)

    preference.profile_name = payload.profile_name
    preference.roles = payload.roles
    preference.keywords = payload.keywords
    preference.work_modes = [mode.value for mode in payload.work_modes]
    preference.preferred_locations = payload.preferred_locations
    preference.salary_min = payload.salary_min
    preference.fresher_friendly = payload.fresher_friendly
    preference.companies_to_avoid = payload.companies_to_avoid
    preference.is_active = payload.is_active

    db.commit()
    db.refresh(preference)
    return preference


def create_pipeline_run(db: Session, payload: PipelineRunCreate) -> PipelineRun:
    run = PipelineRun(
        user_preference_id=payload.user_preference_id,
        search_job_id=payload.search_job_id,
        trigger_type=payload.trigger_type.value,
        status=PipelineRunStatus.queued,
        scheduled_key=payload.scheduled_key,
        stats={},
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

