from fastapi import APIRouter, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, Limit, Offset, SessionDep
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectPatch, ProjectRead
from app.schemas.task import ProjectDetail
from app.services.common import apply_patch, commit, owned

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=201, summary="Создать: project")
def create_project(data: ProjectCreate, user: CurrentUser, session: SessionDep) -> ProjectRead:
    item = Project(**data.model_dump(), owner_id=user.id)
    session.add(item)
    commit(session)
    return ProjectRead.model_validate(item)


@router.get("", response_model=list[ProjectRead], summary="Список: projects")
def list_projects(
    user: CurrentUser, session: SessionDep, offset: Offset = 0, limit: Limit = 50
) -> list[ProjectRead]:
    items = session.scalars(
        select(Project)
        .where(Project.owner_id == user.id)
        .order_by(Project.id)
        .offset(offset)
        .limit(limit)
    )
    return [ProjectRead.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ProjectDetail, summary="Получить: project")
def get_project(item_id: Id, user: CurrentUser, session: SessionDep) -> ProjectDetail:
    return ProjectDetail.model_validate(owned(session, Project, item_id, user.id))


@router.patch("/{item_id}", response_model=ProjectRead, summary="Изменить: project")
def update_project(
    item_id: Id, data: ProjectPatch, user: CurrentUser, session: SessionDep
) -> ProjectRead:
    item = owned(session, Project, item_id, user.id)
    apply_patch(item, data)
    commit(session)
    return ProjectRead.model_validate(item)


@router.delete("/{item_id}", status_code=204, summary="Удалить: project")
def delete_project(item_id: Id, user: CurrentUser, session: SessionDep) -> Response:
    session.delete(owned(session, Project, item_id, user.id))
    commit(session)
    return Response(status_code=204)
