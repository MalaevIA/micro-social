from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from db import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    author_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
