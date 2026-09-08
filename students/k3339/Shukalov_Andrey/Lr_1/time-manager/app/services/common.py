from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Project, Tag, Task
from app.schemas.common import PatchSchema

Owned = TypeVar("Owned", Project, Task, Tag)


def owned(session: Session, model: type[Owned], item_id: int, user_id: int) -> Owned:
    item = session.scalar(select(model).where(model.id == item_id, model.owner_id == user_id))
    if item is None:
        raise HTTPException(404, "Object not found")
    return item


def commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            409, "Conflicting data or related object changed; reload and retry"
        ) from None


def apply_patch(item: object, data: PatchSchema) -> None:
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(item, name, value)
