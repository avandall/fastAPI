from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    client.post(
        "/users/",
        json={"email": "auth@example.com", "password": "mypassword123"},
    )
    r = client.post(
        "/login",
        json={"email": "auth@example.com", "password": "mypassword123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert "token" in data and data["token"]


def test_login_wrong_password(client: TestClient) -> None:
    client.post(
        "/users/",
        json={"email": "u@example.com", "password": "right"},
    )
    r = client.post(
        "/login",
        json={"email": "u@example.com", "password": "wrong"},
    )
    assert r.status_code == 404


def test_login_unknown_user(client: TestClient) -> None:
    r = client.post(
        "/login",
        json={"email": "nobody@example.com", "password": "x"},
    )
    assert r.status_code == 404


def test_login2_form(client: TestClient) -> None:
    client.post(
        "/users/",
        json={"email": "form@example.com", "password": "formpass123"},
    )
    r = client.post(
        "/login2",
        data={"username": "form@example.com", "password": "formpass123"},
    )
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
