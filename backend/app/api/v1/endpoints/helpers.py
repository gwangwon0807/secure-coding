from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.block import Block
from app.models.category import Category
from app.models.chat import ChatRoom, Message
from app.models.community import CommunityComment, CommunityPost
from app.models.enums import ItemStatus, ReportTargetType, TransactionStatus, UserStatus
from app.models.item import Item
from app.models.item_image import ItemImage
from app.models.report import Report
from app.models.transaction import Transaction
from app.models.user import User


def ensure_page_size(page: int, size: int) -> None:
    if page < 1:
        raise HTTPException(status_code=422, detail="INVALID_PAGE_VALUE")
    if size < 1 or size > 100:
        raise HTTPException(status_code=422, detail="INVALID_SIZE_VALUE")


def check_block_relation(db: Session, user_a: int, user_b: int) -> bool:
    stmt = select(Block).where(
        Block.deleted_at.is_(None),
        or_(
            (Block.blocker_id == user_a) & (Block.blocked_user_id == user_b),
            (Block.blocker_id == user_b) & (Block.blocked_user_id == user_a),
        ),
    )
    return db.scalar(stmt) is not None


def get_trade_count(db: Session, user_id: int) -> int:
    stmt = select(func.count(Transaction.id)).where(
        Transaction.status == TransactionStatus.COMPLETED,
        or_(Transaction.buyer_id == user_id, Transaction.seller_id == user_id),
    )
    return db.scalar(stmt) or 0


def get_report_count(db: Session, user_id: int) -> int:
    stmt = select(func.count(Report.id)).where(
        Report.target_type == ReportTargetType.USER,
        Report.target_id == user_id,
    )
    return db.scalar(stmt) or 0


def get_item_thumbnail(item: Item) -> str | None:
    valid_images = [img for img in item.images if img.deleted_at is None]
    if not valid_images:
        return None
    valid_images.sort(key=lambda image: image.sort_order)
    return valid_images[0].image_url


def require_item(db: Session, item_id: int, include_hidden: bool = False) -> Item:
    item = db.get(Item, item_id)
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if not include_hidden and item.status == ItemStatus.HIDDEN:
        raise HTTPException(status_code=404, detail="ITEM_HIDDEN")
    return item


def require_transaction(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="TRANSACTION_NOT_FOUND")
    return transaction


def require_chat_room(db: Session, room_id: int) -> ChatRoom:
    room = db.get(ChatRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="CHAT_ROOM_NOT_FOUND")
    return room


def require_report(db: Session, report_id: int) -> Report:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="REPORT_NOT_FOUND")
    return report


def ensure_user_active(user: User) -> None:
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="USER_NOT_ACTIVE")


def record_audit_log(db: Session, admin_id: int, action: str, target_type: str, target_id: int, reason: str) -> None:
    db.add(
        AuditLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
        )
    )


def build_report_target_summary(db: Session, report: Report) -> str | None:
    if report.target_type == ReportTargetType.ITEM:
        item = db.get(Item, report.target_id)
        return item.title if item else None
    if report.target_type == ReportTargetType.USER:
        user = db.get(User, report.target_id)
        return user.nickname if user else None
    if report.target_type == ReportTargetType.COMMUNITY_POST:
        post = db.get(CommunityPost, report.target_id)
        return post.title if post else None
    if report.target_type == ReportTargetType.COMMUNITY_COMMENT:
        comment = db.get(CommunityComment, report.target_id)
        return comment.content[:30] if comment else None
    if report.target_type == ReportTargetType.CHAT_ROOM:
        room = db.get(ChatRoom, report.target_id)
        if not room:
            return None
        item = db.get(Item, room.item_id)
        return item.title if item else f"채팅방 {room.id}"
    if report.target_type == ReportTargetType.MESSAGE:
        message = db.get(Message, report.target_id)
        return message.content[:30] if message else None
    return None
