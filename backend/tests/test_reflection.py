from decimal import Decimal

from app.models.allocation import Allocation
from app.models.category import Category, CategoryGroup
from app.models.monthly_plan import MonthlyPlan
from app.models.user import User
from app.routers.plans import _previous_year_month


def _register(client, db_session, email):
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    token = response.json()["access_token"]
    user = db_session.query(User).filter(User.email == email).first()
    return user, {"Authorization": f"Bearer {token}"}


def _make_previous_plan(db_session, user, salary):
    year, month = _previous_year_month()
    plan = MonthlyPlan(user_id=user.id, year=year, month=month, salary_amount=salary)
    db_session.add(plan)
    db_session.commit()
    return plan


def test_no_previous_plan_404(client, auth_headers):
    response = client.get("/api/v1/plans/previous/reflection", headers=auth_headers)
    assert response.status_code == 404


def test_fully_funded_essentials_message_appears(client, db_session):
    user, headers = _register(client, db_session, "reflection1@example.com")
    plan = _make_previous_plan(db_session, user, Decimal("10000.00"))

    essentials = (
        db_session.query(Category)
        .filter(Category.user_id == user.id, Category.group == CategoryGroup.ESSENTIALS)
        .all()
    )
    for category in essentials:
        db_session.add(
            Allocation(monthly_plan_id=plan.id, category_id=category.id, allocated_amount=Decimal("100.00"))
        )
    db_session.commit()

    response = client.get("/api/v1/plans/previous/reflection", headers=headers)
    assert response.status_code == 200
    assert "You funded all your essentials this month." in response.json()["messages"]


def test_partially_funded_essentials_message_absent(client, db_session):
    user, headers = _register(client, db_session, "reflection2@example.com")
    plan = _make_previous_plan(db_session, user, Decimal("10000.00"))

    essentials = (
        db_session.query(Category)
        .filter(Category.user_id == user.id, Category.group == CategoryGroup.ESSENTIALS)
        .all()
    )
    # Fund all but one essentials category.
    for category in essentials[:-1]:
        db_session.add(
            Allocation(monthly_plan_id=plan.id, category_id=category.id, allocated_amount=Decimal("100.00"))
        )
    db_session.commit()

    response = client.get("/api/v1/plans/previous/reflection", headers=headers)
    assert response.status_code == 200
    assert "You funded all your essentials this month." not in response.json()["messages"]


def test_savings_message_reflects_wealth_total(client, db_session):
    user, headers = _register(client, db_session, "reflection3@example.com")
    plan = _make_previous_plan(db_session, user, Decimal("10000.00"))

    wealth_categories = (
        db_session.query(Category)
        .filter(Category.user_id == user.id, Category.group == CategoryGroup.WEALTH)
        .all()
    )
    db_session.add(
        Allocation(
            monthly_plan_id=plan.id,
            category_id=wealth_categories[0].id,
            allocated_amount=Decimal("3000.00"),
        )
    )
    db_session.commit()

    response = client.get("/api/v1/plans/previous/reflection", headers=headers)
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert any("R3,000" in m and "savings" in m for m in messages)


def test_remaining_amount_message_variants(client, db_session):
    # Fully allocated -> remaining == 0
    user, headers = _register(client, db_session, "reflection4@example.com")
    plan = _make_previous_plan(db_session, user, Decimal("1000.00"))
    category = db_session.query(Category).filter(Category.user_id == user.id).first()
    db_session.add(
        Allocation(monthly_plan_id=plan.id, category_id=category.id, allocated_amount=Decimal("1000.00"))
    )
    db_session.commit()
    messages = client.get("/api/v1/plans/previous/reflection", headers=headers).json()["messages"]
    assert "You allocated every rand of your salary this month." in messages

    # Left over -> remaining > 0
    user2, headers2 = _register(client, db_session, "reflection5@example.com")
    _make_previous_plan(db_session, user2, Decimal("1000.00"))
    messages2 = client.get("/api/v1/plans/previous/reflection", headers=headers2).json()["messages"]
    assert any("left over" in m for m in messages2)

    # Over-allocated -> remaining < 0
    user3, headers3 = _register(client, db_session, "reflection6@example.com")
    plan3 = _make_previous_plan(db_session, user3, Decimal("1000.00"))
    category3 = db_session.query(Category).filter(Category.user_id == user3.id).first()
    db_session.add(
        Allocation(monthly_plan_id=plan3.id, category_id=category3.id, allocated_amount=Decimal("1500.00"))
    )
    db_session.commit()
    messages3 = client.get("/api/v1/plans/previous/reflection", headers=headers3).json()["messages"]
    assert "You allocated a little more than you earned this month. Let's adjust next month's plan." in messages3


def test_reflection_requires_auth(client):
    response = client.get("/api/v1/plans/previous/reflection")
    assert response.status_code in (401, 403)
