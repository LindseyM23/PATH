import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Allocation(Base):
    __tablename__ = "allocations"
    __table_args__ = (UniqueConstraint("monthly_plan_id", "category_id", name="uq_plan_category"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    monthly_plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monthly_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    monthly_plan: Mapped["MonthlyPlan"] = relationship(back_populates="allocations")
    category: Mapped["Category"] = relationship(back_populates="allocations")
