from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, ConfigDict

Base = declarative_base()


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False, default="Untitled")
    body = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    crawled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    pagerank_score = Column(Float, default=0.0)


class DocumentCreate(BaseModel):
    url: str
    title: str = "Untitled"
    body: str
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    url: str
    title: str
    body: str
    description: Optional[str] = None
    crawled_at: Optional[datetime] = None
    pagerank_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)
