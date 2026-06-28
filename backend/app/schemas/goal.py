import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    icon: str | None = None


class ContributeRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class GoalOut(BaseModel):
    id: uuid.UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    icon: str | None
    progress_percent: Decimal

    model_config = {"from_attributes": True}
