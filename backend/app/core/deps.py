from datetime import datetime
from hmac import compare_digest

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_token, hash_token
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.enums import UserRole, UserStatus
from app.models.user import User


settings = get_settings()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    access_cookie: str | None = Cookie(default=None, alias=settings.access_cookie_name),
    csrf_cookie: str | None = Cookie(default=None, alias=settings.csrf_cookie_name),
) -> User:
    if not access_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ACCESS_TOKEN_MISSING")
    try:
        payload = decode_token(access_cookie)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_ACCESS_TOKEN") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_ACCESS_TOKEN")
    session_id = payload.get("sid")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_ACCESS_TOKEN")
    auth_session = db.scalar(
        select(AuthSession).where(
            AuthSession.id == int(session_id),
            AuthSession.user_id == int(payload["sub"]),
        )
    )
    if not auth_session or auth_session.revoked_at is not None or auth_session.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="SESSION_EXPIRED")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        csrf_header = request.headers.get("X-CSRF-Token")
        if not csrf_cookie or not csrf_header or not compare_digest(csrf_cookie, csrf_header):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF_TOKEN_INVALID")
        if not compare_digest(hash_token(csrf_cookie), auth_session.csrf_token_hash):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF_TOKEN_INVALID")
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="USER_NOT_ACTIVE")
    return current_user


def require_admin(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMIN_REQUIRED")
    return current_user
