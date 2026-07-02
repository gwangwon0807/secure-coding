from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.endpoints.helpers import build_report_target_summary, ensure_page_size, get_item_thumbnail, get_report_count, get_trade_count, record_audit_log, require_report
from app.core.deps import require_admin
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.enums import AdminActionType, ItemStatus, ReportStatus, ReportTargetType, TransactionStatus, UserStatus
from app.models.item import Item
from app.models.report import Report
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.admin import AdminItemListEntry, AdminItemListResponse, AdminItemStatusUpdateRequest, AdminItemStatusUpdateResponse, AdminReportDetailResponse, AdminReportListEntry, AdminReportListResponse, AdminReportUpdateResponse, AdminTransactionListEntry, AdminTransactionListResponse, AdminUserListEntry, AdminUserListResponse, AdminUserStatusUpdateRequest, AdminUserStatusUpdateResponse, AuditLogEntry, AuditLogListResponse
from app.schemas.report import AdminReportUpdateRequest
from app.utils.pagination import build_pagination


router = APIRouter()


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    keyword: str | None = None,
    status: UserStatus | None = None,
    role: str | None = None,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(User)
    if keyword:
        stmt = stmt.where(or_(User.email.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%")))
    if status:
        stmt = stmt.where(User.status == status)
    if role:
        stmt = stmt.where(User.role == role)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    users = db.scalars(stmt.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = [
        AdminUserListEntry(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            role=user.role,
            status=user.status,
            trust_score=user.trust_score,
            trade_count=get_trade_count(db, user.id),
            report_count=get_report_count(db, user.id),
            created_at=user.created_at,
        )
        for user in users
    ]
    return {"users": payload, "pagination": build_pagination(page, size, total_count)}


@router.patch("/users/{user_id}/status", response_model=AdminUserStatusUpdateResponse)
def update_user_status(
    user_id: int,
    payload: AdminUserStatusUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_UPDATE_SELF_STATUS")
    if payload.status == UserStatus.DELETED:
        active_transaction = db.scalar(
            select(Transaction).where(
                or_(Transaction.buyer_id == user.id, Transaction.seller_id == user.id),
                Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED]),
            )
        )
        if active_transaction:
            raise HTTPException(status_code=409, detail="ACTIVE_TRANSACTION_EXISTS")
        user.deleted_at = datetime.utcnow()
    previous_status = user.status
    user.status = payload.status
    db.add(user)
    record_audit_log(db, admin_user.id, "UPDATE_USER_STATUS", "USER", user.id, payload.reason)
    db.commit()
    db.refresh(user)
    return AdminUserStatusUpdateResponse(
        id=user.id,
        previous_status=previous_status,
        status=user.status,
        reason=payload.reason,
        updated_at=user.updated_at,
    )


@router.get("/items", response_model=AdminItemListResponse)
def list_admin_items(
    keyword: str | None = None,
    seller_id: int | None = None,
    category_id: int | None = None,
    status: ItemStatus | None = None,
    reported_only: bool = False,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Item).options(selectinload(Item.seller), selectinload(Item.images))
    if keyword:
        stmt = stmt.where(or_(Item.title.ilike(f"%{keyword}%"), Item.description.ilike(f"%{keyword}%")))
    if seller_id:
        stmt = stmt.where(Item.seller_id == seller_id)
    if category_id:
        stmt = stmt.where(Item.category_id == category_id)
    if status:
        stmt = stmt.where(Item.status == status)
    if reported_only:
        reported_ids = select(Report.target_id).where(Report.target_type == ReportTargetType.ITEM)
        stmt = stmt.where(Item.id.in_(reported_ids))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Item.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for item in items:
        report_count = db.scalar(
            select(func.count(Report.id)).where(Report.target_type == ReportTargetType.ITEM, Report.target_id == item.id)
        ) or 0
        payload.append(
            AdminItemListEntry(
                id=item.id,
                title=item.title,
                price=item.price,
                status=item.status,
                seller={"id": item.seller.id, "email": item.seller.email, "nickname": item.seller.nickname},
                report_count=report_count,
                created_at=item.created_at,
                updated_at=item.updated_at,
                deleted_at=item.deleted_at,
            )
        )
    return {"items": payload, "pagination": build_pagination(page, size, total_count)}


@router.patch("/items/{item_id}/status", response_model=AdminItemStatusUpdateResponse)
def update_admin_item_status(
    item_id: int,
    payload: AdminItemStatusUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.deleted_at is not None:
        raise HTTPException(status_code=409, detail="ITEM_ALREADY_DELETED")
    active_transaction = db.scalar(
        select(Transaction).where(
            Transaction.item_id == item.id,
            Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED]),
        )
    )
    if active_transaction:
        raise HTTPException(status_code=409, detail="ACTIVE_TRANSACTION_EXISTS")
    previous_status = item.status
    item.status = payload.status
    db.add(item)
    record_audit_log(db, admin_user.id, "UPDATE_ITEM_STATUS", "ITEM", item.id, payload.reason)
    db.commit()
    db.refresh(item)
    return AdminItemStatusUpdateResponse(
        id=item.id,
        previous_status=previous_status,
        status=item.status,
        reason=payload.reason,
        updated_at=item.updated_at,
    )


@router.get("/reports", response_model=AdminReportListResponse)
def list_admin_reports(
    status: ReportStatus | None = None,
    target_type: ReportTargetType | None = None,
    reason: str | None = None,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Report)
    if status:
        stmt = stmt.where(Report.status == status)
    if target_type:
        stmt = stmt.where(Report.target_type == target_type)
    if reason:
        stmt = stmt.where(Report.reason == reason)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    reports = db.scalars(stmt.order_by(Report.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for report in reports:
        reporter = db.get(User, report.reporter_id)
        payload.append(
            AdminReportListEntry(
                id=report.id,
                reporter={"id": reporter.id, "nickname": reporter.nickname},
                target_type=report.target_type,
                target_id=report.target_id,
                target_summary=build_report_target_summary(db, report),
                reason=report.reason,
                status=report.status,
                created_at=report.created_at,
                resolved_at=report.resolved_at,
            )
        )
    return {"reports": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/reports/{report_id}", response_model=AdminReportDetailResponse)
def get_admin_report(report_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    report = require_report(db, report_id)
    reporter = db.get(User, report.reporter_id)
    target_detail = {"summary": build_report_target_summary(db, report)}
    return AdminReportDetailResponse(
        id=report.id,
        reporter={"id": reporter.id, "email": reporter.email, "nickname": reporter.nickname},
        target_type=report.target_type,
        target_id=report.target_id,
        target_detail=target_detail,
        reason=report.reason,
        detail=report.detail,
        status=report.status,
        admin_id=report.admin_id,
        admin_memo=report.admin_memo,
        action_type=report.action_type,
        created_at=report.created_at,
        resolved_at=report.resolved_at,
    )


@router.patch("/reports/{report_id}", response_model=AdminReportUpdateResponse)
def update_admin_report(
    report_id: int,
    payload: AdminReportUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    report = require_report(db, report_id)
    report.status = payload.status
    report.action_type = payload.action_type
    report.admin_id = admin_user.id
    report.admin_memo = payload.admin_memo
    report.result_message = payload.result_message
    if payload.status in {ReportStatus.RESOLVED, ReportStatus.REJECTED}:
        report.resolved_at = datetime.utcnow()
    if payload.action_type == AdminActionType.ITEM_HIDDEN and report.target_type == ReportTargetType.ITEM:
        item = db.get(Item, report.target_id)
        if item:
            item.status = ItemStatus.HIDDEN
            db.add(item)
    if payload.action_type == AdminActionType.USER_SUSPENDED and report.target_type == ReportTargetType.USER:
        user = db.get(User, report.target_id)
        if user:
            user.status = UserStatus.SUSPENDED
            db.add(user)
    db.add(report)
    record_audit_log(db, admin_user.id, "UPDATE_REPORT", "REPORT", report.id, payload.admin_memo or payload.action_type.value)
    db.commit()
    return AdminReportUpdateResponse(
        id=report.id,
        status=report.status,
        action_type=report.action_type,
        admin_memo=report.admin_memo,
        result_message=report.result_message,
        resolved_at=report.resolved_at,
    )


@router.get("/transactions", response_model=AdminTransactionListResponse)
def list_admin_transactions(
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Transaction)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    transactions = db.scalars(stmt.order_by(Transaction.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for transaction in transactions:
        item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == transaction.item_id))
        buyer = db.get(User, transaction.buyer_id)
        seller = db.get(User, transaction.seller_id)
        payload.append(
            AdminTransactionListEntry(
                id=transaction.id,
                item={"id": item.id, "title": item.title, "thumbnail_url": get_item_thumbnail(item), "status": item.status},
                buyer={"id": buyer.id, "nickname": buyer.nickname},
                seller={"id": seller.id, "nickname": seller.nickname},
                status=transaction.status,
                price=transaction.price,
                created_at=transaction.created_at,
                completed_at=transaction.completed_at,
            )
        )
    return {"transactions": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/audit-logs", response_model=AuditLogListResponse)
def list_audit_logs(
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(AuditLog)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    logs = db.scalars(stmt.order_by(AuditLog.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = [
        AuditLogEntry(
            id=log.id,
            admin_id=log.admin_id,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            reason=log.reason,
            created_at=log.created_at,
        )
        for log in logs
    ]
    return {"audit_logs": payload, "pagination": build_pagination(page, size, total_count)}
