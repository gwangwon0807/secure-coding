from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ItemStatus
from app.schemas.common import PaginationSchema


class ItemSellerSummary(BaseModel):
    id: int
    nickname: str
    trust_score: int
    profile_image_url: str | None = None


class ItemImageSummary(BaseModel):
    id: int
    image_url: str
    sort_order: int


class ItemListEntry(BaseModel):
    id: int
    title: str
    price: int
    location: str
    status: ItemStatus
    thumbnail_url: str | None
    seller: ItemSellerSummary
    created_at: datetime


class ItemListResponse(BaseModel):
    items: list[ItemListEntry]
    pagination: PaginationSchema


class ItemCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=1, max_length=3000)
    price: int = Field(ge=0)
    category_id: int
    location: str = Field(min_length=1, max_length=100)
    image_ids: list[int] = Field(min_length=1, max_length=10)


class ItemUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=3000)
    price: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    location: str | None = Field(default=None, min_length=1, max_length=100)
    image_ids: list[int] | None = Field(default=None, min_length=1, max_length=10)


class ItemStatusUpdateRequest(BaseModel):
    status: ItemStatus


class ItemCreateResponse(BaseModel):
    id: int
    seller_id: int
    title: str
    price: int
    status: ItemStatus
    created_at: datetime


class ItemUpdateResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    category_id: int
    location: str
    updated_at: datetime


class ItemDeleteResponse(BaseModel):
    id: int
    deleted_at: datetime


class ItemStatusUpdateResponse(BaseModel):
    id: int
    status: ItemStatus
    updated_at: datetime


class ItemDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    category: dict
    location: str
    status: ItemStatus
    images: list[ItemImageSummary]
    seller: ItemSellerSummary
    view_count: int
    created_at: datetime
    updated_at: datetime
