from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.helpers import build_report_target_summary, ensure_page_size, require_chat_room, require_report
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.chat import Message
from app.models.community import CommunityComment, CommunityPost
from app.models.enums import ItemStatus, ReportStatus, ReportTargetType
from app.models.item import Item
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreateRequest, ReportCreateResponse, ReportDetailResponse, ReportListEntry, ReportListResponse
from app.utils.pagination import build_pagination


router = APIRouter()
ITEM_REPORT_THRESHOLD = 3
USER_REPORT_REVIEW_THRESHOLD = 5


def _active_report_count(db: Session, target_type: ReportTargetType, target_id: int) -> int:
    return db.scalar(
        select(func.count(Report.id)).where(
            Report.target_type == target_type,
            Report.target_id == target_id,
            Report.status != ReportStatus.REJECTED,
        )
    ) or 0


def _ensure_report_target(db: Session, payload: ReportCreateRequest, reporter_id: int) -> None:
    if payload.target_type == ReportTargetType.ITEM:
        item = db.get(Item, payload.target_id)
        if not item or item.deleted_at is not None:
            raise HTTPException(status_code=404, detail="TARGET_NOT_FOUND")
        if item.seller_id == reporter_id:
            raise HTTPException(status_code=400, detail="CANNOT_REPORT_OWN_ITEM")
    elif payload.target_type == ReportTargetType.USER:
        user = db.get(User, payload.target_id)
        if not user:
            raise HTTPException(status_code=404, detail="TARGET_NOT_FOUND")
        if user.id == reporter_id:
            raise HTTPException(status_code=400, detail="CANNOT_REPORT_SELF")
    elif payload.target_type == ReportTargetType.COMMUNITY_POST:
        post = db.get(CommunityPost, payload.target_id)
        if not post or post.deleted_at is not None:
            raise HTTPException(status_code=404, detail="TARGET_NOT_FOUND")
        if post.author_id == reporter_id:
            raise HTTPException(status_code=400, detail="CANNOT_REPORT_OWN_POST")
    elif payload.target_type == ReportTargetType.COMMUNITY_COMMENT:
        comment = db.get(CommunityComment, payload.target_id)
        if not comment or comment.deleted_at is not None:
            raise HTTPException(status_code=404, detail="TARGET_NOT_FOUND")
        if comment.author_id == reporter_id:
            raise HTTPException(status_code=400, detail="CANNOT_REPORT_OWN_COMMENT")
    elif payload.target_type == ReportTargetType.CHAT_ROOM:
        room = require_chat_room(db, payload.target_id)
        if reporter_id not in {room.buyer_id, room.seller_id}:
            raise HTTPException(status_code=403, detail="FORBIDDEN_CHAT_REPORT")
    elif payload.target_type == ReportTargetType.MESSAGE:
        message = db.get(Message, payload.target_id)
        if not message:
            raise HTTPException(status_code=404, detail="TARGET_NOT_FOUND")
        room = require_chat_room(db, message.chat_room_id)
        if reporter_id not in {room.buyer_id, room.seller_id}:
            raise HTTPException(status_code=403, detail="FORBIDDEN_CHAT_REPORT")


@router.post("", response_model=ReportCreateResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    _ensure_report_target(db, payload, current_user.id)
    existing = db.scalar(
        select(Report).where(
            Report.reporter_id == current_user.id,
            Report.target_type == payload.target_type,
            Report.target_id == payload.target_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="DUPLICATE_REPORT")
    report = Report(
        reporter_id=current_user.id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        detail=payload.detail,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    if report.target_type == ReportTargetType.ITEM:
        item = db.get(Item, report.target_id)
        if item and item.deleted_at is None:
            active_count = _active_report_count(db, ReportTargetType.ITEM, report.target_id)
            if active_count >= ITEM_REPORT_THRESHOLD and item.status != ItemStatus.HIDDEN:
                item.status = ItemStatus.HIDDEN
                db.add(item)
                db.commit()
    return report


@router.get("/me", response_model=ReportListResponse)
def list_my_reports(
    status_filter: ReportStatus | None = None,
    target_type: ReportTargetType | None = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Report).where(Report.reporter_id == current_user.id)
    if status_filter:
        stmt = stmt.where(Report.status == status_filter)
    if target_type:
        stmt = stmt.where(Report.target_type == target_type)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    reports = db.scalars(stmt.order_by(Report.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = [
        ReportListEntry(
            id=report.id,
            target_type=report.target_type,
            target_id=report.target_id,
            target_summary=build_report_target_summary(db, report),
            reason=report.reason,
            status=report.status,
            created_at=report.created_at,
            resolved_at=report.resolved_at,
        )
        for report in reports
    ]
    return {"reports": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_my_report(report_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    report = require_report(db, report_id)
    if report.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    return ReportDetailResponse(
        id=report.id,
        reporter_id=report.reporter_id,
        target_type=report.target_type,
        target_id=report.target_id,
        target_summary=build_report_target_summary(db, report),
        reason=report.reason,
        detail=report.detail,
        status=report.status,
        result_message=report.result_message,
        created_at=report.created_at,
        resolved_at=report.resolved_at,
    )
