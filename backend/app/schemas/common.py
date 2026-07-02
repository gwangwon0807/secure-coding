from datetime import datetime

from pydantic import BaseModel


class PaginationSchema(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class MessageSchema(BaseModel):
    message: str


class TimestampedResponse(BaseModel):
    id: int
    created_at: datetime
