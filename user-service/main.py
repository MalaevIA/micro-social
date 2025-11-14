from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional, List

app = FastAPI(title="User Service")

class UserCreate(BaseModel):
    email: str
    username: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None

# простейшее in-memory "хранилище"
USERS: dict[str, User] = {}


@app.post("/api/users", response_model=User)
def create_user(user: UserCreate):
    user_id = str(uuid4())
    new_user = User(
        id=user_id,
        email=user.email,
        username=user.username,
        avatar=None,
        bio=None
    )
    USERS[user_id] = new_user
    return new_user


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: str):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/api/users/{user_id}", response_model=User)
def update_user(user_id: str, data: UserUpdate):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = user.copy(update=data.dict(exclude_unset=True))
    USERS[user_id] = updated
    return updated


@app.get("/api/users/search", response_model=List[User])
def search_users(query: str):
    result = [
        u for u in USERS.values()
        if query.lower() in u.username.lower() or query.lower() in u.email.lower()
    ]
    return result
