def test_get_allocations_404_when_no_plan(client, auth_headers):
    response = client.get("/api/v1/plans/current/allocations", headers=auth_headers)
    assert response.status_code == 404


def test_get_allocations_returns_all_categories_at_zero(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers)

    response = client.get("/api/v1/plans/current/allocations", headers=auth_headers)
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 21
    assert all(row["allocated_amount"] == "0.00" for row in rows)


def test_upsert_allocations_creates_then_updates(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers)
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    rent_id = next(c["id"] for c in categories if c["name"] == "Rent")
    groceries_id = next(c["id"] for c in categories if c["name"] == "Groceries")

    first = client.put(
        "/api/v1/plans/current/allocations",
        json={"allocations": [{"category_id": rent_id, "allocated_amount": "6300.00"}]},
        headers=auth_headers,
    )
    assert first.status_code == 200
    rent_row = next(r for r in first.json() if r["category_id"] == rent_id)
    assert rent_row["allocated_amount"] == "6300.00"

    second = client.put(
        "/api/v1/plans/current/allocations",
        json={
            "allocations": [
                {"category_id": rent_id, "allocated_amount": "6500.00"},
                {"category_id": groceries_id, "allocated_amount": "1500.00"},
            ]
        },
        headers=auth_headers,
    )
    assert second.status_code == 200
    rows_by_id = {r["category_id"]: r for r in second.json()}
    assert rows_by_id[rent_id]["allocated_amount"] == "6500.00"  # updated, not duplicated
    assert rows_by_id[groceries_id]["allocated_amount"] == "1500.00"
    assert len(second.json()) == 21  # still one row per category, no duplicates


def test_plan_reflects_allocated_total_and_remaining(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers)
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    rent_id = next(c["id"] for c in categories if c["name"] == "Rent")

    client.put(
        "/api/v1/plans/current/allocations",
        json={"allocations": [{"category_id": rent_id, "allocated_amount": "6300.00"}]},
        headers=auth_headers,
    )

    plan = client.get("/api/v1/plans/current", headers=auth_headers).json()
    assert plan["allocated_total"] == "6300.00"
    assert plan["remaining_amount"] == "11400.00"


def test_allocations_require_auth(client):
    response = client.get("/api/v1/plans/current/allocations")
    assert response.status_code in (401, 403)


def test_quick_log_404_when_no_plan(client, auth_headers):
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    transport_id = next(c["id"] for c in categories if c["name"] == "Transport")

    response = client.post(
        "/api/v1/plans/current/allocations/quick-log",
        json={"category_id": transport_id, "amount": "500.00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_quick_log_creates_then_accumulates(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers)
    categories = client.get("/api/v1/categories", headers=auth_headers).json()
    transport_id = next(c["id"] for c in categories if c["name"] == "Transport")

    first = client.post(
        "/api/v1/plans/current/allocations/quick-log",
        json={"category_id": transport_id, "amount": "500.00"},
        headers=auth_headers,
    )
    assert first.status_code == 200
    assert first.json()["allocated_amount"] == "500.00"

    second = client.post(
        "/api/v1/plans/current/allocations/quick-log",
        json={"category_id": transport_id, "amount": "300.00"},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["allocated_amount"] == "800.00"  # accumulated, not replaced

    plan = client.get("/api/v1/plans/current", headers=auth_headers).json()
    assert plan["allocated_total"] == "800.00"


def test_quick_log_rejects_another_users_category(client, auth_headers):
    client.put("/api/v1/plans/current", json={"salary_amount": "17700.00"}, headers=auth_headers)

    other_user = client.post(
        "/api/v1/auth/register", json={"email": "other@example.com", "password": "password123"}
    ).json()
    other_categories = client.get(
        "/api/v1/categories",
        headers={"Authorization": f"Bearer {other_user['access_token']}"},
    ).json()
    other_transport_id = next(c["id"] for c in other_categories if c["name"] == "Transport")

    response = client.post(
        "/api/v1/plans/current/allocations/quick-log",
        json={"category_id": other_transport_id, "amount": "500.00"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_quick_log_requires_auth(client):
    response = client.post(
        "/api/v1/plans/current/allocations/quick-log",
        json={"category_id": "00000000-0000-0000-0000-000000000000", "amount": "500.00"},
    )
    assert response.status_code in (401, 403)
