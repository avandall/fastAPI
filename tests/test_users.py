from fastapi.testclient import TestClient


def test_create_and_list_users(client: TestClient) -> None:
    r = client.post(
        "/users/",
        json={"email": "user@example.com", "password": "securepass123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "user@example.com"
    assert "id" in body

    listed = client.get("/users/")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "p1"}
    assert client.post("/users/", json=payload).status_code == 200
    r = client.post("/users/", json=payload)
    assert r.status_code == 400


def test_update_user(client: TestClient) -> None:
    created = client.post(
        "/users/",
        json={"email": "old@example.com", "password": "pw"},
    )
    uid = created.json()["id"]

    r = client.put(
        f"/users/{uid}",
        json={"email": "new@example.com", "password": "pw2"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "new@example.com"


def test_update_user_not_found(client: TestClient) -> None:
    r = client.put(
        "/users/99999",
        json={"email": "x@example.com", "password": "pw"},
    )
    assert r.status_code == 404


def test_delete_user(client: TestClient) -> None:
    uid = client.post(
        "/users/",
        json={"email": "gone@example.com", "password": "pw"},
    ).json()["id"]

    r = client.delete(f"/users/{uid}")
    assert r.status_code == 204

    listed = client.get("/users/")
    assert listed.json() == []
