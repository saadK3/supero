import uuid

from app.schemas.pipeline import PipelineRunCreate, TriggerType, UserPreferenceUpsert, WorkMode


def test_user_preference_contract_parses_work_modes():
    payload = UserPreferenceUpsert(
        profile_name="fresh-grad-remote",
        roles=["AI Solutions Engineer", "LLM Engineer"],
        keywords=["python", "langgraph"],
        work_modes=[WorkMode.remote, "hybrid"],
        preferred_locations=["US", "Canada"],
        salary_min=60000,
        fresher_friendly=True,
        companies_to_avoid=["Example Corp"],
    )

    assert payload.profile_name == "fresh-grad-remote"
    assert payload.work_modes == [WorkMode.remote, WorkMode.hybrid]
    assert payload.salary_min == 60000


def test_pipeline_run_create_defaults_to_manual_trigger():
    payload = PipelineRunCreate(user_preference_id=uuid.uuid4())
    assert payload.trigger_type == TriggerType.manual
    assert payload.search_job_id is None

