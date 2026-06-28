import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.category import CategoryGroup


class MonthlyPlan(Base):
    __tablename__ = "monthly_plans"
    __table_args__ = (UniqueConstraint("user_id", "year", "month", name="uq_user_month"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    salary_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="ZAR", server_default="ZAR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="monthly_plans")
    allocations: Mapped[list["Allocation"]] = relationship(
        back_populates="monthly_plan", cascade="all, delete-orphan"
    )

    @property
    def allocated_total(self) -> Decimal:
        return sum((a.allocated_amount for a in self.allocations), Decimal("0"))

    @property
    def remaining_amount(self) -> Decimal:
        return self.salary_amount - self.allocated_total

    @property
    def savings_total(self) -> Decimal:
        return sum(
            (a.allocated_amount for a in self.allocations if a.category.group == CategoryGroup.WEALTH),
            Decimal("0"),
        )

    @property
    def on_track(self) -> bool:
        return self.remaining_amount >= 0
