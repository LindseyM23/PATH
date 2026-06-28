import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class MonthlyPlanUpsert(BaseModel):
    salary_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class MonthlyPlanOut(BaseModel):
    id: uuid.UUID
    year: int
    month: int
    salary_amount: Decimal
    currency: str
    allocated_total: Decimal
    remaining_amount: Decimal
    savings_total: Decimal
    on_track: bool

    model_config = {"from_attributes": True}
