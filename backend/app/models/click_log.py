from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from app.models.document import Base


class ClickLogDB(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(String, index=True, nullable=False)
    doc_id = Column(Integer, nullable=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ClickLogCreate(BaseModel):
    query: str
    doc_id: int
    position: int = 0
