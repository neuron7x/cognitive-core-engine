import asyncio
import contextlib
from unittest.mock import patch


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


def test_pipeline_executor_execute_awaits_async_steps():
    from cognitive_core.core.pipeline_executor import PipelineExecutor
    from cognitive_core.domain.pipelines import Artifact, Pipeline

    async def async_step():
        await asyncio.sleep(0)
        return Artifact(name="async", data=42)

    pipeline = Pipeline(id="p_async", name="Async", steps=[async_step])
    run = PipelineExecutor().execute(pipeline)

    assert len(run.artifacts) == 1
    assert isinstance(run.artifacts[0], Artifact)
    assert run.artifacts[0].data == 42


def test_execute_async_runs_steps_in_parallel_and_records_events():
    from cognitive_core.core.pipeline_executor import PipelineExecutor
    from cognitive_core.domain.pipelines import Artifact, Pipeline, Run

    async def _run() -> tuple[Run, list[tuple[str, str]]]:
        class SleepController:
            def __init__(self) -> None:
                self.waiters: list[asyncio.Future] = []
                self.ready = asyncio.Event()

            async def sleep(self, _: float) -> None:
                loop = asyncio.get_running_loop()
                waiter: asyncio.Future = loop.create_future()
                self.waiters.append(waiter)
                if len(self.waiters) >= 2:
                    self.ready.set()
                await waiter

            def release_all(self) -> None:
                for waiter in self.waiters:
                    if not waiter.done():
                        waiter.set_result(None)

        sleep_controller = SleepController()
        step_events: list[tuple[str, str]] = []

        async def step_one():
            step_events.append(("step_one", "start"))
            await asyncio.sleep(0.2)
            step_events.append(("step_one", "end"))
            return Artifact(name="a", data=1)

        async def step_two():
            step_events.append(("step_two", "start"))
            await asyncio.sleep(0.2)
            step_events.append(("step_two", "end"))
            return Artifact(name="b", data=2)

        async def fake_sleep(delay: float) -> None:
            await sleep_controller.sleep(delay)

        with patch("asyncio.sleep", new=fake_sleep):
            pipeline = Pipeline(id="p2", name="AsyncTest", steps=[step_one, step_two])
            run_task = asyncio.create_task(PipelineExecutor().execute_async(pipeline))

            try:
                await asyncio.wait_for(sleep_controller.ready.wait(), timeout=1)
            except asyncio.TimeoutError:
                run_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await run_task
                raise

            assert len(step_events) == 2
            assert {name for name, event_type in step_events} == {
                "step_one",
                "step_two",
            }
            assert all(event_type == "start" for _, event_type in step_events)

            sleep_controller.release_all()
            run = await run_task

        return run, step_events

    run, step_events = asyncio.run(_run())

    assert sorted(a.data for a in run.artifacts) == [1, 2]
    assert run.status == "completed"
    assert len(run.events) == 4
    assert len(step_events) == 4

    assert {event for event in step_events[:2]} == {
        ("step_one", "start"),
        ("step_two", "start"),
    }
    assert {event for event in step_events[2:]} == {
        ("step_one", "end"),
        ("step_two", "end"),
    }
    assert all(event_type == "end" for _, event_type in step_events[2:])

    for step in ["step_one", "step_two"]:
        start_event = next(e for e in run.events if e.step == step and e.type == "start")
        end_event = next(e for e in run.events if e.step == step and e.type == "end")
        assert start_event.timestamp <= end_event.timestamp
