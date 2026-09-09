from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TimeEntry, User


def get_entry(session: Session, entry_id: int, user_id: int) -> TimeEntry:
    item = session.scalar(
        select(TimeEntry).join(Task).where(TimeEntry.id == entry_id, Task.owner_id == user_id)
    )
    if item is None:
        raise HTTPException(404, "Time entry not found")
    return item


def check_interval(
    session: Session,
    user_id: int,
    started_at: datetime,
    ended_at: datetime,
    exclude_id: int | None = None,
) -> None:
    if ended_at <= started_at:
        raise HTTPException(422, "ended_at must be after started_at")
    if ended_at > datetime.now(timezone.utc):
        raise HTTPException(422, "Time entries describe completed work, not future work")
    # One user cannot count the same time twice. Lock the user row to serialize
    # concurrent inserts/updates before checking overlap under READ COMMITTED.
    session.execute(select(User.id).where(User.id == user_id).with_for_update()).scalar_one()
    query = (
        select(TimeEntry.id)
        .join(Task)
        .where(
            Task.owner_id == user_id,
            TimeEntry.started_at < ended_at,
            TimeEntry.ended_at > started_at,
        )
    )
    if exclude_id is not None:
        query = query.where(TimeEntry.id != exclude_id)
    if session.scalar(query.limit(1)) is not None:
        raise HTTPException(409, "Interval overlaps another time entry")
