"""Configure env and DB before importing the application (import side effects use settings)."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
_tmp.close()
TEST_DB_FILE = Path(_tmp.name)

os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_only_must_be_long_enough"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE.as_posix()}"

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    try:
        TEST_DB_FILE.unlink(missing_ok=True)
    except OSError:
        pass


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/users/",
        json={"email": "owner@example.com", "password": "testpassword123"},
    )
    r = client.post(
        "/login",
        json={"email": "owner@example.com", "password": "testpassword123"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    return {"Authorization": f"Bearer {token}"}
