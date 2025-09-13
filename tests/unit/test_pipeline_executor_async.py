import asyncio

from cognitive_core.core.pipeline_executor_async import PipelineExecutorAsync
from cognitive_core.domain.pipelines import Pipeline


def test_execute_awaits_coroutine_steps():
    order = []

    async def step_one():
        await asyncio.sleep(0.01)
        order.append("step_one")
        return "a"

    def step_two():
        order.append("step_two")
        return "b"

    pipeline = Pipeline(id="p_async", name="AsyncPipe", steps=[step_one, step_two])
    run = asyncio.run(PipelineExecutorAsync().execute(pipeline))

    assert order == ["step_one", "step_two"]
    assert [a.data for a in run.artifacts] == ["a", "b"]
    assert run.status == "completed"
    assert len(run.events) == 4
