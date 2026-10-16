import math
from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Query

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    total: int
    page: int
    limit: int
    total_pages: int
    items: List[T]


def paginate(query: Query, page: int = 1, limit: int = 10) -> dict:
    total = query.count()
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": items
    }
    
