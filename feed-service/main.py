import os
from uuid import uuid4
from typing import List

import httpx
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import Base, Post

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feed Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

class PostCreate(BaseModel):
    author_id: str
    text: str

class PostOut(BaseModel):
    id: str
    author_id: str
    text: str
    created_at: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1) СОЗДАНИЕ ПОСТА (эндпоинт с вложенным вызовом в user-service)
@app.post("/api/posts", response_model=PostOut)
async def create_post(data: PostCreate, db: Session = Depends(get_db)):
    # вложенный вызов: проверяем, что пользователь существует
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/api/users/{data.author_id}")
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Author does not exist")

    post_id = str(uuid4())
    post = Post(id=post_id, author_id=data.author_id, text=data.text)
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostOut(
        id=post.id,
        author_id=post.author_id,
        text=post.text,
        created_at=post.created_at.isoformat()
    )


# 2) Получение поста по id
@app.get("/api/posts/{post_id}", response_model=PostOut)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostOut(
        id=post.id,
        author_id=post.author_id,
        text=post.text,
        created_at=post.created_at.isoformat()
    )


# 3) Лента постов
@app.get("/api/feed", response_model=List[PostOut])
def get_feed(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        PostOut(
            id=p.id,
            author_id=p.author_id,
            text=p.text,
            created_at=p.created_at.isoformat()
        )
        for p in posts
    ]


# 4) Удаление поста
@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"id": post_id, "deleted": True}
