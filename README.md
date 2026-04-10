# Intelligent Job Discovery SaaS - Phase 1

Phase 1 delivers a production-minded backend foundation for an agentic job discovery SaaS.

This phase includes:
- FastAPI scaffold with versioned API routing
- Health endpoints (`live` and `ready`)
- Environment-based configuration with Pydantic Settings
- PostgreSQL + SQLAlchemy setup
- Redis client setup
- Core SQLAlchemy models for future workflows
- Alembic migrations
- Structured logging
- Basic tests

This phase intentionally does **not** include scraping, extraction pipelines, LangGraph orchestration, frontend, or auth flows.

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic + pydantic-settings
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Pytest

## Project Structure
```text
.
|-- alembic/
|   |-- versions/
|   |   `-- 20260409_0001_initial_schema.py
|   |-- env.py
|   `-- script.py.mako
|-- app/
|   |-- api/
|   |   `-- routes/
|   |       `-- health.py
|   |-- core/
|   |   |-- config.py
|   |   `-- logging.py
|   |-- db/
|   |   |-- models/
|   |   |   |-- base_mixins.py
|   |   |   |-- extraction_log.py
|   |   |   |-- job_listing.py
|   |   |   `-- search_job.py
|   |   |-- base.py
|   |   `-- session.py
|   |-- schemas/
|   |   `-- health.py
|   |-- services/
|   |   `-- health_service.py
|   `-- main.py
|-- tests/
|   |-- test_config.py
|   `-- test_health.py
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- pyproject.toml
`-- README.md
```

## Core Entities (Phase 1)
- `SearchJob`
  - Tracks user search requests and lifecycle state.
- `JobListing`
  - Stores normalized listing metadata plus summary/raw text.
  - Includes unique constraint on `(source, source_url)` for deduplication readiness.
- `ExtractionLog`
  - Tracks extraction outcomes per URL.

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

Swagger docs:
- `http://127.0.0.1:8000/docs`

## Run Tests
```powershell
pytest
```

## Notes for Future Phases
- Architecture already separates API routes, service layer, core config, and DB layer.
- Schema and migrations are ready for future agentic orchestration and scraping modules.
- Repo structure is Docker-friendly for a later phase without forcing Docker now.

