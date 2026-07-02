from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AdminActionType, ReportReason, ReportStatus, ReportTargetType
from app.schemas.common import PaginationSchema


class ReportCreateRequest(BaseModel):
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason
    detail: str | None = Field(default=None, max_length=1000)


class ReportCreateResponse(BaseModel):
    id: int
    reporter_id: int
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason
    detail: str | None
    status: ReportStatus
    created_at: datetime


class ReportListEntry(BaseModel):
    id: int
    target_type: ReportTargetType
    target_id: int
    target_summary: str | None
    reason: ReportReason
    status: ReportStatus
    created_at: datetime
    resolved_at: datetime | None


class ReportListResponse(BaseModel):
    reports: list[ReportListEntry]
    pagination: PaginationSchema


class ReportDetailResponse(BaseModel):
    id: int
    reporter_id: int
    target_type: ReportTargetType
    target_id: int
    target_summary: str | None
    reason: ReportReason
    detail: str | None
    status: ReportStatus
    result_message: str | None
    created_at: datetime
    resolved_at: datetime | None


class AdminReportUpdateRequest(BaseModel):
    status: ReportStatus
    action_type: AdminActionType
    admin_memo: str | None = Field(default=None, max_length=1000)
    result_message: str | None = Field(default=None, max_length=500)
