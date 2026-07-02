from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash, verify_password
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.enums import ItemStatus, TransactionStatus, UserStatus
from app.models.item import Item
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, ChangePasswordResponse, MyItemListResponse, PublicProfileResponse, UpdateProfileRequest, UpdateProfileResponse, UserProfileResponse, WithdrawResponse
from app.api.v1.endpoints.helpers import get_item_thumbnail, get_report_count, get_trade_count


router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        profile_image_url=current_user.profile_image_url,
        bio=current_user.bio,
        role=current_user.role,
        status=current_user.status,
        trust_score=current_user.trust_score,
        trade_count=get_trade_count(db, current_user.id),
        report_count=get_report_count(db, current_user.id),
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get("/me/items", response_model=MyItemListResponse)
def get_my_items(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(Item)
        .options(selectinload(Item.seller), selectinload(Item.images))
        .where(
            Item.seller_id == current_user.id,
            Item.deleted_at.is_(None),
            Item.status != ItemStatus.HIDDEN,
        )
        .order_by(Item.created_at.desc())
    ).all()
    return {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "price": item.price,
                "location": item.location,
                "status": item.status,
                "thumbnail_url": get_item_thumbnail(item),
                "seller": {
                    "id": current_user.id,
                    "nickname": current_user.nickname,
                    "trust_score": current_user.trust_score,
                    "profile_image_url": current_user.profile_image_url,
                },
                "created_at": item.created_at,
            }
            for item in items
        ]
    }


@router.patch("/me", response_model=UpdateProfileResponse)
def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    if payload.nickname and payload.nickname != current_user.nickname:
        if db.scalar(select(User).where(User.nickname == payload.nickname)):
            raise HTTPException(status_code=409, detail="NICKNAME_ALREADY_EXISTS")
        current_user.nickname = payload.nickname
    if payload.profile_image_url is not None:
        current_user.profile_image_url = payload.profile_image_url
    if payload.bio is not None:
        current_user.bio = payload.bio
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UpdateProfileResponse(
        id=current_user.id,
        nickname=current_user.nickname,
        profile_image_url=current_user.profile_image_url,
        bio=current_user.bio,
        updated_at=current_user.updated_at,
    )


@router.patch("/me/password", response_model=ChangePasswordResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CURRENT_PASSWORD")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=422, detail="PASSWORD_SAME_AS_CURRENT")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return ChangePasswordResponse(id=current_user.id, updated_at=current_user.updated_at)


@router.delete("/me", response_model=WithdrawResponse)
def withdraw(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    active_transaction = db.scalar(
        select(Transaction).where(
            ((Transaction.buyer_id == current_user.id) | (Transaction.seller_id == current_user.id)),
            Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED]),
        )
    )
    if active_transaction:
        raise HTTPException(status_code=409, detail="ACTIVE_TRANSACTION_EXISTS")
    current_user.status = UserStatus.DELETED
    current_user.deleted_at = datetime.utcnow()
    current_user.bio = None
    current_user.profile_image_url = None
    db.add(current_user)
    db.commit()
    return WithdrawResponse(id=current_user.id, status=current_user.status, deleted_at=current_user.deleted_at)


@router.get("/{user_id}", response_model=PublicProfileResponse)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    return PublicProfileResponse(
        id=user.id,
        nickname=user.nickname,
        profile_image_url=user.profile_image_url,
        bio=user.bio,
        trust_score=user.trust_score,
        trade_count=get_trade_count(db, user.id),
        created_at=user.created_at,
    )
