from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, UserStatus


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    nickname: str = Field(min_length=2, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=100)


class UserSummary(BaseModel):
    id: int
    email: str
    nickname: str
    role: UserRole
    status: UserStatus

    class Config:
        from_attributes = True


class AuthMeResponse(UserSummary):
    profile_image_url: str | None = None
    trust_score: int
    created_at: datetime


class SignupResponse(UserSummary):
    created_at: datetime


class LoginResponse(BaseModel):
    user: UserSummary
