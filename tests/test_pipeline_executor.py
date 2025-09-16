import asyncio
import time


def test_pipeline_executor_runs_steps():
    from cognitive_core.core.pipeline_executor import PipelineExecutor
    from cognitive_core.domain.pipelines import Artifact, Pipeline

    def step_one():
        return Artifact(name="a", data=1)

    def step_two():
        return Artifact(name="b", data=2)

    pipeline = Pipeline(id="p1", name="Test", steps=[step_one, step_two])
    run = PipelineExecutor().execute(pipeline)

    assert [a.data for a in run.artifacts] == [1, 2]
    assert run.status == "completed"
    assert len(run.events) == 4


def test_execute_async_runs_steps_in_parallel_and_records_events():
    from cognitive_core.core.pipeline_executor import PipelineExecutor
    from cognitive_core.domain.pipelines import Artifact, Pipeline, Run

    async def step_one():
        await asyncio.sleep(0.2)
        return Artifact(name="a", data=1)

    async def step_two():
        await asyncio.sleep(0.2)
        return Artifact(name="b", data=2)

    async def _run() -> tuple[float, Run]:
        pipeline = Pipeline(id="p2", name="AsyncTest", steps=[step_one, step_two])
        start = time.time()
        run = await PipelineExecutor().execute_async(pipeline)
        duration = time.time() - start
        return duration, run

    duration, run = asyncio.run(_run())

    assert duration < 0.35
    assert sorted(a.data for a in run.artifacts) == [1, 2]
    assert run.status == "completed"
    assert len(run.events) == 4

    for step in ["step_one", "step_two"]:
        start_event = next(e for e in run.events if e.step == step and e.type == "start")
        end_event = next(e for e in run.events if e.step == step and e.type == "end")
        assert start_event.timestamp <= end_event.timestamp
