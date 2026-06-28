from decimal import Decimal

from pydantic import BaseModel


class ReflectionOut(BaseModel):
    year: int
    month: int
    salary_amount: Decimal
    allocated_total: Decimal
    remaining_amount: Decimal
    messages: list[str]
