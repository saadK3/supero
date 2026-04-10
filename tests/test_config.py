from app.core.config import Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)
    assert settings.app_name == "Job Discovery SaaS API"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.redis_url.startswith("redis://")
    assert settings.pipeline_queue_name == "pipeline:run_queue"
    assert settings.scheduler_enabled is False
    assert settings.scheduler_interval_minutes == 720
