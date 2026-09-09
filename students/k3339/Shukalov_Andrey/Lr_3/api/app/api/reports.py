from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Task, TimeEntry
from app.schemas.task import TaskTimeSummary, TimeSummary

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/time", response_model=TimeSummary, summary="Суммарное время по задачам")
def time_summary(user: CurrentUser, session: SessionDep) -> TimeSummary:
    seconds = func.coalesce(
        func.sum(func.extract("epoch", TimeEntry.ended_at - TimeEntry.started_at)), 0
    )
    rows = session.execute(
        select(Task.id, Task.title, seconds.label("seconds"))
        .outerjoin(TimeEntry)
        .where(Task.owner_id == user.id)
        .group_by(Task.id, Task.title)
        .order_by(Task.id)
    )
    tasks = [
        TaskTimeSummary(task_id=row.id, title=row.title, total_seconds=float(row.seconds))
        for row in rows
    ]
    return TimeSummary(total_seconds=sum(item.total_seconds for item in tasks), tasks=tasks)
