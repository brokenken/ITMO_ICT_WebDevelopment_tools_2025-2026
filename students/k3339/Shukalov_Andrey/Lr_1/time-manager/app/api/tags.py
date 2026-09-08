from fastapi import APIRouter, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, Limit, Offset, SessionDep
from app.models import Tag
from app.schemas.tag import TagCreate, TagPatch, TagRead
from app.services.common import apply_patch, commit, owned

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("", response_model=TagRead, status_code=201, summary="Создать: tag")
def create_tag(data: TagCreate, user: CurrentUser, session: SessionDep) -> TagRead:
    item = Tag(**data.model_dump(), owner_id=user.id)
    session.add(item)
    commit(session)
    return TagRead.model_validate(item)


@router.get("", response_model=list[TagRead], summary="Список: tags")
def list_tags(
    user: CurrentUser, session: SessionDep, offset: Offset = 0, limit: Limit = 50
) -> list[TagRead]:
    items = session.scalars(
        select(Tag).where(Tag.owner_id == user.id).order_by(Tag.id).offset(offset).limit(limit)
    )
    return [TagRead.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=TagRead, summary="Получить: tag")
def get_tag(item_id: Id, user: CurrentUser, session: SessionDep) -> TagRead:
    return TagRead.model_validate(owned(session, Tag, item_id, user.id))


@router.patch("/{item_id}", response_model=TagRead, summary="Изменить: tag")
def update_tag(item_id: Id, data: TagPatch, user: CurrentUser, session: SessionDep) -> TagRead:
    item = owned(session, Tag, item_id, user.id)
    apply_patch(item, data)
    commit(session)
    return TagRead.model_validate(item)


@router.delete("/{item_id}", status_code=204, summary="Удалить: tag")
def delete_tag(item_id: Id, user: CurrentUser, session: SessionDep) -> Response:
    session.delete(owned(session, Tag, item_id, user.id))
    commit(session)
    return Response(status_code=204)
