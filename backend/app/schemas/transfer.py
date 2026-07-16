from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import DepositRequestStatus, TransferStatus, WalletTransactionType
from app.schemas.common import PaginationSchema


class TransferPartySummary(BaseModel):
    id: int
    nickname: str


class WalletSummaryResponse(BaseModel):
    user: TransferPartySummary
    balance: int


class WalletBalanceChangeRequest(BaseModel):
    amount: int = Field(ge=1)


class DepositRequestCreateRequest(BaseModel):
    amount: int = Field(ge=1)


class TransferCreateRequest(BaseModel):
    recipient_id: int
    amount: int = Field(ge=1)
    note: str | None = Field(default=None, max_length=200)
    transaction_id: int | None = None
    chat_room_id: int | None = None


class TransferHistoryEntry(BaseModel):
    id: int
    sender: TransferPartySummary
    recipient: TransferPartySummary
    amount: int
    note: str | None
    status: TransferStatus
    transaction_id: int | None
    chat_room_id: int | None
    created_at: datetime


class TransferListResponse(BaseModel):
    transfers: list[TransferHistoryEntry]
    pagination: PaginationSchema


class WalletLedgerEntry(BaseModel):
    id: int
    transfer_id: int | None
    transaction_type: WalletTransactionType
    amount: int
    balance_after: int
    description: str
    counterparty_user_id: int | None
    created_at: datetime


class WalletLedgerResponse(BaseModel):
    ledger: list[WalletLedgerEntry]
    pagination: PaginationSchema


class TransferDetailResponse(BaseModel):
    id: int
    sender: TransferPartySummary
    recipient: TransferPartySummary
    amount: int
    note: str | None
    status: TransferStatus
    transaction_id: int | None
    chat_room_id: int | None
    created_at: datetime
    canceled_at: datetime | None


class AdminWalletAdjustmentRequest(BaseModel):
    amount: int
    reason: str = Field(min_length=1, max_length=300)


class AdminWalletAdjustmentResponse(BaseModel):
    user_id: int
    balance: int
    amount: int
    reason: str
    updated_at: datetime


class WalletBalanceChangeResponse(BaseModel):
    balance: int
    amount: int
    transaction_type: WalletTransactionType
    updated_at: datetime


class DepositRequestEntry(BaseModel):
    id: int
    user: TransferPartySummary
    amount: int
    status: DepositRequestStatus
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by_admin: TransferPartySummary | None = None


class DepositRequestListResponse(BaseModel):
    requests: list[DepositRequestEntry]
    pagination: PaginationSchema


class AdminDepositRequestDecisionRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class AdminDepositRequestDecisionResponse(BaseModel):
    id: int
    status: DepositRequestStatus
    amount: int
    balance: int
    reviewed_at: datetime
    reviewed_by_admin: TransferPartySummary
    reason: str | None = None


class AdminWalletEntry(BaseModel):
    user: TransferPartySummary
    balance: int
    updated_at: datetime


class AdminWalletListResponse(BaseModel):
    wallets: list[AdminWalletEntry]
    pagination: PaginationSchema
