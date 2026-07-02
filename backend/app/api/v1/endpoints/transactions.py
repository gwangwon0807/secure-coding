from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.endpoints.helpers import check_block_relation, ensure_page_size, get_item_thumbnail, require_transaction
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.enums import ItemStatus, TransactionStatus
from app.models.item import Item
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreateRequest, TransactionDetailResponse, TransactionListEntry, TransactionListResponse, TransactionReasonRequest, TransactionResponse, TransactionStateResponse
from app.utils.pagination import build_pagination


router = APIRouter()


def _transaction_item_summary(item: Item) -> dict:
    return {"id": item.id, "title": item.title, "thumbnail_url": get_item_thumbnail(item), "status": item.status, "price": item.price}


def _transaction_user_summary(user: User) -> dict:
    return {"id": user.id, "nickname": user.nickname}


def _buyer_completed(transaction: Transaction) -> bool:
    return transaction.accepted_at is not None


def _seller_completed(transaction: Transaction) -> bool:
    return transaction.completed_at is not None


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == payload.item_id))
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_REQUEST_OWN_ITEM")
    if item.status in {ItemStatus.HIDDEN, ItemStatus.SOLD}:
        raise HTTPException(status_code=409, detail="ITEM_NOT_AVAILABLE")
    if check_block_relation(db, current_user.id, item.seller_id):
        raise HTTPException(status_code=403, detail="USER_BLOCKED")
    duplicate = db.scalar(
        select(Transaction).where(
            Transaction.item_id == item.id,
            Transaction.buyer_id == current_user.id,
            Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED, TransactionStatus.COMPLETED]),
        )
    )
    if duplicate:
        return duplicate
    transaction = Transaction(
        item_id=item.id,
        buyer_id=current_user.id,
        seller_id=item.seller_id,
        price=payload.price,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    role: str | None = None,
    status_filter: TransactionStatus | None = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Transaction).where(or_(Transaction.buyer_id == current_user.id, Transaction.seller_id == current_user.id))
    if role == "buyer":
        stmt = stmt.where(Transaction.buyer_id == current_user.id)
    elif role == "seller":
        stmt = stmt.where(Transaction.seller_id == current_user.id)
    elif role not in (None, ""):
        raise HTTPException(status_code=422, detail="INVALID_ROLE_VALUE")
    if status_filter:
        stmt = stmt.where(Transaction.status == status_filter)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    transactions = db.scalars(stmt.order_by(Transaction.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    entries = []
    for transaction in transactions:
        item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == transaction.item_id))
        buyer = db.get(User, transaction.buyer_id)
        seller = db.get(User, transaction.seller_id)
        entries.append(
            TransactionListEntry(
                id=transaction.id,
                item=_transaction_item_summary(item),
                buyer=_transaction_user_summary(buyer),
                seller=_transaction_user_summary(seller),
                status=transaction.status,
                buyer_completed=_buyer_completed(transaction),
                seller_completed=_seller_completed(transaction),
                price=transaction.price,
                created_at=transaction.created_at,
                completed_at=transaction.completed_at,
            )
        )
    return {"transactions": entries, "pagination": build_pagination(page, size, total_count)}


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction_detail(transaction_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    transaction = require_transaction(db, transaction_id)
    if current_user.id not in {transaction.buyer_id, transaction.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == transaction.item_id))
    buyer = db.get(User, transaction.buyer_id)
    seller = db.get(User, transaction.seller_id)
    return TransactionDetailResponse(
        id=transaction.id,
        item=_transaction_item_summary(item),
        buyer=_transaction_user_summary(buyer),
        seller=_transaction_user_summary(seller),
        status=transaction.status,
        buyer_completed=_buyer_completed(transaction),
        seller_completed=_seller_completed(transaction),
        price=transaction.price,
        created_at=transaction.created_at,
        accepted_at=transaction.accepted_at,
        rejected_at=transaction.rejected_at,
        canceled_at=transaction.canceled_at,
        completed_at=transaction.completed_at,
    )


@router.patch("/{transaction_id}/accept", response_model=TransactionStateResponse)
def accept_transaction(transaction_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    transaction = require_transaction(db, transaction_id)
    if transaction.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if transaction.status not in {TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED}:
        raise HTTPException(status_code=409, detail="INVALID_TRANSACTION_STATUS")
    item = db.get(Item, transaction.item_id)
    if item.status == ItemStatus.SOLD:
        raise HTTPException(status_code=409, detail="ITEM_NOT_AVAILABLE")
    if item.status != ItemStatus.RESERVED:
        raise HTTPException(status_code=409, detail="ITEM_STATUS_CONFLICT")
    if transaction.completed_at is not None:
        raise HTTPException(status_code=409, detail="SELLER_ALREADY_CONFIRMED")
    transaction.completed_at = datetime.utcnow()
    if transaction.accepted_at is not None and transaction.completed_at is not None:
        transaction.status = TransactionStatus.COMPLETED
        item.status = ItemStatus.SOLD
        db.add(item)
    else:
        transaction.status = TransactionStatus.ACCEPTED
    db.add(transaction)
    db.commit()
    return TransactionStateResponse(
        id=transaction.id,
        status=transaction.status,
        item_id=item.id,
        item_status=item.status,
        buyer_completed=_buyer_completed(transaction),
        seller_completed=_seller_completed(transaction),
        accepted_at=transaction.accepted_at,
        completed_at=transaction.completed_at,
    )


@router.patch("/{transaction_id}/reject", response_model=TransactionStateResponse)
def reject_transaction(
    transaction_id: int,
    payload: TransactionReasonRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    transaction = require_transaction(db, transaction_id)
    if transaction.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if transaction.status != TransactionStatus.REQUESTED:
        raise HTTPException(status_code=409, detail="INVALID_TRANSACTION_STATUS")
    transaction.status = TransactionStatus.REJECTED
    transaction.rejected_at = datetime.utcnow()
    transaction.reject_reason = payload.reason
    db.add(transaction)
    db.commit()
    return TransactionStateResponse(
        id=transaction.id,
        status=transaction.status,
        item_id=transaction.item_id,
        rejected_at=transaction.rejected_at,
        reason=transaction.reject_reason,
    )


@router.patch("/{transaction_id}/complete", response_model=TransactionStateResponse)
def complete_transaction(transaction_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    transaction = require_transaction(db, transaction_id)
    if current_user.id not in {transaction.buyer_id, transaction.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if transaction.status not in {TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED}:
        raise HTTPException(status_code=409, detail="INVALID_TRANSACTION_STATUS")
    item = db.get(Item, transaction.item_id)
    if item.status != ItemStatus.RESERVED:
        raise HTTPException(status_code=409, detail="ITEM_STATUS_CONFLICT")
    if current_user.id == transaction.buyer_id:
        if transaction.accepted_at is not None:
            raise HTTPException(status_code=409, detail="BUYER_ALREADY_CONFIRMED")
        transaction.accepted_at = datetime.utcnow()
    else:
        if transaction.completed_at is not None:
            raise HTTPException(status_code=409, detail="SELLER_ALREADY_CONFIRMED")
        transaction.completed_at = datetime.utcnow()
    if transaction.accepted_at is not None and transaction.completed_at is not None:
        transaction.status = TransactionStatus.COMPLETED
        item.status = ItemStatus.SOLD
        db.add(item)
    else:
        transaction.status = TransactionStatus.ACCEPTED
    db.add(transaction)
    db.commit()
    return TransactionStateResponse(
        id=transaction.id,
        status=transaction.status,
        item_id=item.id,
        item_status=item.status,
        buyer_completed=_buyer_completed(transaction),
        seller_completed=_seller_completed(transaction),
        accepted_at=transaction.accepted_at,
        completed_at=transaction.completed_at,
    )


@router.patch("/{transaction_id}/cancel", response_model=TransactionStateResponse)
def cancel_transaction(
    transaction_id: int,
    payload: TransactionReasonRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    transaction = require_transaction(db, transaction_id)
    if current_user.id not in {transaction.buyer_id, transaction.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if transaction.status not in {TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED}:
        raise HTTPException(status_code=409, detail="INVALID_TRANSACTION_STATUS")
    item = db.get(Item, transaction.item_id)
    transaction.status = TransactionStatus.CANCELED
    transaction.canceled_at = datetime.utcnow()
    transaction.cancel_reason = payload.reason
    if item.status == ItemStatus.RESERVED:
        item.status = ItemStatus.ON_SALE
        db.add(item)
    db.add(transaction)
    db.commit()
    return TransactionStateResponse(
        id=transaction.id,
        status=transaction.status,
        item_id=transaction.item_id,
        item_status=item.status if item else None,
        canceled_at=transaction.canceled_at,
        reason=transaction.cancel_reason,
    )
