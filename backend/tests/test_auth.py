def test_register_creates_user_and_seeds_categories(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123", "display_name": "New"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert body["access_token"]

    categories = client.get(
        "/api/v1/categories", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert categories.status_code == 200
    assert len(categories.json()) == 21


def test_register_duplicate_email_fails(client):
    payload = {"email": "dupe@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register", json={"email": "login@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register", json={"email": "wrong@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "wrong@example.com", "password": "incorrect"}
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)
