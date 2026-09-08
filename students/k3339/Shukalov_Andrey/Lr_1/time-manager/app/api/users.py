from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.api.deps import CurrentUser, Id, Limit, Offset, SessionDep
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.user import PasswordChange, UserPatch, UserPublic, UserRead
from app.services.common import apply_patch, commit

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead, summary="Мой профиль")
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.patch("/me", response_model=UserRead, summary="Изменить имя в профиле")
def update_me(data: UserPatch, user: CurrentUser, session: SessionDep) -> UserRead:
    apply_patch(user, data)
    commit(session)
    return UserRead.model_validate(user)


@router.post("/me/password", status_code=204, summary="Сменить пароль и отозвать старые токены")
def change_password(data: PasswordChange, user: CurrentUser, session: SessionDep) -> Response:
    # Serialize concurrent password changes and refresh the hash after acquiring the lock.
    locked = session.scalar(
        select(User)
        .where(User.id == user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if locked is None or not verify_password(data.current_password, locked.password_hash):
        raise HTTPException(400, "Incorrect current password")
    if data.current_password == data.new_password:
        raise HTTPException(422, "New password must differ")
    locked.password_hash = hash_password(data.new_password)
    locked.token_version += 1
    commit(session)
    return Response(status_code=204)


@router.delete("/me", status_code=204, summary="Удалить свой аккаунт и его данные")
def delete_me(user: CurrentUser, session: SessionDep) -> Response:
    session.delete(user)
    commit(session)
    return Response(status_code=204)


@router.get("", response_model=list[UserPublic], summary="Список пользователей (публичные поля)")
def list_users(
    user: CurrentUser, session: SessionDep, offset: Offset = 0, limit: Limit = 50
) -> list[UserPublic]:
    return [
        UserPublic.model_validate(item)
        for item in session.scalars(select(User).order_by(User.id).offset(offset).limit(limit))
    ]


@router.get("/{user_id}", response_model=UserPublic, summary="Публичный профиль пользователя")
def get_user(user_id: Id, user: CurrentUser, session: SessionDep) -> UserPublic:
    item = session.get(User, user_id)
    if item is None:
        raise HTTPException(404, "User not found")
    return UserPublic.model_validate(item)
