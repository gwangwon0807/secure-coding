from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.item import ItemImageSummary
from app.schemas.common import PaginationSchema


class CommunityPostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)
    image_ids: list[int] = Field(default_factory=list, max_length=10)


class CommunityPostUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    image_ids: list[int] | None = Field(default=None, max_length=10)


class CommunityCommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommunityCommentUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommunityAuthorSummary(BaseModel):
    id: int
    nickname: str


class CommunityCommentEntry(BaseModel):
    id: int
    author: CommunityAuthorSummary
    content: str
    created_at: datetime
    updated_at: datetime


class CommunityPostListEntry(BaseModel):
    id: int
    title: str
    author: CommunityAuthorSummary
    comment_count: int
    thumbnail_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CommunityPostListResponse(BaseModel):
    posts: list[CommunityPostListEntry]
    pagination: PaginationSchema


class CommunityPostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    author: CommunityAuthorSummary
    images: list[ItemImageSummary]
    comments: list[CommunityCommentEntry]
    created_at: datetime
    updated_at: datetime


class CommunityPostStateResponse(BaseModel):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class CommunityCommentStateResponse(BaseModel):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
