from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.pipeline_executor import PipelineExecutor
from ..db import Pipeline as PipelineModel, Run as RunModel
from ..domain.pipelines import Artifact, Pipeline as DomainPipeline, Run as DomainRun


class PipelineError(Exception):
    """Base exception for pipeline service errors."""


class PipelineNotFoundError(PipelineError):
    """Raised when a pipeline does not exist."""


class PipelineAlreadyExistsError(PipelineError):
    """Raised when attempting to create a duplicate pipeline."""


@dataclass
class PipelineRepository:
    session: Session

    def list(self) -> List[PipelineModel]:
        return (
            self.session.query(PipelineModel)
            .order_by(PipelineModel.id)
            .all()
        )

    def get(self, pipeline_id: int) -> PipelineModel | None:
        return self.session.get(PipelineModel, pipeline_id)

    def get_by_name(self, name: str) -> PipelineModel | None:
        return self.session.query(PipelineModel).filter_by(name=name).one_or_none()

    def add(self, pipeline: PipelineModel) -> PipelineModel:
        self.session.add(pipeline)
        self.session.flush()
        return pipeline

    def add_run(self, run: RunModel) -> RunModel:
        self.session.add(run)
        self.session.flush()
        return run


class PipelineService:
    """Business logic for pipeline management."""

    def __init__(self, session: Session, executor: PipelineExecutor | None = None):
        self.session = session
        self.repository = PipelineRepository(session)
        self.executor = executor or PipelineExecutor()

    def list_pipelines(self) -> List[PipelineModel]:
        return self.repository.list()

    def create_pipeline(self, name: str) -> PipelineModel:
        pipeline = PipelineModel(name=name)
        self.repository.add(pipeline)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise PipelineAlreadyExistsError(name) from exc
        self.session.refresh(pipeline)
        return pipeline

    def get_pipeline(self, pipeline_id: int) -> PipelineModel:
        pipeline = self.repository.get(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(str(pipeline_id))
        return pipeline

    def run_pipeline(self, pipeline_id: int) -> Tuple[RunModel, DomainRun]:
        pipeline = self.get_pipeline(pipeline_id)
        run_model = RunModel(pipeline_id=pipeline.id, status="running")
        self.repository.add_run(run_model)

        domain_pipeline = self._to_domain_pipeline(pipeline)
        try:
            domain_run = self.executor.execute(domain_pipeline)
        except Exception:
            self.session.rollback()
            raise

        run_model.status = domain_run.status
        self.session.commit()
        self.session.refresh(run_model)
        return run_model, domain_run

    def step_count(self, pipeline: PipelineModel) -> int:
        return len(self._build_steps(pipeline))

    def _to_domain_pipeline(self, pipeline: PipelineModel) -> DomainPipeline:
        return DomainPipeline(
            id=str(pipeline.id),
            name=pipeline.name,
            steps=self._build_steps(pipeline),
        )

    def _build_steps(self, pipeline: PipelineModel) -> List:
        def _step() -> Artifact:
            return Artifact(name="result", data=1)

        _step.__name__ = "result"
        return [_step]
