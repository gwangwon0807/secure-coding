from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.endpoints.helpers import build_report_target_summary, ensure_page_size, get_item_thumbnail, get_report_count, get_trade_count, record_audit_log, require_report
from app.core.deps import require_admin
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.chat import ChatRoom, Message
from app.models.category import Category
from app.models.community import CommunityComment, CommunityPost, CommunityPostImage
from app.models.enums import AdminActionType, ItemStatus, ReportStatus, ReportTargetType, TransactionStatus, UserStatus, WalletTransactionType
from app.models.item import Item
from app.models.report import Report
from app.models.transaction import Transaction
from app.models.transfer import Transfer, Wallet, WalletLedger
from app.models.user import User
from app.schemas.admin import AdminChatMessageEntry, AdminChatMessageListResponse, AdminChatRoomEntry, AdminChatRoomListResponse, AdminCommunityCommentEntry, AdminCommunityCommentListResponse, AdminCommunityPostEntry, AdminCommunityPostListResponse, AdminItemListEntry, AdminItemListResponse, AdminItemStatusUpdateRequest, AdminItemStatusUpdateResponse, AdminModerationRequest, AdminReportDetailResponse, AdminReportListEntry, AdminReportListResponse, AdminReportUpdateResponse, AdminTransactionListEntry, AdminTransactionListResponse, AdminUserListEntry, AdminUserListResponse, AdminUserStatusUpdateRequest, AdminUserStatusUpdateResponse, AuditLogEntry, AuditLogListResponse
from app.schemas.report import AdminReportUpdateRequest
from app.schemas.transfer import AdminWalletAdjustmentRequest, AdminWalletAdjustmentResponse, AdminWalletEntry, AdminWalletListResponse, TransferHistoryEntry, TransferListResponse
from app.utils.pagination import build_pagination


router = APIRouter()
USER_REPORT_REVIEW_THRESHOLD = 1
INITIAL_WALLET_BALANCE = 100000


def get_or_create_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.scalar(select(Wallet).where(Wallet.user_id == user_id))
    if wallet:
        return wallet
    wallet = Wallet(user_id=user_id, balance=INITIAL_WALLET_BALANCE)
    db.add(wallet)
    db.flush()
    db.add(
        WalletLedger(
            wallet_id=wallet.id,
            transaction_type=WalletTransactionType.INITIAL_CREDIT,
            amount=INITIAL_WALLET_BALANCE,
            balance_after=wallet.balance,
            description="초기 테스트 잔액 지급",
        )
    )
    return wallet


def user_summary(user: User | None) -> dict | None:
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
        "status": user.status,
        "trust_score": user.trust_score,
        "created_at": user.created_at,
    }


def get_pending_user_report_count(db: Session, user_id: int) -> int:
    stmt = select(func.count(Report.id)).where(
        Report.target_type == ReportTargetType.USER,
        Report.target_id == user_id,
        Report.status.in_([ReportStatus.RECEIVED, ReportStatus.REVIEWING]),
    )
    return db.scalar(stmt) or 0


def report_entries_for_target(db: Session, target_type: ReportTargetType, target_id: int) -> list[dict]:
    reports = db.scalars(
        select(Report).where(Report.target_type == target_type, Report.target_id == target_id).order_by(Report.created_at.desc())
    ).all()
    entries = []
    for report in reports:
        reporter = db.get(User, report.reporter_id)
        entries.append(
            {
                "id": report.id,
                "reporter": user_summary(reporter),
                "reason": report.reason,
                "detail": report.detail,
                "status": report.status,
                "action_type": report.action_type,
                "admin_memo": report.admin_memo,
                "created_at": report.created_at,
                "resolved_at": report.resolved_at,
            }
        )
    return entries


def item_detail_payload(db: Session, item_id: int) -> dict:
    item = db.scalar(select(Item).options(selectinload(Item.seller), selectinload(Item.images)).where(Item.id == item_id))
    if not item:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    category = db.get(Category, item.category_id)
    images = [image for image in item.images if image.deleted_at is None]
    images.sort(key=lambda image: image.sort_order)
    transactions = db.scalars(select(Transaction).where(Transaction.item_id == item.id).order_by(Transaction.created_at.desc()).limit(10)).all()
    chat_rooms = db.scalars(select(ChatRoom).where(ChatRoom.item_id == item.id).order_by(ChatRoom.created_at.desc()).limit(10)).all()
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "location": item.location,
        "status": item.status,
        "category": {"id": category.id, "name": category.name} if category else None,
        "seller": user_summary(item.seller),
        "images": [{"id": image.id, "image_url": image.image_url, "sort_order": image.sort_order} for image in images],
        "reports": report_entries_for_target(db, ReportTargetType.ITEM, item.id),
        "transactions": [
            {
                "id": transaction.id,
                "buyer": user_summary(db.get(User, transaction.buyer_id)),
                "seller": user_summary(db.get(User, transaction.seller_id)),
                "status": transaction.status,
                "price": transaction.price,
                "created_at": transaction.created_at,
                "completed_at": transaction.completed_at,
            }
            for transaction in transactions
        ],
        "chat_rooms": [
            {
                "id": room.id,
                "buyer": user_summary(db.get(User, room.buyer_id)),
                "seller": user_summary(db.get(User, room.seller_id)),
                "message_count": db.scalar(select(func.count(Message.id)).where(Message.chat_room_id == room.id)) or 0,
                "created_at": room.created_at,
            }
            for room in chat_rooms
        ],
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "deleted_at": item.deleted_at,
    }


def community_post_detail_payload(db: Session, post_id: int) -> dict:
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="COMMUNITY_POST_NOT_FOUND")
    author = db.get(User, post.author_id)
    images = db.scalars(
        select(CommunityPostImage)
        .where(CommunityPostImage.post_id == post.id, CommunityPostImage.deleted_at.is_(None))
        .order_by(CommunityPostImage.sort_order.asc())
    ).all()
    comments = db.scalars(
        select(CommunityComment).where(CommunityComment.post_id == post.id).order_by(CommunityComment.created_at.asc())
    ).all()
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": user_summary(author),
        "images": [{"id": image.id, "image_url": image.image_url, "sort_order": image.sort_order} for image in images],
        "comments": [
            {
                "id": comment.id,
                "author": user_summary(db.get(User, comment.author_id)),
                "content": comment.content,
                "created_at": comment.created_at,
                "deleted_at": comment.deleted_at,
            }
            for comment in comments
        ],
        "reports": report_entries_for_target(db, ReportTargetType.COMMUNITY_POST, post.id),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "deleted_at": post.deleted_at,
    }


def community_comment_detail_payload(db: Session, comment_id: int) -> dict:
    comment = db.get(CommunityComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="COMMUNITY_COMMENT_NOT_FOUND")
    post = db.get(CommunityPost, comment.post_id)
    return {
        "id": comment.id,
        "content": comment.content,
        "author": user_summary(db.get(User, comment.author_id)),
        "post": {"id": post.id, "title": post.title, "deleted_at": post.deleted_at} if post else None,
        "reports": report_entries_for_target(db, ReportTargetType.COMMUNITY_COMMENT, comment.id),
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "deleted_at": comment.deleted_at,
    }


def chat_room_detail_payload(db: Session, room_id: int) -> dict:
    room = db.get(ChatRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="CHAT_ROOM_NOT_FOUND")
    item = db.get(Item, room.item_id)
    messages = db.scalars(select(Message).where(Message.chat_room_id == room.id).order_by(Message.created_at.asc()).limit(100)).all()
    return {
        "id": room.id,
        "item": {"id": item.id, "title": item.title, "status": item.status, "price": item.price} if item else None,
        "buyer": user_summary(db.get(User, room.buyer_id)),
        "seller": user_summary(db.get(User, room.seller_id)),
        "messages": [
            {
                "id": message.id,
                "sender": user_summary(db.get(User, message.sender_id)),
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at,
            }
            for message in messages
        ],
        "reports": report_entries_for_target(db, ReportTargetType.CHAT_ROOM, room.id),
        "created_at": room.created_at,
        "last_message_at": room.last_message_at,
    }


def transfer_detail_payload(db: Session, transfer_id: int) -> dict:
    transfer = db.get(Transfer, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="TRANSFER_NOT_FOUND")
    return {
        "id": transfer.id,
        "sender": user_summary(db.get(User, transfer.sender_id)),
        "recipient": user_summary(db.get(User, transfer.recipient_id)),
        "amount": transfer.amount,
        "note": transfer.note,
        "status": transfer.status,
        "transaction_id": transfer.transaction_id,
        "chat_room_id": transfer.chat_room_id,
        "created_at": transfer.created_at,
        "canceled_at": transfer.canceled_at,
    }


def user_detail_payload(db: Session, user_id: int) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    items = db.scalars(
        select(Item)
        .options(selectinload(Item.images))
        .where(Item.seller_id == user.id)
        .order_by(Item.created_at.desc())
        .limit(10)
    ).all()
    posts = db.scalars(select(CommunityPost).where(CommunityPost.author_id == user.id).order_by(CommunityPost.created_at.desc()).limit(10)).all()
    comments = db.scalars(select(CommunityComment).where(CommunityComment.author_id == user.id).order_by(CommunityComment.created_at.desc()).limit(10)).all()
    transactions = db.scalars(
        select(Transaction)
        .where(or_(Transaction.buyer_id == user.id, Transaction.seller_id == user.id))
        .order_by(Transaction.created_at.desc())
        .limit(10)
    ).all()
    transfers = db.scalars(
        select(Transfer)
        .where(or_(Transfer.sender_id == user.id, Transfer.recipient_id == user.id))
        .order_by(Transfer.created_at.desc())
        .limit(10)
    ).all()
    chat_rooms = db.scalars(
        select(ChatRoom)
        .where(or_(ChatRoom.buyer_id == user.id, ChatRoom.seller_id == user.id))
        .order_by(ChatRoom.created_at.desc())
        .limit(10)
    ).all()
    wallet = get_or_create_wallet(db, user.id)
    pending_report_count = get_pending_user_report_count(db, user.id)
    return {
        "user": user_summary(user),
        "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "trade_count": get_trade_count(db, user.id),
        "report_count": pending_report_count,
        "needs_review": pending_report_count >= USER_REPORT_REVIEW_THRESHOLD,
        "wallet": {"balance": wallet.balance, "updated_at": wallet.updated_at},
        "reports": report_entries_for_target(db, ReportTargetType.USER, user.id),
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "price": item.price,
                "status": item.status,
                "thumbnail_url": get_item_thumbnail(item),
                "created_at": item.created_at,
                "deleted_at": item.deleted_at,
            }
            for item in items
        ],
        "posts": [
            {"id": post.id, "title": post.title, "created_at": post.created_at, "deleted_at": post.deleted_at}
            for post in posts
        ],
        "comments": [
            {"id": comment.id, "post_id": comment.post_id, "content": comment.content, "created_at": comment.created_at, "deleted_at": comment.deleted_at}
            for comment in comments
        ],
        "transactions": [
            {
                "id": transaction.id,
                "item_id": transaction.item_id,
                "status": transaction.status,
                "price": transaction.price,
                "created_at": transaction.created_at,
                "completed_at": transaction.completed_at,
            }
            for transaction in transactions
        ],
        "transfers": [transfer_detail_payload(db, transfer.id) for transfer in transfers],
        "chat_rooms": [
            {
                "id": room.id,
                "item": {"id": item.id, "title": item.title} if (item := db.get(Item, room.item_id)) else None,
                "buyer": user_summary(db.get(User, room.buyer_id)),
                "seller": user_summary(db.get(User, room.seller_id)),
                "created_at": room.created_at,
            }
            for room in chat_rooms
        ],
    }


def report_target_detail_payload(db: Session, target_type: ReportTargetType, target_id: int) -> dict | None:
    if target_type == ReportTargetType.USER:
        return user_detail_payload(db, target_id)
    if target_type == ReportTargetType.ITEM:
        return item_detail_payload(db, target_id)
    if target_type == ReportTargetType.COMMUNITY_POST:
        return community_post_detail_payload(db, target_id)
    if target_type == ReportTargetType.COMMUNITY_COMMENT:
        return community_comment_detail_payload(db, target_id)
    if target_type == ReportTargetType.CHAT_ROOM:
        return chat_room_detail_payload(db, target_id)
    if target_type == ReportTargetType.MESSAGE:
        message = db.get(Message, target_id)
        if not message:
            return None
        return {"message": {"id": message.id, "content": message.content, "created_at": message.created_at}, "chat_room": chat_room_detail_payload(db, message.chat_room_id)}
    return None


def delete_chat_room_data(db: Session, room_id: int) -> bool:
    room = db.get(ChatRoom, room_id)
    if not room:
        return False
    db.query(Message).filter(Message.chat_room_id == room_id).delete()
    db.delete(room)
    return True


def apply_report_action(db: Session, report: Report, action_type: AdminActionType) -> bool:
    if action_type in {AdminActionType.NONE, AdminActionType.REPORT_REJECTED}:
        return True

    if action_type == AdminActionType.ITEM_HIDDEN and report.target_type == ReportTargetType.ITEM:
        item = db.get(Item, report.target_id)
        if not item:
            return False
        item.status = ItemStatus.HIDDEN
        db.add(item)
        return True

    if action_type == AdminActionType.ITEM_DELETED and report.target_type == ReportTargetType.ITEM:
        item = db.get(Item, report.target_id)
        if not item:
            return False
        item.status = ItemStatus.HIDDEN
        item.deleted_at = datetime.utcnow()
        db.add(item)
        return True

    if action_type == AdminActionType.USER_SUSPENDED and report.target_type == ReportTargetType.USER:
        user = db.get(User, report.target_id)
        if not user:
            return False
        user.status = UserStatus.SUSPENDED
        db.add(user)
        return True

    if action_type == AdminActionType.USER_DELETED and report.target_type == ReportTargetType.USER:
        user = db.get(User, report.target_id)
        if not user:
            return False
        user.status = UserStatus.DELETED
        user.deleted_at = datetime.utcnow()
        db.add(user)
        return True

    if action_type == AdminActionType.COMMUNITY_POST_HIDDEN and report.target_type == ReportTargetType.COMMUNITY_POST:
        post = db.get(CommunityPost, report.target_id)
        if not post:
            return False
        post.deleted_at = datetime.utcnow()
        db.add(post)
        return True

    if action_type == AdminActionType.COMMUNITY_COMMENT_HIDDEN and report.target_type == ReportTargetType.COMMUNITY_COMMENT:
        comment = db.get(CommunityComment, report.target_id)
        if not comment:
            return False
        comment.deleted_at = datetime.utcnow()
        db.add(comment)
        return True

    if action_type == AdminActionType.CHAT_ROOM_DELETED and report.target_type == ReportTargetType.CHAT_ROOM:
        return delete_chat_room_data(db, report.target_id)

    if action_type == AdminActionType.MESSAGE_DELETED and report.target_type == ReportTargetType.MESSAGE:
        message = db.get(Message, report.target_id)
        if not message:
            return False
        db.delete(message)
        return True

    return False


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
    payload = []
    for user in users:
        pending_report_count = get_pending_user_report_count(db, user.id)
        payload.append(
            AdminUserListEntry(
                id=user.id,
                email=user.email,
                nickname=user.nickname,
                role=user.role,
                status=user.status,
                trust_score=user.trust_score,
                trade_count=get_trade_count(db, user.id),
                report_count=pending_report_count,
                needs_review=(pending_report_count >= USER_REPORT_REVIEW_THRESHOLD),
                created_at=user.created_at,
            )
        )
    payload.sort(key=lambda user: (user.needs_review, user.report_count, user.created_at), reverse=True)
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


@router.get("/users/{user_id}")
def get_admin_user_detail(user_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    payload = user_detail_payload(db, user_id)
    db.commit()
    return payload


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


@router.get("/items/{item_id}")
def get_admin_item_detail(item_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return item_detail_payload(db, item_id)


@router.get("/reports", response_model=AdminReportListResponse)
def list_admin_reports(
    status: ReportStatus | None = None,
    target_type: ReportTargetType | None = None,
    reason: str | None = None,
    include_resolved: bool = False,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Report)
    if status:
        stmt = stmt.where(Report.status == status)
    elif not include_resolved:
        stmt = stmt.where(Report.status.notin_([ReportStatus.RESOLVED, ReportStatus.REJECTED]))
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
    target_detail = report_target_detail_payload(db, report.target_type, report.target_id)
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
    next_status = payload.status
    if payload.action_type == AdminActionType.REPORT_REJECTED:
        next_status = ReportStatus.REJECTED
    elif payload.action_type != AdminActionType.NONE:
        next_status = ReportStatus.RESOLVED

    if report.target_type == ReportTargetType.USER and report.target_id == admin_user.id and payload.action_type in {AdminActionType.USER_SUSPENDED, AdminActionType.USER_DELETED}:
        raise HTTPException(status_code=400, detail="CANNOT_UPDATE_SELF_STATUS")

    action_applied = apply_report_action(db, report, payload.action_type)
    if not action_applied:
        raise HTTPException(status_code=400, detail="INVALID_REPORT_ACTION_FOR_TARGET")

    report.status = next_status
    report.action_type = payload.action_type
    report.admin_id = admin_user.id
    report.admin_memo = payload.admin_memo
    report.result_message = payload.result_message
    if next_status in {ReportStatus.RESOLVED, ReportStatus.REJECTED}:
        report.resolved_at = datetime.utcnow()
    else:
        report.resolved_at = None
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


@router.get("/community/posts", response_model=AdminCommunityPostListResponse)
def list_admin_community_posts(
    keyword: str | None = None,
    reported_only: bool = False,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(CommunityPost)
    if keyword:
        stmt = stmt.where(or_(CommunityPost.title.ilike(f"%{keyword}%"), CommunityPost.content.ilike(f"%{keyword}%")))
    if reported_only:
        reported_ids = select(Report.target_id).where(Report.target_type == ReportTargetType.COMMUNITY_POST)
        stmt = stmt.where(CommunityPost.id.in_(reported_ids))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    posts = db.scalars(stmt.order_by(CommunityPost.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for post in posts:
        author = db.get(User, post.author_id)
        comment_count = db.scalar(
            select(func.count(CommunityComment.id)).where(CommunityComment.post_id == post.id, CommunityComment.deleted_at.is_(None))
        ) or 0
        report_count = db.scalar(
            select(func.count(Report.id)).where(Report.target_type == ReportTargetType.COMMUNITY_POST, Report.target_id == post.id)
        ) or 0
        payload.append(
            AdminCommunityPostEntry(
                id=post.id,
                title=post.title,
                author={"id": author.id, "nickname": author.nickname},
                comment_count=comment_count,
                report_count=report_count,
                created_at=post.created_at,
                deleted_at=post.deleted_at,
            )
        )
    return {"posts": payload, "pagination": build_pagination(page, size, total_count)}


@router.patch("/community/posts/{post_id}/hide")
def hide_community_post(
    post_id: int,
    payload: AdminModerationRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="COMMUNITY_POST_NOT_FOUND")
    if post.deleted_at is None:
        post.deleted_at = datetime.utcnow()
        action = "HIDE_COMMUNITY_POST"
    else:
        post.deleted_at = None
        action = "RESTORE_COMMUNITY_POST"
    db.add(post)
    record_audit_log(db, admin_user.id, action, "COMMUNITY_POST", post.id, payload.reason)
    db.commit()
    return {"message": "처리되었습니다."}


@router.get("/community/posts/{post_id}")
def get_admin_community_post_detail(post_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return community_post_detail_payload(db, post_id)


@router.get("/community/comments", response_model=AdminCommunityCommentListResponse)
def list_admin_community_comments(
    keyword: str | None = None,
    reported_only: bool = False,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(CommunityComment)
    if keyword:
        stmt = stmt.where(CommunityComment.content.ilike(f"%{keyword}%"))
    if reported_only:
        reported_ids = select(Report.target_id).where(Report.target_type == ReportTargetType.COMMUNITY_COMMENT)
        stmt = stmt.where(CommunityComment.id.in_(reported_ids))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    comments = db.scalars(stmt.order_by(CommunityComment.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for comment in comments:
        author = db.get(User, comment.author_id)
        post = db.get(CommunityPost, comment.post_id)
        report_count = db.scalar(
            select(func.count(Report.id)).where(Report.target_type == ReportTargetType.COMMUNITY_COMMENT, Report.target_id == comment.id)
        ) or 0
        payload.append(
            AdminCommunityCommentEntry(
                id=comment.id,
                post_id=comment.post_id,
                post_title=post.title if post else None,
                author={"id": author.id, "nickname": author.nickname},
                content=comment.content,
                report_count=report_count,
                created_at=comment.created_at,
                deleted_at=comment.deleted_at,
            )
        )
    return {"comments": payload, "pagination": build_pagination(page, size, total_count)}


@router.patch("/community/comments/{comment_id}/hide")
def hide_community_comment(
    comment_id: int,
    payload: AdminModerationRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    comment = db.get(CommunityComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="COMMUNITY_COMMENT_NOT_FOUND")
    if comment.deleted_at is None:
        comment.deleted_at = datetime.utcnow()
        action = "HIDE_COMMUNITY_COMMENT"
    else:
        comment.deleted_at = None
        action = "RESTORE_COMMUNITY_COMMENT"
    db.add(comment)
    record_audit_log(db, admin_user.id, action, "COMMUNITY_COMMENT", comment.id, payload.reason)
    db.commit()
    return {"message": "처리되었습니다."}


@router.get("/community/comments/{comment_id}")
def get_admin_community_comment_detail(comment_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return community_comment_detail_payload(db, comment_id)


@router.get("/chat-rooms", response_model=AdminChatRoomListResponse)
def list_admin_chat_rooms(
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(ChatRoom)
    if keyword:
        item_ids = select(Item.id).where(Item.title.ilike(f"%{keyword}%"))
        stmt = stmt.where(ChatRoom.item_id.in_(item_ids))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rooms = db.scalars(stmt.order_by(ChatRoom.last_message_at.desc().nullslast(), ChatRoom.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for room in rooms:
        item = db.get(Item, room.item_id)
        buyer = db.get(User, room.buyer_id)
        seller = db.get(User, room.seller_id)
        message_count = db.scalar(select(func.count(Message.id)).where(Message.chat_room_id == room.id)) or 0
        payload.append(
            AdminChatRoomEntry(
                id=room.id,
                item={"id": item.id, "title": item.title} if item else {"id": room.item_id, "title": f"상품 {room.item_id}"},
                buyer={"id": buyer.id, "nickname": buyer.nickname},
                seller={"id": seller.id, "nickname": seller.nickname},
                message_count=message_count,
                last_message_at=room.last_message_at,
                created_at=room.created_at,
            )
        )
    return {"chat_rooms": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/chat-rooms/{room_id}/messages", response_model=AdminChatMessageListResponse)
def list_admin_chat_messages(
    room_id: int,
    page: int = 1,
    size: int = 50,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    room = db.get(ChatRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="CHAT_ROOM_NOT_FOUND")
    stmt = select(Message).where(Message.chat_room_id == room_id)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    messages = db.scalars(stmt.order_by(Message.created_at.asc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for message in messages:
        sender = db.get(User, message.sender_id)
        payload.append(
            AdminChatMessageEntry(
                id=message.id,
                sender={"id": sender.id, "nickname": sender.nickname},
                content=message.content,
                created_at=message.created_at,
            )
        )
    return {"messages": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/chat-rooms/{room_id}")
def get_admin_chat_room_detail(room_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return chat_room_detail_payload(db, room_id)


@router.delete("/chat-rooms/{room_id}")
def delete_admin_chat_room(
    room_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not delete_chat_room_data(db, room_id):
        raise HTTPException(status_code=404, detail="CHAT_ROOM_NOT_FOUND")
    record_audit_log(db, admin_user.id, "DELETE_CHAT_ROOM", "CHAT_ROOM", room_id, "관리자 삭제")
    db.commit()
    return {"message": "채팅방이 삭제되었습니다."}


@router.get("/wallets", response_model=AdminWalletListResponse)
def list_admin_wallets(
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(User)
    if keyword:
        stmt = stmt.where(or_(User.email.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%")))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    users = db.scalars(stmt.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for user in users:
        wallet = get_or_create_wallet(db, user.id)
        payload.append(
            AdminWalletEntry(
                user={"id": user.id, "nickname": user.nickname},
                balance=wallet.balance,
                updated_at=wallet.updated_at,
            )
        )
    db.commit()
    return {"wallets": payload, "pagination": build_pagination(page, size, total_count)}


@router.patch("/wallets/{user_id}/adjust", response_model=AdminWalletAdjustmentResponse)
def adjust_admin_wallet_balance(
    user_id: int,
    payload: AdminWalletAdjustmentRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    wallet = get_or_create_wallet(db, user.id)
    next_balance = wallet.balance + payload.amount
    if next_balance < 0:
        raise HTTPException(status_code=409, detail="INSUFFICIENT_BALANCE")
    wallet.balance = next_balance
    db.add(wallet)
    db.flush()
    db.add(
        WalletLedger(
            wallet_id=wallet.id,
            transaction_type=WalletTransactionType.ADMIN_ADJUSTMENT,
            amount=payload.amount,
            balance_after=wallet.balance,
            description=payload.reason,
        )
    )
    record_audit_log(db, admin_user.id, "ADJUST_WALLET_BALANCE", "WALLET", user.id, payload.reason)
    db.commit()
    db.refresh(wallet)
    return AdminWalletAdjustmentResponse(
        user_id=user.id,
        balance=wallet.balance,
        amount=payload.amount,
        reason=payload.reason,
        updated_at=wallet.updated_at,
    )


@router.get("/transfers", response_model=TransferListResponse)
def list_admin_transfers(
    page: int = 1,
    size: int = 20,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Transfer)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    transfers = db.scalars(stmt.order_by(Transfer.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for transfer in transfers:
        sender = db.get(User, transfer.sender_id)
        recipient = db.get(User, transfer.recipient_id)
        payload.append(
            TransferHistoryEntry(
                id=transfer.id,
                sender={"id": sender.id, "nickname": sender.nickname},
                recipient={"id": recipient.id, "nickname": recipient.nickname},
                amount=transfer.amount,
                note=transfer.note,
                status=transfer.status,
                transaction_id=transfer.transaction_id,
                chat_room_id=transfer.chat_room_id,
                created_at=transfer.created_at,
            )
        )
    return {"transfers": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/transfers/{transfer_id}")
def get_admin_transfer_detail(transfer_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return transfer_detail_payload(db, transfer_id)


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
