from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}


def test_list_posts_empty(client: TestClient) -> None:
    r = client.get("/sqlalchemy")
    assert r.status_code == 200
    assert r.json() == []


def test_create_post_requires_auth(client: TestClient) -> None:
    r = client.post(
        "/sqlalchemy",
        json={"title": "T", "content": "C", "published": True},
    )
    assert r.status_code == 401


def test_create_get_post(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {"title": "Hello", "content": "Body", "published": True}
    r = client.post("/sqlalchemy", json=payload, headers=auth_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["published"] is True
    assert "id" in data
    assert data["owner"]["email"] == "owner@example.com"

    listed = client.get("/sqlalchemy")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_get_posts_by_user_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/sqlalchemy/999", headers=auth_headers)
    assert r.status_code == 404


def test_update_delete_forbidden_other_owner(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post(
        "/users/",
        json={"email": "other@example.com", "password": "otherpass123"},
    )
    other_login = client.post(
        "/login",
        json={"email": "other@example.com", "password": "otherpass123"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['token']}"}

    create = client.post(
        "/sqlalchemy",
        json={"title": "Mine", "content": "X", "published": True},
        headers=auth_headers,
    )
    post_id = create.json()["id"]

    upd = client.put(
        f"/sqlalchemy/{post_id}",
        json={"title": "Hacked", "content": "Nope", "published": False},
        headers=other_headers,
    )
    assert upd.status_code == 403

    dele = client.delete(f"/sqlalchemy/{post_id}", headers=other_headers)
    assert dele.status_code == 403


def test_update_delete_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    create = client.post(
        "/sqlalchemy",
        json={"title": "A", "content": "B", "published": True},
        headers=auth_headers,
    )
    post_id = create.json()["id"]

    r = client.put(
        f"/sqlalchemy/{post_id}",
        json={"title": "A2", "content": "B2", "published": False},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "A2"
    assert r.json()["published"] is False

    d = client.delete(f"/sqlalchemy/{post_id}", headers=auth_headers)
    assert d.status_code == 204

    listed = client.get("/sqlalchemy")
    assert listed.status_code == 200
    assert listed.json() == []
