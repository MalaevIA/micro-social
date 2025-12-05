import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, DIALOGS  # type: ignore
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- UNIT-ТЕСТЫ ----------

def test_create_dialog():
    DIALOGS.clear()

    payload = {
        "user1_id": "user-1",
        "user2_id": "user-2"
    }

    resp = client.post("/api/dialogs", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "dialog_id" in data
    dialog_id = data["dialog_id"]
    assert dialog_id in DIALOGS
    assert data["participants"] == ["user-1", "user-2"]


def test_send_message_to_non_existing_dialog():
    resp = client.post("/api/dialogs/non-existing/messages", json={
        "author_id": "user-1",
        "text": "hello"
    })
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Dialog not found"


# ---------- ИНТЕГРАЦИОННЫЙ ТЕСТ (простая цепочка) ----------

def test_create_dialog_and_send_and_get_messages():
    DIALOGS.clear()

    # создаём диалог
    resp = client.post("/api/dialogs", json={
        "user1_id": "user-1",
        "user2_id": "user-2"
    })
    dialog_id = resp.json()["dialog_id"]

    # отправляем сообщения
    client.post(f"/api/dialogs/{dialog_id}/messages", json={
        "author_id": "user-1",
        "text": "Привет"
    })
    client.post(f"/api/dialogs/{dialog_id}/messages", json={
        "author_id": "user-2",
        "text": "Здравствуйте"
    })

    # читаем историю
    resp_msgs = client.get(f"/api/dialogs/{dialog_id}/messages")
    assert resp_msgs.status_code == 200

    msgs = resp_msgs.json()
    assert len(msgs) == 2
    assert msgs[0]["text"] == "Привет"
    assert msgs[1]["text"] == "Здравствуйте"
