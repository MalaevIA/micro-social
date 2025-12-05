import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, NOTIFICATIONS  # type: ignore
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- UNIT-ТЕСТЫ ----------

def test_create_notification():
    NOTIFICATIONS.clear()

    payload = {
        "user_id": "user-1",
        "type": "new_message",
        "payload": {"dialog_id": "dlg-1"}
    }

    resp = client.post("/api/notifications", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["user_id"] == "user-1"
    assert data["type"] == "new_message"
    assert data["is_read"] is False
    assert data["id"] in NOTIFICATIONS


def test_mark_notification_read_not_found():
    NOTIFICATIONS.clear()

    resp = client.patch("/api/notifications/non-existing-id/read")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Notification not found"


# ---------- ИНТЕГРАЦИОННЫЙ ТЕСТ ----------

def test_create_and_list_notifications_for_user():
    NOTIFICATIONS.clear()

    client.post("/api/notifications", json={
        "user_id": "user-1",
        "type": "new_message",
        "payload": {"dialog_id": "dlg-1"}
    })
    client.post("/api/notifications", json={
        "user_id": "user-2",
        "type": "system",
        "payload": {}
    })

    resp = client.get("/api/notifications/user-1")
    assert resp.status_code == 200

    items = resp.json()
    assert len(items) == 1
    assert items[0]["user_id"] == "user-1"
    assert items[0]["type"] == "new_message"
