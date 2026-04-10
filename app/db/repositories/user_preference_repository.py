import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user_preference import UserPreference


def get_user_preference_by_id(db: Session, preference_id: uuid.UUID) -> UserPreference | None:
    return db.get(UserPreference, preference_id)


def list_active_user_preferences(db: Session) -> list[UserPreference]:
    stmt = select(UserPreference).where(UserPreference.is_active.is_(True))
    return list(db.scalars(stmt))


def create_user_preference(db: Session, values: dict) -> UserPreference:
    preference = UserPreference(**values)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def update_user_preference(db: Session, preference: UserPreference, values: dict) -> UserPreference:
    for key, value in values.items():
        setattr(preference, key, value)
    db.commit()
    db.refresh(preference)
    return preference

