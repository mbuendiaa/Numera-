from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import AuthTokenORM, UserORM
from numera.security.tokens import TokenError, decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserORM:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, "access")
    except TokenError as exc:
        raise credentials_error from exc

    revoked = db.get(AuthTokenORM, payload["jti"])
    if revoked is not None and revoked.revoked:
        raise credentials_error

    user = db.get(UserORM, payload["sub"])
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_roles(*roles: str) -> Callable:
    def dependency(user: UserORM = Depends(get_current_user)) -> UserORM:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency


require_admin = require_roles("owner", "admin")
require_owner = require_roles("owner")
