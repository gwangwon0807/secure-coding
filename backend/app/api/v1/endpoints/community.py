from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.helpers import ensure_page_size
from app.core.deps import require_active_user
from app.db.session import get_db
from app.models.community import CommunityComment, CommunityPost, CommunityPostImage
from app.models.user import User
from app.schemas.community import CommunityCommentCreateRequest, CommunityCommentEntry, CommunityCommentStateResponse, CommunityCommentUpdateRequest, CommunityPostCreateRequest, CommunityPostDetailResponse, CommunityPostListEntry, CommunityPostListResponse, CommunityPostStateResponse, CommunityPostUpdateRequest
from app.utils.pagination import build_pagination


router = APIRouter()


def _author_summary(user: User) -> dict:
    return {"id": user.id, "nickname": user.nickname}


def _image_summary(image: CommunityPostImage) -> dict:
    return {"id": image.id, "image_url": image.image_url, "sort_order": image.sort_order}


def _load_post_images(db: Session, post_id: int) -> list[CommunityPostImage]:
    return db.scalars(
        select(CommunityPostImage)
        .where(CommunityPostImage.post_id == post_id, CommunityPostImage.deleted_at.is_(None))
        .order_by(CommunityPostImage.sort_order.asc(), CommunityPostImage.id.asc())
    ).all()


def _attach_images(db: Session, post: CommunityPost, current_user: User, image_ids: list[int]) -> list[CommunityPostImage]:
    if not image_ids:
        existing_images = _load_post_images(db, post.id)
        for image in existing_images:
            image.post_id = None
            db.add(image)
        return []

    images = db.scalars(
        select(CommunityPostImage).where(CommunityPostImage.id.in_(image_ids), CommunityPostImage.deleted_at.is_(None))
    ).all()
    if len(images) != len(set(image_ids)):
        raise HTTPException(status_code=422, detail="INVALID_IMAGE_IDS")
    if any(image.uploader_id != current_user.id for image in images):
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    existing_images = _load_post_images(db, post.id)
    incoming_ids = set(image_ids)
    for image in existing_images:
        if image.id not in incoming_ids:
            image.post_id = None
            db.add(image)

    image_map = {image.id: image for image in images}
    ordered_images = []
    for index, image_id in enumerate(image_ids, start=1):
        image = image_map[image_id]
        image.post_id = post.id
        image.sort_order = index
        db.add(image)
        ordered_images.append(image)
    return ordered_images


def _require_post(db: Session, post_id: int) -> CommunityPost:
    post = db.get(CommunityPost, post_id)
    if not post or post.deleted_at is not None:
        raise HTTPException(status_code=404, detail="POST_NOT_FOUND")
    return post


def _require_comment(db: Session, comment_id: int) -> CommunityComment:
    comment = db.get(CommunityComment, comment_id)
    if not comment or comment.deleted_at is not None:
        raise HTTPException(status_code=404, detail="COMMENT_NOT_FOUND")
    return comment


@router.get("/posts", response_model=CommunityPostListResponse)
def list_posts(
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    ensure_page_size(page, size)
    stmt = select(CommunityPost).where(CommunityPost.deleted_at.is_(None))
    if keyword:
      stmt = stmt.where((CommunityPost.title.ilike(f"%{keyword}%")) | (CommunityPost.content.ilike(f"%{keyword}%")))
    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    posts = db.scalars(stmt.order_by(CommunityPost.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    payload = []
    for post in posts:
        author = db.get(User, post.author_id)
        images = _load_post_images(db, post.id)
        comment_count = db.scalar(
            select(func.count()).where(CommunityComment.post_id == post.id, CommunityComment.deleted_at.is_(None))
        ) or 0
        payload.append(
            CommunityPostListEntry(
                id=post.id,
                title=post.title,
                author=_author_summary(author),
                comment_count=comment_count,
                thumbnail_url=images[0].image_url if images else None,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
        )
    return {"posts": payload, "pagination": build_pagination(page, size, total_count)}


@router.post("/posts", response_model=CommunityPostStateResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: CommunityPostCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    post = CommunityPost(author_id=current_user.id, title=payload.title, content=payload.content)
    db.add(post)
    db.flush()
    _attach_images(db, post, current_user, payload.image_ids)
    db.commit()
    db.refresh(post)
    return CommunityPostStateResponse(id=post.id, created_at=post.created_at)


@router.get("/posts/{post_id}", response_model=CommunityPostDetailResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = _require_post(db, post_id)
    author = db.get(User, post.author_id)
    images = _load_post_images(db, post.id)
    comments = db.scalars(
        select(CommunityComment).where(CommunityComment.post_id == post.id, CommunityComment.deleted_at.is_(None)).order_by(CommunityComment.created_at.asc())
    ).all()
    comment_entries = []
    for comment in comments:
        comment_author = db.get(User, comment.author_id)
        comment_entries.append(
            CommunityCommentEntry(
                id=comment.id,
                author=_author_summary(comment_author),
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
        )
    return CommunityPostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author=_author_summary(author),
        images=[_image_summary(image) for image in images],
        comments=comment_entries,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.patch("/posts/{post_id}", response_model=CommunityPostStateResponse)
def update_post(
    post_id: int,
    payload: CommunityPostUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    post = _require_post(db, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.image_ids is not None:
        _attach_images(db, post, current_user, payload.image_ids)
    db.add(post)
    db.commit()
    db.refresh(post)
    return CommunityPostStateResponse(id=post.id, updated_at=post.updated_at)


@router.delete("/posts/{post_id}", response_model=CommunityPostStateResponse)
def delete_post(post_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    post = _require_post(db, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    post.deleted_at = datetime.utcnow()
    db.add(post)
    db.commit()
    return CommunityPostStateResponse(id=post.id, deleted_at=post.deleted_at)


@router.post("/posts/{post_id}/comments", response_model=CommunityCommentStateResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    payload: CommunityCommentCreateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    _require_post(db, post_id)
    comment = CommunityComment(post_id=post_id, author_id=current_user.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommunityCommentStateResponse(id=comment.id, created_at=comment.created_at)


@router.patch("/comments/{comment_id}", response_model=CommunityCommentStateResponse)
def update_comment(
    comment_id: int,
    payload: CommunityCommentUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    comment = _require_comment(db, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    comment.content = payload.content
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommunityCommentStateResponse(id=comment.id, updated_at=comment.updated_at)


@router.delete("/comments/{comment_id}", response_model=CommunityCommentStateResponse)
def delete_comment(comment_id: int, current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    comment = _require_comment(db, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    comment.deleted_at = datetime.utcnow()
    db.add(comment)
    db.commit()
    return CommunityCommentStateResponse(id=comment.id, deleted_at=comment.deleted_at)
