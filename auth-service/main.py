from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="Auth Service")

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

TOKENS: dict[str, str] = {}  # access_token -> user_id


@app.post("/api/auth/register")
def register(data: RegisterRequest):
    # в реальности тут был бы вызов user-service и сохранение пользователя
    user_id = str(uuid4())
    return {"id": user_id, "email": data.email, "username": data.username}


@app.post("/api/auth/login")
def login(data: LoginRequest):
    # тут просто фейковый токен
    access_token = str(uuid4())
    TOKENS[access_token] = "some-user-id"
    return {"access_token": access_token}


@app.post("/api/auth/refresh")
def refresh_token(old_token: str):
    if old_token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    new_token = str(uuid4())
    TOKENS[new_token] = TOKENS[old_token]
    del TOKENS[old_token]
    return {"access_token": new_token}
