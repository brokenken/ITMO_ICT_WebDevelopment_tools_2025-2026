from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, Limit, Offset, SessionDep
from app.models import Priority, Project, Task, TaskStatus, TaskTag
from app.schemas.task import TaskCreate, TaskDetail, TaskPatch, TaskRead
from app.services.common import apply_patch, commit, owned
from app.services.tasks import task_detail

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=201, summary="Создать задачу")
def create_task(data: TaskCreate, user: CurrentUser, session: SessionDep) -> TaskRead:
    if data.project_id is not None:
        owned(session, Project, data.project_id, user.id)
    item = Task(**data.model_dump(), owner_id=user.id)
    session.add(item)
    commit(session)
    return TaskRead.model_validate(item)


@router.get("", response_model=list[TaskRead], summary="Список задач с фильтрами")
def list_tasks(
    user: CurrentUser,
    session: SessionDep,
    offset: Offset = 0,
    limit: Limit = 50,
    status: TaskStatus | None = None,
    priority: Priority | None = None,
    project_id: int | None = None,
    tag_id: int | None = None,
    overdue: bool = False,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> list[TaskRead]:
    query = select(Task).where(Task.owner_id == user.id)
    if status is not None:
        query = query.where(Task.status == status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if tag_id is not None:
        query = query.where(Task.tag_links.any(TaskTag.tag_id == tag_id))
    if overdue:
        query = query.where(
            Task.deadline < datetime.now(timezone.utc), Task.status != TaskStatus.done
        )
    if q:
        query = query.where(Task.title.icontains(q, autoescape=True))
    return [
        TaskRead.model_validate(item)
        for item in session.scalars(query.order_by(Task.id).offset(offset).limit(limit))
    ]


@router.get("/{task_id}", response_model=TaskDetail, summary="Задача с проектом, тегами и временем")
def get_task(task_id: Id, user: CurrentUser, session: SessionDep) -> TaskDetail:
    return task_detail(owned(session, Task, task_id, user.id))


@router.patch("/{task_id}", response_model=TaskRead, summary="Изменить задачу")
def update_task(task_id: Id, data: TaskPatch, user: CurrentUser, session: SessionDep) -> TaskRead:
    item = owned(session, Task, task_id, user.id)
    if data.project_id is not None:
        owned(session, Project, data.project_id, user.id)
    apply_patch(item, data)
    commit(session)
    return TaskRead.model_validate(item)


@router.delete("/{task_id}", status_code=204, summary="Удалить задачу и её записи времени")
def delete_task(task_id: Id, user: CurrentUser, session: SessionDep) -> Response:
    session.delete(owned(session, Task, task_id, user.id))
    commit(session)
    return Response(status_code=204)
