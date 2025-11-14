from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import List

app = FastAPI(title="Chat Service")

class DialogCreate(BaseModel):
    user1_id: str
    user2_id: str

class MessageCreate(BaseModel):
    author_id: str
    text: str

class Message(BaseModel):
    id: str
    author_id: str
    text: str

DIALOGS: dict[str, list[Message]] = {}


@app.post("/api/dialogs")
def create_dialog(data: DialogCreate):
    dialog_id = str(uuid4())
    DIALOGS[dialog_id] = []
    return {"dialog_id": dialog_id, "participants": [data.user1_id, data.user2_id]}


@app.post("/api/dialogs/{dialog_id}/messages", response_model=Message)
def send_message(dialog_id: str, data: MessageCreate):
    if dialog_id not in DIALOGS:
        raise HTTPException(status_code=404, detail="Dialog not found")
    msg = Message(id=str(uuid4()), author_id=data.author_id, text=data.text)
    DIALOGS[dialog_id].append(msg)
    return msg


@app.get("/api/dialogs/{dialog_id}/messages", response_model=List[Message])
def get_messages(dialog_id: str):
    if dialog_id not in DIALOGS:
        raise HTTPException(status_code=404, detail="Dialog not found")
    return DIALOGS[dialog_id]
