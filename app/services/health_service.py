from sqlalchemy import text
from sqlalchemy.orm import Session

from redis import Redis


def check_database(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_redis(redis_client: Redis) -> bool:
    try:
        return bool(redis_client.ping())
    except Exception:
        return False

