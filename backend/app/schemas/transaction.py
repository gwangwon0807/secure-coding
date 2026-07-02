from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ItemStatus, TransactionStatus
from app.schemas.common import PaginationSchema


class TransactionCreateRequest(BaseModel):
    item_id: int
    price: int = Field(ge=0)


class TransactionReasonRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class TransactionItemSummary(BaseModel):
    id: int
    title: str
    thumbnail_url: str | None
    status: ItemStatus
    price: int | None = None


class TransactionUserSummary(BaseModel):
    id: int
    nickname: str


class TransactionResponse(BaseModel):
    id: int
    item_id: int
    buyer_id: int
    seller_id: int
    status: TransactionStatus
    price: int
    created_at: datetime


class TransactionListEntry(BaseModel):
    id: int
    item: TransactionItemSummary
    buyer: TransactionUserSummary
    seller: TransactionUserSummary
    status: TransactionStatus
    buyer_completed: bool = False
    seller_completed: bool = False
    price: int
    created_at: datetime
    completed_at: datetime | None


class TransactionListResponse(BaseModel):
    transactions: list[TransactionListEntry]
    pagination: PaginationSchema


class TransactionDetailResponse(BaseModel):
    id: int
    item: TransactionItemSummary
    buyer: TransactionUserSummary
    seller: TransactionUserSummary
    status: TransactionStatus
    buyer_completed: bool = False
    seller_completed: bool = False
    price: int
    created_at: datetime
    accepted_at: datetime | None
    rejected_at: datetime | None
    canceled_at: datetime | None
    completed_at: datetime | None


class TransactionStateResponse(BaseModel):
    id: int
    status: TransactionStatus
    item_id: int
    item_status: ItemStatus | None = None
    buyer_completed: bool = False
    seller_completed: bool = False
    accepted_at: datetime | None = None
    rejected_at: datetime | None = None
    canceled_at: datetime | None = None
    completed_at: datetime | None = None
    reason: str | None = None
