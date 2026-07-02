from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoryListResponse


router = APIRouter()


@router.get("", response_model=CategoryListResponse)
def list_categories(is_active: bool = True, db: Session = Depends(get_db)):
    stmt = select(Category).order_by(Category.sort_order.asc(), Category.id.asc())
    if is_active:
        stmt = stmt.where(Category.is_active.is_(True))
    categories = db.scalars(stmt).all()
    return {"categories": categories}
