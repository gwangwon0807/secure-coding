from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, require_active_user
from app.core.security import create_token, decode_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthMeResponse, LoginRequest, LoginResponse, SignupRequest, SignupResponse


router = APIRouter()
settings = get_settings()


def _set_auth_cookies(response: Response, user_id: int) -> None:
    access = create_token(str(user_id), "access", settings.access_token_expire_minutes)
    refresh = create_token(str(user_id), "refresh", settings.refresh_token_expire_minutes)
    for name, value, minutes in (
        (settings.access_cookie_name, access, settings.access_token_expire_minutes),
        (settings.refresh_cookie_name, refresh, settings.refresh_token_expire_minutes),
    ):
        response.set_cookie(
            key=name,
            value=value,
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            max_age=minutes * 60,
            path="/",
        )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/")


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
    _set_auth_cookies(response, user.id)
    return {"user": user}


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    _clear_auth_cookies(response)
    return {"message": "로그아웃되었습니다."}


@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="REFRESH_TOKEN_MISSING")
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
    _set_auth_cookies(response, int(payload["sub"]))
    return {"message": "토큰이 재발급되었습니다."}


@router.get("/me", response_model=AuthMeResponse)
def me(current_user: User = Depends(require_active_user)):
    return current_user
