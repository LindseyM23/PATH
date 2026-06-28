def test_get_current_plan_404_when_none_exists(client, auth_headers):
    response = client.get("/api/v1/plans/current", headers=auth_headers)
    assert response.status_code == 404


def test_upsert_plan_creates_then_updates_same_month(client, auth_headers):
    create = client.put(
        "/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers
    )
    assert create.status_code == 200
    plan_id = create.json()["id"]
    assert create.json()["salary_amount"] == "17700.00"

    update = client.put(
        "/api/v1/plans/current", json={"salary_amount": "18000.00"}, headers=auth_headers
    )
    assert update.status_code == 200
    assert update.json()["id"] == plan_id  # same row updated, not a duplicate
    assert update.json()["salary_amount"] == "18000.00"

    fetched = client.get("/api/v1/plans/current", headers=auth_headers)
    assert fetched.json()["salary_amount"] == "18000.00"


def test_plans_require_auth(client):
    response = client.get("/api/v1/plans/current")
    assert response.status_code in (401, 403)


def test_savings_total_and_on_track(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "10000.00"}, headers=auth_headers)
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    car_fund_id = next(c["id"] for c in categories if c["name"] == "Car Fund")
    rent_id = next(c["id"] for c in categories if c["name"] == "Rent")

    client.put(
        "/api/v1/plans/current/allocations",
        json={
            "allocations": [
                {"category_id": car_fund_id, "allocated_amount": "1500.00"},
                {"category_id": rent_id, "allocated_amount": "4000.00"},
            ]
        },
        headers=auth_headers,
    )

    plan = client.get("/api/v1/plans/current", headers=auth_headers).json()
    assert plan["savings_total"] == "1500.00"  # only the Wealth-group allocation
    assert plan["on_track"] is True  # remaining (4500) is non-negative

    # Over-allocate to flip on_track to False.
    client.put(
        "/api/v1/plans/current/allocations",
        json={"allocations": [{"category_id": rent_id, "allocated_amount": "9000.00"}]},
        headers=auth_headers,
    )
    plan2 = client.get("/api/v1/plans/current", headers=auth_headers).json()
    assert plan2["on_track"] is False
