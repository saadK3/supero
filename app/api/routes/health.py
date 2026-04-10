from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from redis import Redis
from sqlalchemy.orm import Session

from app.db.session import get_db, get_redis
from app.schemas.health import HealthResponse, ServiceStatus
from app.services.health_service import check_database, check_redis

router = APIRouter(prefix="/health")


@router.get("/live", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def liveness_check() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/ready", response_model=HealthResponse)
def readiness_check(
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
) -> HealthResponse:
    db_ok = check_database(db)
    redis_ok = check_redis(redis_client)

    overall_status = "ok" if db_ok and redis_ok else "degraded"
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        services=ServiceStatus(
            database="ok" if db_ok else "down",
            redis="ok" if redis_ok else "down",
        ),
    )

