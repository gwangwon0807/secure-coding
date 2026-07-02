from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.helpers import ensure_page_size
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.block import Block
from app.models.user import User
from app.schemas.block import BlockCreateRequest, BlockCreateResponse, BlockDeleteResponse, BlockListEntry, BlockListResponse
from app.utils.pagination import build_pagination


router = APIRouter()


@router.post("", response_model=BlockCreateResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    payload: BlockCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    if payload.blocked_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_BLOCK_SELF")
    blocked_user = db.get(User, payload.blocked_user_id)
    if not blocked_user:
        raise HTTPException(status_code=404, detail="BLOCKED_USER_NOT_FOUND")
    existing = db.scalar(
        select(Block).where(
            Block.blocker_id == current_user.id,
            Block.blocked_user_id == payload.blocked_user_id,
            Block.deleted_at.is_(None),
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="ALREADY_BLOCKED")
    block = Block(blocker_id=current_user.id, blocked_user_id=payload.blocked_user_id)
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.get("", response_model=BlockListResponse)
def list_blocks(page: int = 1, size: int = 20, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    ensure_page_size(page, size)
    stmt = select(Block).where(Block.blocker_id == current_user.id, Block.deleted_at.is_(None))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    blocks = db.scalars(stmt.order_by(Block.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for block in blocks:
        user = db.get(User, block.blocked_user_id)
        payload.append(
            BlockListEntry(
                id=block.id,
                blocked_user={"id": user.id, "nickname": user.nickname, "profile_image_url": user.profile_image_url},
                created_at=block.created_at,
            )
        )
    return {"blocks": payload, "pagination": build_pagination(page, size, total_count)}


@router.delete("/{user_id}", response_model=BlockDeleteResponse)
def delete_block(user_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    block = db.scalar(
        select(Block).where(
            Block.blocker_id == current_user.id,
            Block.blocked_user_id == user_id,
            Block.deleted_at.is_(None),
        )
    )
    if not block:
        raise HTTPException(status_code=404, detail="BLOCK_NOT_FOUND")
    block.deleted_at = datetime.utcnow()
    db.add(block)
    db.commit()
    return BlockDeleteResponse(blocked_user_id=user_id, unblocked_at=block.deleted_at)
