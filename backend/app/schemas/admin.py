from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AdminActionType, ItemStatus, ReportReason, ReportStatus, ReportTargetType, TransactionStatus, UserRole, UserStatus
from app.schemas.common import PaginationSchema


class AdminUserStatusUpdateRequest(BaseModel):
    status: UserStatus
    reason: str = Field(min_length=1, max_length=500)


class AdminItemStatusUpdateRequest(BaseModel):
    status: ItemStatus
    reason: str = Field(min_length=1, max_length=500)


class AdminModerationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class AdminUserListEntry(BaseModel):
    id: int
    email: str
    nickname: str
    role: UserRole
    status: UserStatus
    trust_score: int
    trade_count: int
    report_count: int
    needs_review: bool = False
    created_at: datetime


class AdminUserListResponse(BaseModel):
    users: list[AdminUserListEntry]
    pagination: PaginationSchema


class AdminUserStatusUpdateResponse(BaseModel):
    id: int
    previous_status: UserStatus
    status: UserStatus
    reason: str
    updated_at: datetime


class AdminItemListEntry(BaseModel):
    id: int
    title: str
    price: int
    status: ItemStatus
    seller: dict
    report_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AdminItemListResponse(BaseModel):
    items: list[AdminItemListEntry]
    pagination: PaginationSchema


class AdminItemStatusUpdateResponse(BaseModel):
    id: int
    previous_status: ItemStatus
    status: ItemStatus
    reason: str
    updated_at: datetime


class AdminReportListEntry(BaseModel):
    id: int
    reporter: dict
    target_type: ReportTargetType
    target_id: int
    target_summary: str | None
    reason: ReportReason
    status: ReportStatus
    created_at: datetime
    resolved_at: datetime | None


class AdminReportListResponse(BaseModel):
    reports: list[AdminReportListEntry]
    pagination: PaginationSchema


class AdminReportDetailResponse(BaseModel):
    id: int
    reporter: dict
    target_type: ReportTargetType
    target_id: int
    target_detail: dict | None
    reason: ReportReason
    detail: str | None
    status: ReportStatus
    admin_id: int | None
    admin_memo: str | None
    action_type: AdminActionType
    created_at: datetime
    resolved_at: datetime | None


class AdminReportUpdateResponse(BaseModel):
    id: int
    status: ReportStatus
    action_type: AdminActionType
    admin_memo: str | None
    result_message: str | None
    resolved_at: datetime | None


class AdminTransactionListEntry(BaseModel):
    id: int
    item: dict
    buyer: dict
    seller: dict
    status: TransactionStatus
    price: int
    created_at: datetime
    completed_at: datetime | None


class AdminTransactionListResponse(BaseModel):
    transactions: list[AdminTransactionListEntry]
    pagination: PaginationSchema


class AdminCommunityPostEntry(BaseModel):
    id: int
    title: str
    author: dict
    comment_count: int
    report_count: int
    created_at: datetime
    deleted_at: datetime | None


class AdminCommunityPostListResponse(BaseModel):
    posts: list[AdminCommunityPostEntry]
    pagination: PaginationSchema


class AdminCommunityCommentEntry(BaseModel):
    id: int
    post_id: int
    post_title: str | None
    author: dict
    content: str
    report_count: int
    created_at: datetime
    deleted_at: datetime | None


class AdminCommunityCommentListResponse(BaseModel):
    comments: list[AdminCommunityCommentEntry]
    pagination: PaginationSchema


class AdminChatRoomEntry(BaseModel):
    id: int
    item: dict
    buyer: dict
    seller: dict
    message_count: int
    last_message_at: datetime | None
    created_at: datetime


class AdminChatRoomListResponse(BaseModel):
    chat_rooms: list[AdminChatRoomEntry]
    pagination: PaginationSchema


class AdminChatMessageEntry(BaseModel):
    id: int
    sender: dict
    content: str
    created_at: datetime


class AdminChatMessageListResponse(BaseModel):
    messages: list[AdminChatMessageEntry]
    pagination: PaginationSchema


class AuditLogEntry(BaseModel):
    id: int
    admin_id: int
    action: str
    target_type: str
    target_id: int
    reason: str
    created_at: datetime


class AuditLogListResponse(BaseModel):
    audit_logs: list[AuditLogEntry]
    pagination: PaginationSchema
