import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from main import app, EVENTS  # type: ignore
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- UNIT-ТЕСТЫ ----------

def test_push_event():
    EVENTS.clear()

    payload = {
        "user_id": "user-1",
        "event_type": "view_post",
        "object_id": "post-1"
    }

    resp = client.post("/api/recommendations/event", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert len(EVENTS) == 1

    event = EVENTS[0]

    # Если это Pydantic-модель / обычный объект
    user_id = getattr(event, "user_id", None)

    # Если вдруг там dict (на будущее)
    if user_id is None and isinstance(event, dict):
        user_id = event.get("user_id")

    assert user_id == "user-1"


# ---------- ИНТЕГРАЦИОННЫЙ ТЕСТ ----------

def test_get_recommendations():
    resp = client.get("/api/recommendations/user-1")
    assert resp.status_code == 200

    items = resp.json()
    # т.к. сервис возвращает статический список - просто проверяем формат ответа
    assert isinstance(items, list)
    assert len(items) >= 1
    assert "post_id" in items[0]
    assert "score" in items[0]
