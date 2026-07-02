from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.endpoints.helpers import ensure_page_size, get_item_thumbnail
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.category import Category
from app.models.enums import ImageStatus, ItemStatus, TransactionStatus
from app.models.item import Item
from app.models.item_image import ItemImage
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.item import ItemCreateRequest, ItemCreateResponse, ItemDeleteResponse, ItemDetailResponse, ItemListEntry, ItemListResponse, ItemStatusUpdateRequest, ItemStatusUpdateResponse, ItemUpdateRequest, ItemUpdateResponse
from app.utils.pagination import build_pagination


router = APIRouter()


def _serialize_seller(user: User) -> dict:
    return {"id": user.id, "nickname": user.nickname, "trust_score": user.trust_score, "profile_image_url": user.profile_image_url}


@router.get("", response_model=ItemListResponse)
def list_items(
    keyword: str | None = None,
    category_id: int | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    location: str | None = None,
    status_filter: ItemStatus | None = Query(default=None, alias="status"),
    sort: str = "latest",
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="INVALID_PRICE_RANGE")
    stmt = (
        select(Item)
        .options(selectinload(Item.seller), selectinload(Item.images))
        .where(Item.deleted_at.is_(None), Item.status != ItemStatus.HIDDEN)
    )
    if status_filter is not None:
        stmt = stmt.where(Item.status == status_filter)
    if keyword:
        stmt = stmt.where(or_(Item.title.ilike(f"%{keyword}%"), Item.description.ilike(f"%{keyword}%")))
    if category_id:
        stmt = stmt.where(Item.category_id == category_id)
    if min_price is not None:
        stmt = stmt.where(Item.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Item.price <= max_price)
    if location:
        stmt = stmt.where(Item.location.ilike(f"%{location}%"))

    sort_map = {"latest": desc(Item.created_at), "price_asc": asc(Item.price), "price_desc": desc(Item.price)}
    if sort not in sort_map:
        raise HTTPException(status_code=422, detail="INVALID_SORT_VALUE")
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(sort_map[sort]).offset((page - 1) * size).limit(size)).all()
    payload = [
        ItemListEntry(
            id=item.id,
            title=item.title,
            price=item.price,
            location=item.location,
            status=item.status,
            thumbnail_url=get_item_thumbnail(item),
            seller={"id": item.seller.id, "nickname": item.seller.nickname, "trust_score": item.seller.trust_score},
            created_at=item.created_at,
        )
        for item in items
    ]
    return {"items": payload, "pagination": build_pagination(page, size, total_count)}


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item_detail(item_id: int, db: Session = Depends(get_db)):
    item = db.scalar(
        select(Item)
        .options(selectinload(Item.category), selectinload(Item.seller), selectinload(Item.images))
        .where(Item.id == item_id)
    )
    if not item or item.deleted_at is not None or item.status == ItemStatus.HIDDEN:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    item.view_count += 1
    db.add(item)
    db.commit()
    db.refresh(item)
    images = [img for img in item.images if img.deleted_at is None]
    images.sort(key=lambda image: image.sort_order)
    return ItemDetailResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        price=item.price,
        category={"id": item.category.id, "name": item.category.name},
        location=item.location,
        status=item.status,
        images=[{"id": img.id, "image_url": img.image_url, "sort_order": img.sort_order} for img in images],
        seller=_serialize_seller(item.seller),
        view_count=item.view_count,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=ItemCreateResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    category = db.get(Category, payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")
    images = db.scalars(select(ItemImage).where(ItemImage.id.in_(payload.image_ids), ItemImage.deleted_at.is_(None))).all()
    if len(images) != len(payload.image_ids):
        raise HTTPException(status_code=404, detail="IMAGE_NOT_FOUND")
    if any(image.uploader_id != current_user.id for image in images):
        raise HTTPException(status_code=403, detail="IMAGE_OWNER_MISMATCH")
    item = Item(
        seller_id=current_user.id,
        category_id=payload.category_id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        location=payload.location,
    )
    db.add(item)
    db.flush()
    for order, image_id in enumerate(payload.image_ids, start=1):
        image = next(img for img in images if img.id == image_id)
        image.item_id = item.id
        image.sort_order = order
        image.status = ImageStatus.ATTACHED
        db.add(image)
    db.commit()
    db.refresh(item)
    return ItemCreateResponse(id=item.id, seller_id=item.seller_id, title=item.title, price=item.price, status=item.status, created_at=item.created_at)


@router.patch("/{item_id}", response_model=ItemUpdateResponse)
def update_item(
    item_id: int,
    payload: ItemUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(Item).options(selectinload(Item.images)).where(Item.id == item_id))
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if item.status == ItemStatus.SOLD:
        raise HTTPException(status_code=409, detail="CANNOT_EDIT_SOLD_ITEM")
    if item.status == ItemStatus.HIDDEN:
        raise HTTPException(status_code=409, detail="CANNOT_EDIT_HIDDEN_ITEM")
    for field in ("title", "description", "price", "location"):
        value = getattr(payload, field)
        if value is not None:
            setattr(item, field, value)
    if payload.category_id is not None:
        category = db.get(Category, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")
        item.category_id = payload.category_id
    if payload.image_ids is not None:
        images = db.scalars(select(ItemImage).where(ItemImage.id.in_(payload.image_ids), ItemImage.deleted_at.is_(None))).all()
        if len(images) != len(payload.image_ids):
            raise HTTPException(status_code=404, detail="IMAGE_NOT_FOUND")
        if any(image.uploader_id != current_user.id for image in images):
            raise HTTPException(status_code=403, detail="IMAGE_OWNER_MISMATCH")
        for existing in item.images:
            if existing.deleted_at is None:
                existing.item_id = None
                existing.status = ImageStatus.TEMP
                db.add(existing)
        for order, image_id in enumerate(payload.image_ids, start=1):
            image = next(img for img in images if img.id == image_id)
            image.item_id = item.id
            image.sort_order = order
            image.status = ImageStatus.ATTACHED
            db.add(image)
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemUpdateResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        price=item.price,
        category_id=item.category_id,
        location=item.location,
        updated_at=item.updated_at,
    )


@router.delete("/{item_id}", response_model=ItemDeleteResponse)
def delete_item(item_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    active_transaction = db.scalar(
        select(Transaction).where(
            Transaction.item_id == item.id,
            Transaction.status.in_([TransactionStatus.REQUESTED, TransactionStatus.ACCEPTED]),
        )
    )
    if active_transaction:
        raise HTTPException(status_code=409, detail="ACTIVE_TRANSACTION_EXISTS")
    item.deleted_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return ItemDeleteResponse(id=item.id, deleted_at=item.deleted_at)


@router.patch("/{item_id}/status", response_model=ItemStatusUpdateResponse)
def update_item_status(
    item_id: int,
    payload: ItemStatusUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    item = db.get(Item, item_id)
    if not item or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")
    if item.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if payload.status == ItemStatus.SOLD:
        raise HTTPException(status_code=409, detail="CANNOT_SET_SOLD_DIRECTLY")
    item.status = payload.status
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemStatusUpdateResponse(id=item.id, status=item.status, updated_at=item.updated_at)
