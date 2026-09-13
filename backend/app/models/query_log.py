from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime
from pydantic import BaseModel
from app.models.document import Base


class QueryLogDB(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(String, index=True, nullable=False)
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QueryLogCreate(BaseModel):
    query: str
    results_count: int
    execution_time_ms: float
