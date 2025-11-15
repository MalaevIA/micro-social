from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Recommendations Service")

class Event(BaseModel):
    user_id: str
    event_type: str
    object_id: str

class Recommendation(BaseModel):
    post_id: str
    score: float

EVENTS: list[Event] = []


@app.post("/api/recommendations/event")
def push_event(event: Event):
    EVENTS.append(event)
    return {"status": "ok"}


@app.get("/api/recommendations/{user_id}", response_model=List[Recommendation])
def get_recommendations(user_id: str):

    return [
        Recommendation(post_id="post-1", score=0.95),
        Recommendation(post_id="post-2", score=0.88),
    ]
