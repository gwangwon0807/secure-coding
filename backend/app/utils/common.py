from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


settings = get_settings()


def ensure_upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_file_url(filename: str) -> str:
    return f"{settings.public_upload_prefix}/{filename}"


def save_upload_file(file: UploadFile) -> tuple[str, str]:
    upload_dir = ensure_upload_dir()
    suffix = Path(file.filename or "").suffix.lower()
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{suffix}"
    destination = upload_dir / filename
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())
    return filename, build_file_url(filename)
