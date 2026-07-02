from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.enums import ImageStatus, ItemStatus
from app.models.item import Item
from app.models.item_image import ItemImage
from app.models.user import User
from app.schemas.image import DeleteImageResponse, ImageListResponse
from app.utils.common import save_upload_file


router = APIRouter()
settings = get_settings()
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("/items", response_model=ImageListResponse, status_code=status.HTTP_201_CREATED)
def upload_item_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=422, detail="IMAGE_REQUIRED")
    if len(files) > 10:
        raise HTTPException(status_code=422, detail="TOO_MANY_IMAGES")
    images = []
    for index, file in enumerate(files, start=1):
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(status_code=415, detail="INVALID_IMAGE_EXTENSION")
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail="INVALID_IMAGE_MIME_TYPE")
        storage_key, image_url = save_upload_file(file)
        image = ItemImage(
            uploader_id=current_user.id,
            image_url=image_url,
            storage_key=storage_key,
            sort_order=index,
            status=ImageStatus.TEMP,
        )
        db.add(image)
        images.append(image)
    db.commit()
    for image in images:
        db.refresh(image)
    return {"images": images}


@router.delete("/{image_id}", response_model=DeleteImageResponse)
def delete_image(
    image_id: int,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    image = db.get(ItemImage, image_id)
    if not image or image.deleted_at is not None:
        raise HTTPException(status_code=404, detail="IMAGE_NOT_FOUND")
    if image.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if image.item_id:
        item = db.get(Item, image.item_id)
        attached_count = db.query(ItemImage).filter(ItemImage.item_id == item.id, ItemImage.deleted_at.is_(None)).count()
        if attached_count <= 1:
            raise HTTPException(status_code=409, detail="CANNOT_DELETE_LAST_IMAGE")
        if item.status in {ItemStatus.SOLD, ItemStatus.HIDDEN}:
            raise HTTPException(status_code=409, detail="IMAGE_ATTACHED_TO_LOCKED_ITEM")
    image.deleted_at = datetime.utcnow()
    image.status = ImageStatus.DELETED
    file_path = Path(settings.upload_dir) / image.storage_key
    if file_path.exists():
        file_path.unlink()
    db.add(image)
    db.commit()
    return DeleteImageResponse(id=image.id, deleted_at=image.deleted_at)
