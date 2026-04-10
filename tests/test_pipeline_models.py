from app.db.models.job_listing import JobListing
from app.db.models.pipeline_run import PipelineRun
from app.db.models.user_preference import UserPreference


def test_pipeline_models_expose_expected_columns():
    assert hasattr(UserPreference, "roles")
    assert hasattr(PipelineRun, "status")
    assert hasattr(PipelineRun, "trigger_type")
    assert hasattr(JobListing, "apply_url")
    assert hasattr(JobListing, "fit_score")
    assert hasattr(JobListing, "match_reasons")

