from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import SessionDep
from app.core.security import DUMMY_HASH, create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.user import Register, Token, UserRead
from app.services.common import commit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=201, summary="Регистрация")
def register(data: Register, session: SessionDep) -> UserRead:
    user = User(**data.model_dump(exclude={"password"}), password_hash=hash_password(data.password))
    session.add(user)
    commit(session)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token, summary="Вход и получение JWT")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = session.scalar(select(User).where(User.username == form.username.strip().lower()))
    valid = verify_password(form.password, user.password_hash if user else DUMMY_HASH)
    if user is None or not valid:
        raise HTTPException(
            401, "Incorrect username or password", headers={"WWW-Authenticate": "Bearer"}
        )
    return Token(access_token=create_access_token(user))
