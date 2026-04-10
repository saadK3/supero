# Intelligent Job Discovery SaaS (Phase 2B)

Current status:
- Backend foundation (Phase 1) completed.
- Pipeline foundation schema/contracts (Phase 2A) completed.
- Input + trigger layer (Phase 2B) completed.

Phase 2B includes:
- Preference APIs (create/update + fetch)
- Pipeline run APIs (create + fetch)
- Redis queue enqueue on run creation
- Separate scheduler worker scaffold (manual one-off or interval loop)
- Tests for routes, contracts, scheduler behavior

Out of scope for now:
- LangGraph runtime graph execution
- Playwright crawling/extraction
- Filtering, dedupe, ranking execution engine

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic + pydantic-settings
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Pytest

## Core Entities
- `SearchJob`
- `JobListing` (extended with `apply_url`, `fit_score`, `match_reasons`)
- `ExtractionLog`
- `UserPreference`
- `PipelineRun`
- `CandidateURL`

## Local Setup
1. Create and activate a virtual environment.

PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.
```powershell
pip install -e .[dev]
```

3. Copy environment template.
```powershell
Copy-Item .env.example .env
```

4. Ensure PostgreSQL and Redis are running locally, then update `.env` values if needed.
Required Phase 2B env keys:
```env
PIPELINE_QUEUE_NAME=pipeline:run_queue
SCHEDULER_ENABLED=false
SCHEDULER_INTERVAL_MINUTES=720
```

5. Run migrations.
```powershell
alembic upgrade head
```

6. Start the API server.
```powershell
uvicorn app.main:app --reload
```

Server will run on `http://127.0.0.1:8000`.

## Endpoint Checks
From another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/live
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

Create/update preferences:
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/pipeline/preferences" `
  -ContentType "application/json" `
  -Body '{"profile_name":"default","roles":["LLM Engineer"],"keywords":["python","langgraph"],"work_modes":["remote"],"preferred_locations":["US"],"salary_min":50000,"fresher_friendly":true,"companies_to_avoid":[],"is_active":true}'
```

Create pipeline run:
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/pipeline/runs" `
  -ContentType "application/json" `
  -Body '{"user_preference_id":"<preference-uuid>","trigger_type":"manual"}'
```

Get run:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/pipeline/runs/<run-uuid>
```

Run one scheduler cycle:
```powershell
python -m app.workers.scheduler --once
```

Swagger docs:
- `http://127.0.0.1:8000/docs`

## Run Tests
```powershell
pytest
```

## Notes for Next Phase
- Next is Phase 2C: LangGraph orchestration skeleton wired to queued pipeline runs.
