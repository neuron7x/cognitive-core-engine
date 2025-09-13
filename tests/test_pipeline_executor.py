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
