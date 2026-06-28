def test_create_goal_returns_zero_progress(client, auth_headers):
    response = client.post(
        "/api/v1/goals",
        json={"name": "Emergency Fund", "target_amount": "10000.00", "icon": "🛟"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Emergency Fund"
    assert body["current_amount"] == "0.00"
    assert body["progress_percent"] == "0.00"


def test_list_goals_only_returns_own_goals(client, auth_headers):
    client.post(
        "/api/v1/goals", json={"name": "Car Fund", "target_amount": "5000.00"}, headers=auth_headers
    )

    other_user = client.post(
        "/api/v1/auth/register", json={"email": "other-goals@example.com", "password": "password123"}
    ).json()
    other_headers = {"Authorization": f"Bearer {other_user['access_token']}"}
    client.post(
        "/api/v1/goals", json={"name": "Vacation Fund", "target_amount": "3000.00"}, headers=other_headers
    )

    response = client.get("/api/v1/goals", headers=auth_headers)
    assert response.status_code == 200
    names = [g["name"] for g in response.json()]
    assert names == ["Car Fund"]


def test_contribute_accumulates_and_updates_progress(client, auth_headers):
    goal = client.post(
        "/api/v1/goals", json={"name": "Car Fund", "target_amount": "10000.00"}, headers=auth_headers
    ).json()

    first = client.post(
        f"/api/v1/goals/{goal['id']}/contribute", json={"amount": "2000.00"}, headers=auth_headers
    )
    assert first.status_code == 200
    assert first.json()["current_amount"] == "2000.00"
    assert first.json()["progress_percent"] == "20.00"

    second = client.post(
        f"/api/v1/goals/{goal['id']}/contribute", json={"amount": "1000.00"}, headers=auth_headers
    )
    assert second.status_code == 200
    assert second.json()["current_amount"] == "3000.00"  # accumulated, not replaced
    assert second.json()["progress_percent"] == "30.00"


def test_contribute_rejects_another_users_goal(client, auth_headers):
    other_user = client.post(
        "/api/v1/auth/register", json={"email": "other-contribute@example.com", "password": "password123"}
    ).json()
    other_headers = {"Authorization": f"Bearer {other_user['access_token']}"}
    other_goal = client.post(
        "/api/v1/goals", json={"name": "House Fund", "target_amount": "5000.00"}, headers=other_headers
    ).json()

    response = client.post(
        f"/api/v1/goals/{other_goal['id']}/contribute", json={"amount": "100.00"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_goal_removes_it(client, auth_headers):
    goal = client.post(
        "/api/v1/goals", json={"name": "Business Fund", "target_amount": "20000.00"}, headers=auth_headers
    ).json()

    delete_response = client.delete(f"/api/v1/goals/{goal['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    remaining = client.get("/api/v1/goals", headers=auth_headers).json()
    assert remaining == []


def test_delete_rejects_another_users_goal(client, auth_headers):
    other_user = client.post(
        "/api/v1/auth/register", json={"email": "other-delete@example.com", "password": "password123"}
    ).json()
    other_headers = {"Authorization": f"Bearer {other_user['access_token']}"}
    other_goal = client.post(
        "/api/v1/goals", json={"name": "Vacation Fund", "target_amount": "5000.00"}, headers=other_headers
    ).json()

    response = client.delete(f"/api/v1/goals/{other_goal['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_goals_require_auth(client):
    response = client.get("/api/v1/goals")
    assert response.status_code in (401, 403)
