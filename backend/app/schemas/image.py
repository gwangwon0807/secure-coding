from datetime import datetime

from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: int
    image_url: str
    sort_order: int
    created_at: datetime


class ImageListResponse(BaseModel):
    images: list[ImageResponse]


class DeleteImageResponse(BaseModel):
    id: int
    deleted_at: datetime
