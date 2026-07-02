from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ImageStatus


class ImageResponse(BaseModel):
    id: int
    image_url: str
    sort_order: int
    status: ImageStatus
    created_at: datetime


class ImageListResponse(BaseModel):
    images: list[ImageResponse]


class DeleteImageResponse(BaseModel):
    id: int
    deleted_at: datetime
