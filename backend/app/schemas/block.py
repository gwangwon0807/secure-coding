from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import PaginationSchema


class BlockCreateRequest(BaseModel):
    blocked_user_id: int


class BlockCreateResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_user_id: int
    created_at: datetime


class BlockListEntry(BaseModel):
    id: int
    blocked_user: dict
    created_at: datetime


class BlockListResponse(BaseModel):
    blocks: list[BlockListEntry]
    pagination: PaginationSchema


class BlockDeleteResponse(BaseModel):
    blocked_user_id: int
    unblocked_at: datetime
