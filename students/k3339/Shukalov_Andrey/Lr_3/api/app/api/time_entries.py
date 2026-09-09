from fastapi import APIRouter, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, Limit, Offset, SessionDep
from app.models import Task, TimeEntry
from app.schemas.time_entry import TimeEntryCreate, TimeEntryPatch, TimeEntryRead
from app.services.common import apply_patch, commit, owned
from app.services.time_entries import check_interval, get_entry

router = APIRouter(prefix="/time-entries", tags=["Time entries"])


@router.post(
    "", response_model=TimeEntryRead, status_code=201, summary="Записать затраченное время"
)
def create_entry(data: TimeEntryCreate, user: CurrentUser, session: SessionDep) -> TimeEntryRead:
    owned(session, Task, data.task_id, user.id)
    check_interval(session, user.id, data.started_at, data.ended_at)
    item = TimeEntry(**data.model_dump())
    session.add(item)
    commit(session)
    return TimeEntryRead.model_validate(item)


@router.get("", response_model=list[TimeEntryRead], summary="Список записей времени")
def list_entries(
    user: CurrentUser,
    session: SessionDep,
    offset: Offset = 0,
    limit: Limit = 50,
    task_id: int | None = None,
) -> list[TimeEntryRead]:
    query = select(TimeEntry).join(Task).where(Task.owner_id == user.id)
    if task_id is not None:
        query = query.where(TimeEntry.task_id == task_id)
    items = session.scalars(
        query.order_by(TimeEntry.started_at, TimeEntry.id).offset(offset).limit(limit)
    )
    return [TimeEntryRead.model_validate(item) for item in items]


@router.get("/{entry_id}", response_model=TimeEntryRead, summary="Получить запись времени")
def read_entry(entry_id: Id, user: CurrentUser, session: SessionDep) -> TimeEntryRead:
    return TimeEntryRead.model_validate(get_entry(session, entry_id, user.id))


@router.patch("/{entry_id}", response_model=TimeEntryRead, summary="Изменить запись времени")
def update_entry(
    entry_id: Id, data: TimeEntryPatch, user: CurrentUser, session: SessionDep
) -> TimeEntryRead:
    # Acquire the per-user lock before reading the values being modified.
    from app.models import User

    session.execute(select(User.id).where(User.id == user.id).with_for_update()).scalar_one()
    item = get_entry(session, entry_id, user.id)
    check_interval(
        session,
        user.id,
        data.started_at or item.started_at,
        data.ended_at or item.ended_at,
        exclude_id=item.id,
    )
    apply_patch(item, data)
    commit(session)
    return TimeEntryRead.model_validate(item)


@router.delete("/{entry_id}", status_code=204, summary="Удалить запись времени")
def delete_entry(entry_id: Id, user: CurrentUser, session: SessionDep) -> Response:
    session.delete(get_entry(session, entry_id, user.id))
    commit(session)
    return Response(status_code=204)
