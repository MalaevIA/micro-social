import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, USERS  # type: ignore
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- UNIT-ТЕСТЫ ----------

def test_create_user():
    USERS.clear()

    payload = {
        "email": "test@example.com",
        "username": "testuser"
    }

    resp = client.post("/api/users", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["id"] in USERS


def test_get_user():
    USERS.clear()

    resp_create = client.post("/api/users", json={
        "email": "get@example.com",
        "username": "getuser"
    })
    assert resp_create.status_code == 200
    user_id = resp_create.json()["id"]

    resp = client.get(f"/api/users/{user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user_id
    assert data["email"] == "get@example.com"
    assert data["username"] == "getuser"


def test_update_user():
    USERS.clear()

    resp_create = client.post("/api/users", json={
        "email": "update@example.com",
        "username": "oldname"
    })
    user_id = resp_create.json()["id"]

    resp_update = client.patch(f"/api/users/{user_id}", json={
        "username": "newname",
        "bio": "updated bio"
    })
    assert resp_update.status_code == 200

    data = resp_update.json()
    assert data["username"] == "newname"
    assert data["bio"] == "updated bio"


# ---------- ИНТЕГРАЦИОННЫЕ ТЕСТЫ (простые) ----------

def test_get_user_not_found():
    USERS.clear()

    resp = client.get("/api/users/non-existing-id-123")
    assert resp.status_code == 404

    data = resp.json()
    assert data["detail"] == "User not found"
