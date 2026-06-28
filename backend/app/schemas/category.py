import uuid

from pydantic import BaseModel

from app.models.category import CategoryGroup


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    group: CategoryGroup
    icon: str | None
    is_default: bool
    sort_order: int

    model_config = {"from_attributes": True}
