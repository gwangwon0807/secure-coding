from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.helpers import check_block_relation, ensure_page_size
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.chat import ChatRoom
from app.models.enums import UserStatus, WalletTransactionType
from app.models.transaction import Transaction
from app.models.transfer import Transfer, Wallet, WalletLedger
from app.models.user import User
from app.schemas.transfer import TransferCreateRequest, TransferDetailResponse, TransferHistoryEntry, TransferListResponse, WalletBalanceChangeRequest, WalletBalanceChangeResponse, WalletLedgerEntry, WalletLedgerResponse, WalletSummaryResponse
from app.utils.pagination import build_pagination


router = APIRouter()
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


def build_party_summary(user: User) -> dict:
    return {"id": user.id, "nickname": user.nickname}


@router.get("/wallet/me", response_model=WalletSummaryResponse)
def get_my_wallet(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    wallet = get_or_create_wallet(db, current_user.id)
    db.commit()
    db.refresh(wallet)
    return WalletSummaryResponse(user=build_party_summary(current_user), balance=wallet.balance)


@router.get("/wallet/me/ledger", response_model=WalletLedgerResponse)
def get_my_wallet_ledger(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    wallet = get_or_create_wallet(db, current_user.id)
    db.commit()
    stmt = select(WalletLedger).where(WalletLedger.wallet_id == wallet.id)
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    ledger = db.scalars(stmt.order_by(WalletLedger.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    return {
        "ledger": [
            WalletLedgerEntry(
                id=entry.id,
                transfer_id=entry.transfer_id,
                transaction_type=entry.transaction_type,
                amount=entry.amount,
                balance_after=entry.balance_after,
                description=entry.description,
                counterparty_user_id=entry.counterparty_user_id,
                created_at=entry.created_at,
            )
            for entry in ledger
        ],
        "pagination": build_pagination(page, size, total_count),
    }


@router.post("/wallet/me/deposit", response_model=WalletBalanceChangeResponse)
def deposit_my_wallet(
    payload: WalletBalanceChangeRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(db, current_user.id)
    wallet.balance += payload.amount
    db.add(wallet)
    db.flush()
    db.add(
        WalletLedger(
            wallet_id=wallet.id,
            transaction_type=WalletTransactionType.USER_DEPOSIT,
            amount=payload.amount,
            balance_after=wallet.balance,
            description="내 지갑 입금",
        )
    )
    db.commit()
    db.refresh(wallet)
    return WalletBalanceChangeResponse(
        balance=wallet.balance,
        amount=payload.amount,
        transaction_type=WalletTransactionType.USER_DEPOSIT,
        updated_at=wallet.updated_at,
    )


@router.post("/wallet/me/withdraw", response_model=WalletBalanceChangeResponse)
def withdraw_my_wallet(
    payload: WalletBalanceChangeRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(db, current_user.id)
    if wallet.balance < payload.amount:
        raise HTTPException(status_code=409, detail="INSUFFICIENT_BALANCE")
    wallet.balance -= payload.amount
    db.add(wallet)
    db.flush()
    db.add(
        WalletLedger(
            wallet_id=wallet.id,
            transaction_type=WalletTransactionType.USER_WITHDRAWAL,
            amount=-payload.amount,
            balance_after=wallet.balance,
            description="내 지갑 출금",
        )
    )
    db.commit()
    db.refresh(wallet)
    return WalletBalanceChangeResponse(
        balance=wallet.balance,
        amount=payload.amount,
        transaction_type=WalletTransactionType.USER_WITHDRAWAL,
        updated_at=wallet.updated_at,
    )


@router.post("", response_model=TransferDetailResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    payload: TransferCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    if payload.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_TRANSFER_TO_SELF")
    recipient = db.get(User, payload.recipient_id)
    if not recipient or recipient.deleted_at is not None:
        raise HTTPException(status_code=404, detail="RECIPIENT_NOT_FOUND")
    if recipient.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="RECIPIENT_NOT_ACTIVE")
    if check_block_relation(db, current_user.id, recipient.id):
        raise HTTPException(status_code=403, detail="USER_BLOCKED")
    if payload.transaction_id:
        transaction = db.get(Transaction, payload.transaction_id)
        if not transaction or current_user.id not in {transaction.buyer_id, transaction.seller_id} or payload.recipient_id not in {transaction.buyer_id, transaction.seller_id}:
            raise HTTPException(status_code=403, detail="INVALID_TRANSACTION_CONTEXT")
    if payload.chat_room_id:
        chat_room = db.get(ChatRoom, payload.chat_room_id)
        if not chat_room or current_user.id not in {chat_room.buyer_id, chat_room.seller_id} or payload.recipient_id not in {chat_room.buyer_id, chat_room.seller_id}:
            raise HTTPException(status_code=403, detail="INVALID_CHAT_ROOM_CONTEXT")

    sender_wallet = get_or_create_wallet(db, current_user.id)
    recipient_wallet = get_or_create_wallet(db, recipient.id)
    if sender_wallet.balance < payload.amount:
        raise HTTPException(status_code=409, detail="INSUFFICIENT_BALANCE")

    sender_wallet.balance -= payload.amount
    recipient_wallet.balance += payload.amount
    db.add(sender_wallet)
    db.add(recipient_wallet)
    db.flush()

    transfer = Transfer(
        sender_id=current_user.id,
        recipient_id=recipient.id,
        amount=payload.amount,
        note=payload.note,
        transaction_id=payload.transaction_id,
        chat_room_id=payload.chat_room_id,
    )
    db.add(transfer)
    db.flush()

    db.add(
        WalletLedger(
            wallet_id=sender_wallet.id,
            transfer_id=transfer.id,
            transaction_type=WalletTransactionType.TRANSFER_OUT,
            amount=-payload.amount,
            balance_after=sender_wallet.balance,
            description=payload.note or f"{recipient.nickname}님에게 송금",
            counterparty_user_id=recipient.id,
        )
    )
    db.add(
        WalletLedger(
            wallet_id=recipient_wallet.id,
            transfer_id=transfer.id,
            transaction_type=WalletTransactionType.TRANSFER_IN,
            amount=payload.amount,
            balance_after=recipient_wallet.balance,
            description=payload.note or f"{current_user.nickname}님에게서 송금",
            counterparty_user_id=current_user.id,
        )
    )
    db.commit()
    db.refresh(transfer)
    return TransferDetailResponse(
        id=transfer.id,
        sender=build_party_summary(current_user),
        recipient=build_party_summary(recipient),
        amount=transfer.amount,
        note=transfer.note,
        status=transfer.status,
        transaction_id=transfer.transaction_id,
        chat_room_id=transfer.chat_room_id,
        created_at=transfer.created_at,
        canceled_at=transfer.canceled_at,
    )


@router.get("", response_model=TransferListResponse)
def list_my_transfers(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(Transfer).where(or_(Transfer.sender_id == current_user.id, Transfer.recipient_id == current_user.id))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    transfers = db.scalars(stmt.order_by(Transfer.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for transfer in transfers:
        sender = db.get(User, transfer.sender_id)
        recipient = db.get(User, transfer.recipient_id)
        payload.append(
            TransferHistoryEntry(
                id=transfer.id,
                sender=build_party_summary(sender),
                recipient=build_party_summary(recipient),
                amount=transfer.amount,
                note=transfer.note,
                status=transfer.status,
                transaction_id=transfer.transaction_id,
                chat_room_id=transfer.chat_room_id,
                created_at=transfer.created_at,
            )
        )
    return {"transfers": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/{transfer_id}", response_model=TransferDetailResponse)
def get_transfer_detail(transfer_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    transfer = db.get(Transfer, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="TRANSFER_NOT_FOUND")
    if current_user.id not in {transfer.sender_id, transfer.recipient_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    sender = db.get(User, transfer.sender_id)
    recipient = db.get(User, transfer.recipient_id)
    return TransferDetailResponse(
        id=transfer.id,
        sender=build_party_summary(sender),
        recipient=build_party_summary(recipient),
        amount=transfer.amount,
        note=transfer.note,
        status=transfer.status,
        transaction_id=transfer.transaction_id,
        chat_room_id=transfer.chat_room_id,
        created_at=transfer.created_at,
        canceled_at=transfer.canceled_at,
    )
