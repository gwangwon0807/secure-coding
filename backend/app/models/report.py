from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AdminActionType, ReportReason, ReportStatus, ReportTargetType


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    target_type: Mapped[ReportTargetType] = mapped_column(Enum(ReportTargetType))
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    reason: Mapped[ReportReason] = mapped_column(Enum(ReportReason))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.RECEIVED)
    action_type: Mapped[AdminActionType] = mapped_column(Enum(AdminActionType), default=AdminActionType.NONE)
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    admin_memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
