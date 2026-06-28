from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.allocation import Allocation
from app.models.category import Category, CategoryGroup
from app.models.monthly_plan import MonthlyPlan
from app.models.user import User
from app.schemas.allocation import AllocationOut, AllocationsUpsert, QuickLogRequest
from app.schemas.monthly_plan import MonthlyPlanOut, MonthlyPlanUpsert
from app.schemas.reflection import ReflectionOut

router = APIRouter(prefix="/plans", tags=["plans"])


def _current_year_month() -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    return now.year, now.month


def _previous_year_month() -> tuple[int, int]:
    year, month = _current_year_month()
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _get_current_plan(db: Session, user_id) -> MonthlyPlan | None:
    year, month = _current_year_month()
    return (
        db.query(MonthlyPlan)
        .filter(MonthlyPlan.user_id == user_id, MonthlyPlan.year == year, MonthlyPlan.month == month)
        .first()
    )


@router.get("/current", response_model=MonthlyPlanOut)
def get_current_plan(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MonthlyPlan:
    plan = _get_current_plan(db, current_user.id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No plan for the current month yet")
    return plan


@router.put("/current", response_model=MonthlyPlanOut)
def upsert_current_plan(
    payload: MonthlyPlanUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MonthlyPlan:
    plan = _get_current_plan(db, current_user.id)
    if plan is None:
        year, month = _current_year_month()
        plan = MonthlyPlan(
            user_id=current_user.id,
            year=year,
            month=month,
            salary_amount=payload.salary_amount,
        )
        db.add(plan)
    else:
        plan.salary_amount = payload.salary_amount

    db.commit()
    db.refresh(plan)
    return plan


def _require_current_plan(db: Session, user_id) -> MonthlyPlan:
    plan = _get_current_plan(db, user_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No plan for the current month yet")
    return plan


def _allocation_rows(db: Session, plan: MonthlyPlan) -> list[Allocation]:
    """Every active category for the plan's user, each paired with its allocation
    (creating an unsaved zero-amount one in-memory if none exists yet) — gives the
    frontend a single call that already has every row it needs to render, pre-filled.
    """
    categories = (
        db.query(Category)
        .filter(Category.user_id == plan.user_id, Category.is_archived.is_(False))
        .order_by(Category.sort_order)
        .all()
    )
    existing_by_category = {a.category_id: a for a in plan.allocations}

    rows = []
    for category in categories:
        allocation = existing_by_category.get(category.id)
        if allocation is None:
            allocation = Allocation(category_id=category.id, allocated_amount=Decimal("0.00"))
        allocation.category_name = category.name  # type: ignore[attr-defined]
        allocation.group = category.group  # type: ignore[attr-defined]
        allocation.icon = category.icon  # type: ignore[attr-defined]
        rows.append(allocation)
    return rows


@router.get("/current/allocations", response_model=list[AllocationOut])
def get_current_allocations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Allocation]:
    plan = _require_current_plan(db, current_user.id)
    return _allocation_rows(db, plan)


@router.put("/current/allocations", response_model=list[AllocationOut])
def upsert_current_allocations(
    payload: AllocationsUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Allocation]:
    plan = _require_current_plan(db, current_user.id)
    existing_by_category = {a.category_id: a for a in plan.allocations}

    for item in payload.allocations:
        allocation = existing_by_category.get(item.category_id)
        if allocation is None:
            db.add(
                Allocation(
                    monthly_plan_id=plan.id,
                    category_id=item.category_id,
                    allocated_amount=item.allocated_amount,
                )
            )
        else:
            allocation.allocated_amount = item.allocated_amount

    db.commit()
    db.refresh(plan)
    return _allocation_rows(db, plan)


@router.post("/current/allocations/quick-log", response_model=AllocationOut)
def quick_log_allocation(
    payload: QuickLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Allocation:
    plan = _require_current_plan(db, current_user.id)

    category = (
        db.query(Category)
        .filter(Category.id == payload.category_id, Category.user_id == current_user.id)
        .first()
    )
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")

    allocation = (
        db.query(Allocation)
        .filter(Allocation.monthly_plan_id == plan.id, Allocation.category_id == category.id)
        .first()
    )
    if allocation is None:
        allocation = Allocation(
            monthly_plan_id=plan.id, category_id=category.id, allocated_amount=payload.amount
        )
        db.add(allocation)
    else:
        allocation.allocated_amount += payload.amount

    db.commit()
    db.refresh(allocation)

    allocation.category_name = category.name  # type: ignore[attr-defined]
    allocation.group = category.group  # type: ignore[attr-defined]
    allocation.icon = category.icon  # type: ignore[attr-defined]
    return allocation


def _get_previous_plan(db: Session, user_id) -> MonthlyPlan | None:
    year, month = _previous_year_month()
    return (
        db.query(MonthlyPlan)
        .filter(MonthlyPlan.user_id == user_id, MonthlyPlan.year == year, MonthlyPlan.month == month)
        .first()
    )


def _build_reflection_messages(plan: MonthlyPlan, allocation_rows: list[Allocation]) -> list[str]:
    messages = []

    essentials = [r for r in allocation_rows if r.group == CategoryGroup.ESSENTIALS]  # type: ignore[attr-defined]
    if essentials and all(r.allocated_amount > 0 for r in essentials):
        messages.append("You funded all your essentials this month.")

    wealth_total = sum(
        (r.allocated_amount for r in allocation_rows if r.group == CategoryGroup.WEALTH),  # type: ignore[attr-defined]
        Decimal("0"),
    )
    if wealth_total > 0:
        messages.append(f"You put R{wealth_total:,.0f} toward your savings and wealth goals this month.")

    if plan.remaining_amount < 0:
        messages.append(
            "You allocated a little more than you earned this month. Let's adjust next month's plan."
        )
    elif plan.remaining_amount == 0:
        messages.append("You allocated every rand of your salary this month.")
    else:
        messages.append(
            f"You had R{plan.remaining_amount:,.0f} left over — consider giving it a job next month."
        )

    return messages


@router.get("/previous/reflection", response_model=ReflectionOut)
def get_previous_reflection(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ReflectionOut:
    plan = _get_previous_plan(db, current_user.id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No plan for last month yet")

    rows = _allocation_rows(db, plan)
    messages = _build_reflection_messages(plan, rows)

    return ReflectionOut(
        year=plan.year,
        month=plan.month,
        salary_amount=plan.salary_amount,
        allocated_total=plan.allocated_total,
        remaining_amount=plan.remaining_amount,
        messages=messages,
    )
