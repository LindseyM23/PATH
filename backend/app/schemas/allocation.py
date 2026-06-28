import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.category import CategoryGroup


class AllocationItem(BaseModel):
    category_id: uuid.UUID
    allocated_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class AllocationsUpsert(BaseModel):
    allocations: list[AllocationItem]


class QuickLogRequest(BaseModel):
    category_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class AllocationOut(BaseModel):
    category_id: uuid.UUID
    category_name: str
    group: CategoryGroup
    icon: str | None
    allocated_amount: Decimal

    model_config = {"from_attributes": True}
