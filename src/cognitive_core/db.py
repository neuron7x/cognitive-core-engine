"""Database models and base class."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Pipeline(Base):
    """A pipeline groups runs together."""

    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    runs = relationship("Run", back_populates="pipeline")


class Run(Base):
    """A single execution of a pipeline."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, server_default="pending")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    pipeline = relationship("Pipeline", back_populates="runs")
    events = relationship("Event", back_populates="run")
    artifacts = relationship("Artifact", back_populates="run")


class Event(Base):
    """Events emitted during a run."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    type = Column(String(100), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    run = relationship("Run", back_populates="events")


class Artifact(Base):
    """Artifacts produced by runs."""

    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    uri = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    run = relationship("Run", back_populates="artifacts")
