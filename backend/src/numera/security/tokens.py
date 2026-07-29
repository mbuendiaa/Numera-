from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from numera.core.config import settings


class TokenError(ValueError):
    pass


def _create_token(subject: str, token_type: str, lifetime: timedelta) -> tuple[str, str, int]:
    now = datetime.now(timezone.utc)
    expires = now + lifetime
    jti = uuid4().hex
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, int(lifetime.total_seconds())


def create_access_token(user_id: str) -> tuple[str, str, int]:
    return _create_token(
        user_id,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> tuple[str, str, int]:
    return _create_token(
        user_id,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise TokenError("Invalid or expired token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")
    if not payload.get("sub") or not payload.get("jti"):
        raise TokenError("Token is missing required claims")
    return payload
