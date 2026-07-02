from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.endpoints.helpers import check_block_relation, ensure_page_size, get_item_thumbnail, require_chat_room
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.chat import ChatRoom, Message
from app.models.enums import ItemStatus, MessageType, TransactionStatus
from app.models.item import Item
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.chat import ChatRoomCreateRequest, ChatRoomCreateResponse, ChatRoomDeleteResponse, ChatRoomDetailResponse, ChatRoomListEntry, ChatRoomListResponse, MessageCreateRequest, MessageEntry, MessageListResponse, ReadRequest, ReadResponse
from app.utils.pagination import build_pagination


router = APIRouter()


@router.post("", response_model=ChatRoomCreateResponse, status_code=status.HTTP_201_CREATED)
def create_chat_room(
    payload: ChatRoomCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == payload.item_id))
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_CHAT_OWN_ITEM")
    if item.status in {ItemStatus.HIDDEN, ItemStatus.SOLD}:
        raise HTTPException(status_code=409, detail="ITEM_NOT_AVAILABLE")
    if check_block_relation(db, current_user.id, item.seller_id):
        raise HTTPException(status_code=403, detail="USER_BLOCKED")
    existing = db.scalar(
        select(ChatRoom).where(
            ChatRoom.item_id == item.id,
            ChatRoom.buyer_id == current_user.id,
            ChatRoom.seller_id == item.seller_id,
        )
    )
    if existing:
        return ChatRoomCreateResponse(
            id=existing.id,
            item_id=existing.item_id,
            buyer_id=existing.buyer_id,
            seller_id=existing.seller_id,
            created_at=existing.created_at,
            is_new=False,
        )
    room = ChatRoom(item_id=item.id, buyer_id=current_user.id, seller_id=item.seller_id)
    db.add(room)
    db.commit()
    db.refresh(room)
    return ChatRoomCreateResponse(
        id=room.id,
        item_id=room.item_id,
        buyer_id=room.buyer_id,
        seller_id=room.seller_id,
        created_at=room.created_at,
        is_new=True,
    )


@router.get("", response_model=ChatRoomListResponse)
def list_chat_rooms(page: int = 1, size: int = 20, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    ensure_page_size(page, size)
    stmt = select(ChatRoom).where(or_(ChatRoom.buyer_id == current_user.id, ChatRoom.seller_id == current_user.id))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rooms = db.scalars(
        stmt.order_by(ChatRoom.last_message_at.desc().nullslast(), ChatRoom.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    payload = []
    for room in rooms:
        item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == room.item_id))
        opponent_id = room.seller_id if room.buyer_id == current_user.id else room.buyer_id
        opponent = db.get(User, opponent_id)
        last_message = db.scalar(select(Message).where(Message.chat_room_id == room.id).order_by(Message.created_at.desc()).limit(1))
        unread_count = db.scalar(
            select(func.count(Message.id)).where(
                Message.chat_room_id == room.id,
                Message.sender_id != current_user.id,
                Message.is_read.is_(False),
            )
        ) or 0
        payload.append(
            ChatRoomListEntry(
                id=room.id,
                item={"id": item.id, "title": item.title, "thumbnail_url": get_item_thumbnail(item), "status": item.status},
                opponent={"id": opponent.id, "nickname": opponent.nickname},
                last_message={"content": last_message.content, "created_at": last_message.created_at} if last_message else None,
                unread_count=unread_count,
            )
        )
    return {"chat_rooms": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/{room_id}", response_model=ChatRoomDetailResponse)
def get_chat_room(room_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    room = require_chat_room(db, room_id)
    if current_user.id not in {room.buyer_id, room.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if check_block_relation(db, room.buyer_id, room.seller_id):
        raise HTTPException(status_code=403, detail="USER_BLOCKED")
    item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == room.item_id))
    buyer = db.get(User, room.buyer_id)
    seller = db.get(User, room.seller_id)
    opponent = seller if current_user.id == room.buyer_id else buyer
    transaction = db.scalar(
        select(Transaction)
        .where(
            Transaction.item_id == room.item_id,
            Transaction.buyer_id == room.buyer_id,
            Transaction.seller_id == room.seller_id,
            Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED, TransactionStatus.COMPLETED]),
        )
        .order_by(Transaction.created_at.desc())
        .limit(1)
    )
    return ChatRoomDetailResponse(
        id=room.id,
        item={"id": item.id, "title": item.title, "price": item.price, "thumbnail_url": get_item_thumbnail(item), "status": item.status},
        buyer={"id": buyer.id, "nickname": buyer.nickname},
        seller={"id": seller.id, "nickname": seller.nickname},
        opponent={"id": opponent.id, "nickname": opponent.nickname},
        transaction=(
            {
                "id": transaction.id,
                "status": transaction.status,
                "buyer_completed": transaction.accepted_at is not None,
                "seller_completed": transaction.completed_at is not None,
            }
            if transaction
            else None
        ),
        created_at=room.created_at,
        last_message_at=room.last_message_at,
    )


@router.get("/{room_id}/messages", response_model=MessageListResponse)
def list_messages(
    room_id: int,
    cursor: int | None = None,
    size: int = 30,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    room = require_chat_room(db, room_id)
    if current_user.id not in {room.buyer_id, room.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if size < 1 or size > 100:
        raise HTTPException(status_code=422, detail="INVALID_SIZE_VALUE")
    stmt = select(Message).where(Message.chat_room_id == room_id)
    if cursor:
        stmt = stmt.where(Message.id < cursor)
    messages = db.scalars(stmt.order_by(Message.id.desc()).limit(size + 1)).all()
    has_next = len(messages) > size
    sliced = messages[:size]
    next_cursor = sliced[-1].id if has_next and sliced else None
    return {
        "messages": [
            MessageEntry(
                id=message.id,
                chat_room_id=message.chat_room_id,
                sender_id=message.sender_id,
                content=message.content,
                message_type=message.message_type,
                is_read=message.is_read,
                created_at=message.created_at,
            )
            for message in reversed(sliced)
        ],
        "next_cursor": next_cursor,
        "has_next": has_next,
    }


@router.post("/{room_id}/messages", response_model=MessageEntry, status_code=status.HTTP_201_CREATED)
def create_message(
    room_id: int,
    payload: MessageCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    room = require_chat_room(db, room_id)
    if current_user.id not in {room.buyer_id, room.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if payload.message_type != MessageType.TEXT:
        raise HTTPException(status_code=422, detail="INVALID_MESSAGE_TYPE")
    if check_block_relation(db, room.buyer_id, room.seller_id):
        raise HTTPException(status_code=403, detail="USER_BLOCKED")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="EMPTY_MESSAGE")
    message = Message(chat_room_id=room.id, sender_id=current_user.id, content=content)
    room.last_message_at = datetime.utcnow()
    db.add_all([message, room])
    db.commit()
    db.refresh(message)
    return message


@router.patch("/{room_id}/read", response_model=ReadResponse)
def read_messages(
    room_id: int,
    payload: ReadRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    room = require_chat_room(db, room_id)
    if current_user.id not in {room.buyer_id, room.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    stmt = select(Message).where(Message.chat_room_id == room.id, Message.sender_id != current_user.id, Message.is_read.is_(False))
    if payload.last_read_message_id:
        stmt = stmt.where(Message.id <= payload.last_read_message_id)
    messages = db.scalars(stmt).all()
    for message in messages:
        message.is_read = True
        db.add(message)
    db.commit()
    return ReadResponse(room_id=room.id, read_count=len(messages))


@router.delete("/{room_id}", response_model=ChatRoomDeleteResponse)
def delete_chat_room(room_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    room = require_chat_room(db, room_id)
    if current_user.id not in {room.buyer_id, room.seller_id}:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    deleted_message_count = db.scalar(select(func.count(Message.id)).where(Message.chat_room_id == room.id)) or 0
    db.execute(delete(Message).where(Message.chat_room_id == room.id))
    db.execute(delete(ChatRoom).where(ChatRoom.id == room.id))
    db.commit()
    return ChatRoomDeleteResponse(id=room.id, deleted_message_count=deleted_message_count)
