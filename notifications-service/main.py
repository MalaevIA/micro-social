from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from typing import List

app = FastAPI(title="Notifications Service")

class NotificationCreate(BaseModel):
    user_id: str
    type: str
    payload: dict

class Notification(BaseModel):
    id: str
    user_id: str
    type: str
    payload: dict
    is_read: bool

NOTIFICATIONS: dict[str, Notification] = {}


@app.post("/api/notifications", response_model=Notification)
def create_notification(data: NotificationCreate):
    notif_id = str(uuid4())
    notif = Notification(
        id=notif_id,
        user_id=data.user_id,
        type=data.type,
        payload=data.payload,
        is_read=False
    )
    NOTIFICATIONS[notif_id] = notif
    return notif


@app.get("/api/notifications/{user_id}", response_model=List[Notification])
def get_notifications(user_id: str):
    return [n for n in NOTIFICATIONS.values() if n.user_id == user_id]


@app.patch("/api/notifications/{notif_id}/read", response_model=Notification)
def mark_read(notif_id: str):
    notif = NOTIFICATIONS.get(notif_id)
    if not notif:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    NOTIFICATIONS[notif_id] = notif
    return notif
