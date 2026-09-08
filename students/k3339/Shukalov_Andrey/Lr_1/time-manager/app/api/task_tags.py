from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, SessionDep
from app.models import Tag, Task, TaskTag
from app.schemas.tag import TaskTagCreate, TaskTagPatch, TaskTagRead
from app.services.common import commit, owned

router = APIRouter(prefix="/tasks/{task_id}/tags", tags=["Task tags"])


def get_link(task_id: Id, tag_id: Id, user: CurrentUser, session: SessionDep) -> TaskTag:
    owned(session, Task, task_id, user.id)
    item = session.get(TaskTag, (task_id, tag_id))
    if item is None:
        raise HTTPException(404, "Association not found")
    return item


@router.post("", response_model=TaskTagRead, status_code=201, summary="Привязать тег к задаче")
def add_tag(
    task_id: Id, data: TaskTagCreate, user: CurrentUser, session: SessionDep
) -> TaskTagRead:
    owned(session, Task, task_id, user.id)
    owned(session, Tag, data.tag_id, user.id)
    item = TaskTag(task_id=task_id, **data.model_dump())
    session.add(item)
    commit(session)
    return TaskTagRead.model_validate(item)


@router.get("", response_model=list[TaskTagRead], summary="Теги задачи со значимостью")
def list_tags(task_id: Id, user: CurrentUser, session: SessionDep) -> list[TaskTagRead]:
    owned(session, Task, task_id, user.id)
    items = session.scalars(
        select(TaskTag).where(TaskTag.task_id == task_id).order_by(TaskTag.tag_id)
    )
    return [TaskTagRead.model_validate(item) for item in items]


@router.get("/{tag_id}", response_model=TaskTagRead, summary="Получить связь задачи с тегом")
def read_link(task_id: Id, tag_id: Id, user: CurrentUser, session: SessionDep) -> TaskTagRead:
    return TaskTagRead.model_validate(get_link(task_id, tag_id, user, session))


@router.patch(
    "/{tag_id}", response_model=TaskTagRead, summary="Изменить значимость тега для задачи"
)
def update_link(
    task_id: Id, tag_id: Id, data: TaskTagPatch, user: CurrentUser, session: SessionDep
) -> TaskTagRead:
    item = get_link(task_id, tag_id, user, session)
    item.relevance = data.relevance
    commit(session)
    return TaskTagRead.model_validate(item)


@router.delete("/{tag_id}", status_code=204, summary="Убрать тег с задачи")
def delete_link(task_id: Id, tag_id: Id, user: CurrentUser, session: SessionDep) -> Response:
    session.delete(get_link(task_id, tag_id, user, session))
    commit(session)
    return Response(status_code=204)
