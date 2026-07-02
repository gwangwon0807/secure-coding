from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ItemStatus, MessageType
from app.schemas.common import PaginationSchema


class ChatRoomCreateRequest(BaseModel):
    item_id: int


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    message_type: MessageType = MessageType.TEXT


class ReadRequest(BaseModel):
    last_read_message_id: int | None = None


class ChatRoomCreateResponse(BaseModel):
    id: int
    item_id: int
    buyer_id: int
    seller_id: int
    created_at: datetime
    is_new: bool


class ChatRoomListEntry(BaseModel):
    id: int
    item: dict
    opponent: dict
    last_message: dict | None
    unread_count: int


class ChatRoomListResponse(BaseModel):
    chat_rooms: list[ChatRoomListEntry]
    pagination: PaginationSchema


class ChatRoomDetailResponse(BaseModel):
    id: int
    item: dict
    buyer: dict
    seller: dict
    opponent: dict
    transaction: dict | None = None
    created_at: datetime
    last_message_at: datetime | None


class MessageEntry(BaseModel):
    id: int
    chat_room_id: int
    sender_id: int
    content: str
    message_type: MessageType
    is_read: bool
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessageEntry]
    next_cursor: int | None
    has_next: bool


class ReadResponse(BaseModel):
    room_id: int
    read_count: int


class ChatRoomDeleteResponse(BaseModel):
    id: int
    deleted_message_count: int
