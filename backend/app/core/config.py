from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "중고마켓 MVP API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True

    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@db:5432/secure_coding")
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    backend_cors_origins: str = "http://localhost:3000"
    upload_dir: str = str(BASE_DIR / "uploads")
    public_upload_prefix: str = "/uploads"

    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    csrf_cookie_name: str = "csrf_token"

    admin_email: str = "admin@example.com"
    admin_password: str = "admin1234"
    admin_nickname: str = "관리자"


@lru_cache
def get_settings() -> Settings:
    return Settings()
