from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from numera.api.dependencies import bearer_scheme, get_current_user
from numera.api.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    Message,
    RefreshRequest,
    TokenPair,
    UserRead,
    UserRegister,
    UserUpdate,
)
from numera.core.config import settings
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import AuthTokenORM, UserORM
from numera.security.passwords import hash_password, verify_password
from numera.security.tokens import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter()
users_router = APIRouter()


def _store_refresh_token(db: Session, user_id: str, jti: str) -> None:
    db.add(
        AuthTokenORM(
            jti=jti,
            user_id=user_id,
            token_type="refresh",
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )
    )


def _token_pair(db: Session, user_id: str) -> TokenPair:
    access, _, expires_in = create_access_token(user_id)
    refresh, refresh_jti, _ = create_refresh_token(user_id)
    _store_refresh_token(db, user_id, refresh_jti)
    db.commit()
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=expires_in,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    existing = db.scalar(select(UserORM).where(UserORM.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    user = UserORM(
        email=email,
        password_hash=hash_password(payload.password),
        name=payload.name.strip(),
        company_id=None,
        # The effective role is assigned through a company membership. Until
        # onboarding is completed, the user has no tenant privileges.
        role="readonly",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login with email and password",
    description=(
        "Enter only the account email and password. The response contains the "
        "access token to paste into Swagger's Authorize dialog."
    ),
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()
    user = db.scalar(select(UserORM).where(UserORM.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return _token_pair(db, user.id)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = decode_token(payload.refresh_token, "refresh")
    except TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    stored = db.get(AuthTokenORM, claims["jti"])
    if stored is None or stored.revoked:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")
    if stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    user = db.get(UserORM, claims["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User is not available")

    stored.revoked = True
    return _token_pair(db, user.id)


@router.post("/logout", response_model=Message)
def logout(
    payload: LogoutRequest,
    credentials=Depends(bearer_scheme),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    access_claims = decode_token(credentials.credentials, "access")
    db.merge(
        AuthTokenORM(
            jti=access_claims["jti"],
            user_id=user.id,
            token_type="access",
            expires_at=datetime.fromtimestamp(access_claims["exp"], tz=timezone.utc).replace(tzinfo=None),
            revoked=True,
        )
    )

    if payload.refresh_token:
        try:
            refresh_claims = decode_token(payload.refresh_token, "refresh")
            if refresh_claims["sub"] == user.id:
                stored = db.get(AuthTokenORM, refresh_claims["jti"])
                if stored:
                    stored.revoked = True
        except TokenError:
            pass
    db.commit()
    return Message(detail="Logged out successfully")


@router.get("/me", response_model=UserRead)
def me(user: UserORM = Depends(get_current_user)):
    return user


@users_router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user
