from datetime import datetime, timedelta
from hmac import compare_digest

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import require_active_user
from app.core.security import create_token, decode_token, generate_secure_token, get_password_hash, hash_token, verify_password
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.enums import UserStatus
from app.models.transfer import Wallet
from app.models.user import User
from app.schemas.auth import AuthMeResponse, LoginRequest, LoginResponse, SignupRequest, SignupResponse


router = APIRouter()
settings = get_settings()


def _set_auth_cookies(
    response: Response,
    user_id: int,
    session_id: int,
    refresh_token: str,
    csrf_token: str,
) -> None:
    access_token = create_token(
        str(user_id),
        "access",
        settings.access_token_expire_minutes,
        {"sid": session_id},
    )
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_minutes * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")


def _validate_csrf(request: Request, csrf_token: str | None, session: AuthSession) -> None:
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_token or not csrf_header or not compare_digest(csrf_token, csrf_header):
        raise HTTPException(status_code=403, detail="CSRF_TOKEN_INVALID")
    if not compare_digest(hash_token(csrf_token), session.csrf_token_hash):
        raise HTTPException(status_code=403, detail="CSRF_TOKEN_INVALID")


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="EMAIL_ALREADY_EXISTS")
    if db.scalar(select(User).where(User.nickname == payload.nickname)):
        raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")
    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        nickname=payload.nickname,
    )
    db.add(user)
    db.flush()
    db.add(Wallet(user_id=user.id, balance=0))
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
    if user.status.name == "DELETED":
        raise HTTPException(status_code=403, detail="USER_DELETED")
    if user.status.name == "SUSPENDED":
        raise HTTPException(status_code=403, detail="USER_SUSPENDED")
    refresh_token = generate_secure_token()
    csrf_token = generate_secure_token()
    auth_session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh_token),
        csrf_token_hash=hash_token(csrf_token),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    db.add(auth_session)
    db.flush()
    _set_auth_cookies(response, user.id, auth_session.id, refresh_token, csrf_token)
    db.commit()
    return {"user": user}


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    access_token: str | None = Cookie(default=None, alias=settings.access_cookie_name),
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
    csrf_token: str | None = Cookie(default=None, alias=settings.csrf_cookie_name),
    db: Session = Depends(get_db),
):
    auth_session = None
    if refresh_token:
        auth_session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(refresh_token)))
    if not auth_session and access_token:
        try:
            payload = decode_token(access_token)
            session_id = payload.get("sid")
            auth_session = db.get(AuthSession, int(session_id)) if session_id else None
        except Exception:  # noqa: BLE001
            auth_session = None
    if auth_session and auth_session.revoked_at is None:
        _validate_csrf(request, csrf_token, auth_session)
        auth_session.revoked_at = datetime.utcnow()
        db.add(auth_session)
        db.commit()
    _clear_auth_cookies(response)
    return {"message": "로그아웃되었습니다."}


@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
    csrf_token: str | None = Cookie(default=None, alias=settings.csrf_cookie_name),
    db: Session = Depends(get_db),
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="REFRESH_TOKEN_MISSING")
    auth_session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(refresh_token)))
    if not auth_session or auth_session.revoked_at is not None or auth_session.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
    _validate_csrf(request, csrf_token, auth_session)
    user = db.get(User, auth_session.user_id)
    if not user or user.status != UserStatus.ACTIVE:
        auth_session.revoked_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=403, detail="USER_NOT_ACTIVE")

    next_refresh_token = generate_secure_token()
    next_csrf_token = generate_secure_token()
    auth_session.refresh_token_hash = hash_token(next_refresh_token)
    auth_session.csrf_token_hash = hash_token(next_csrf_token)
    auth_session.last_used_at = datetime.utcnow()
    auth_session.expires_at = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)
    db.add(auth_session)
    _set_auth_cookies(response, user.id, auth_session.id, next_refresh_token, next_csrf_token)
    db.commit()
    return {"message": "토큰이 재발급되었습니다."}


@router.get("/me", response_model=AuthMeResponse)
def me(current_user: User = Depends(require_active_user)):
    return current_user
