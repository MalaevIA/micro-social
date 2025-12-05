import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, TOKENS  # type: ignore
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- UNIT-ТЕСТЫ ----------

def test_register_creates_user_like_object():
    payload = {
        "email": "user@example.com",
        "username": "user1",
        "password": "Qwerty123!"
    }

    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_login_returns_token():
    payload = {
        "email": "user@example.com",
        "password": "Qwerty123!"
    }

    resp = client.post("/api/auth/login", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "access_token" in data
    assert data["access_token"] in TOKENS


# ---------- ИНТЕГРАЦИОННЫЙ ТЕСТ (авторизация как цепочка) ----------

def test_login_idempotent():
    """
    Интеграционный сценарий:
    два раза подряд логинимся с одними и теми же данными,
    оба раза получаем валидный токен (ошибки нет).
    """

    payload = {
        "email": "user@example.com",
        "password": "Qwerty123!"
    }

    resp1 = client.post("/api/auth/login", json=payload)
    resp2 = client.post("/api/auth/login", json=payload)

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    token1 = resp1.json().get("access_token")
    token2 = resp2.json().get("access_token")

    assert token1 is not None
    assert token2 is not None
