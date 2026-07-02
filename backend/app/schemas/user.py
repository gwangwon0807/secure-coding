from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import UserRole, UserStatus
from app.schemas.item import ItemListEntry


class UserProfileResponse(BaseModel):
    id: int
    email: str
    nickname: str
    profile_image_url: str | None
    bio: str | None
    role: UserRole
    status: UserStatus
    trust_score: int
    trade_count: int
    report_count: int
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=20)
    profile_image_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=300)


class UpdateProfileResponse(BaseModel):
    id: int
    nickname: str
    profile_image_url: str | None
    bio: str | None
    updated_at: datetime


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=100)
    new_password: str = Field(min_length=8, max_length=100)


class ChangePasswordResponse(BaseModel):
    id: int
    updated_at: datetime


class WithdrawResponse(BaseModel):
    id: int
    status: UserStatus
    deleted_at: datetime


class PublicProfileResponse(BaseModel):
    id: int
    nickname: str
    profile_image_url: str | None
    bio: str | None
    trust_score: int
    trade_count: int
    created_at: datetime


class MyItemListResponse(BaseModel):
    items: list[ItemListEntry]
