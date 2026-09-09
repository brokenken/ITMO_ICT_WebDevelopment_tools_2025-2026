from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Path, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_session
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_session)]
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")
Id = Annotated[int, Path(gt=0, le=2147483647)]
Offset = Annotated[int, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=100)]


def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2)]) -> User:
    error = HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(
            token,
            get_settings().jwt_secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "iat", "ver"]},
        )
        user_id = int(payload["sub"])
        if user_id <= 0 or user_id > 2147483647 or type(payload["ver"]) is not int:
            raise error
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise error from None
    user = session.get(User, user_id)
    if user is None or user.token_version != payload["ver"]:
        raise error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
