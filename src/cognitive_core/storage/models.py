from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import JSON, Float, String, Integer, DateTime, func
Base = declarative_base()

class Episode(Base):
    __tablename__ = "episodes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped = mapped_column(DateTime(timezone=True), server_default=func.now())
    key: Mapped[str] = mapped_column(String(128), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)
    reward: Mapped[float] = mapped_column(Float, default=0.0)
    surprise: Mapped[float] = mapped_column(Float, default=0.0)
