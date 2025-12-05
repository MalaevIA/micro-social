import os
import sys

# для тестов говорим: используй SQLite вместо Postgres
os.environ["DATABASE_URL"] = "sqlite:///./test_feed.db"

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, get_db  # type: ignore
from models import Base, Post  # type: ignore

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_feed.db"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ---------- UNIT / ЛОКАЛЬНЫЕ ТЕСТЫ СЕРВИСА ----------

def test_get_post_not_found():
    resp = client.get("/api/posts/non-existing-id-123")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Post not found"


# ---------- ИНТЕГРАЦИОННЫЕ ТЕСТЫ (с моками user-service) ----------

def test_create_post_with_existing_user(monkeypatch: pytest.MonkeyPatch):
    async def fake_get(url, *args, **kwargs):
        class FakeResponse:
            status_code = 200

            def json(self):
                return {
                    "id": "user-123",
                    "email": "user@example.com",
                    "username": "user123",
                }

        return FakeResponse()

    monkeypatch.setattr(
        httpx.AsyncClient, "get",
        lambda self, url, *a, **k: fake_get(url, *a, **k)
    )

    payload = {
        "author_id": "user-123",
        "text": "integration test post",
    }

    resp = client.post("/api/posts", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["author_id"] == "user-123"
    assert data["text"] == "integration test post"
    assert "id" in data


def test_create_post_with_missing_user(monkeypatch: pytest.MonkeyPatch):
    async def fake_get_404(url, *args, **kwargs):
        class FakeResponse:
            status_code = 404

            def json(self):
                return {"detail": "User not found"}

        return FakeResponse()

    monkeypatch.setattr(
        httpx.AsyncClient, "get",
        lambda self, url, *a, **k: fake_get_404(url, *a, **k)
    )

    payload = {
        "author_id": "non-existing",
        "text": "should fail",
    }

    resp = client.post("/api/posts", json=payload)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Author does not exist"
