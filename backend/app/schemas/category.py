from datetime import datetime

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]
