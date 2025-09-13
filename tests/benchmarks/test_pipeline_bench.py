from cognitive_core.core.pipeline_executor import PipelineExecutor
from cognitive_core.domain.pipelines import Artifact, Pipeline


def test_pipeline_execution_benchmark(benchmark):
    """Benchmark execution time of a simple pipeline."""

    def step_sum() -> Artifact:
        total = sum(range(1000))
        return Artifact(name="sum", data=total)

    def step_double() -> Artifact:
        values = [x * 2 for x in range(1000)]
        return Artifact(name="double", data=values)

    pipeline = Pipeline(id="bench", name="Benchmark", steps=[step_sum, step_double])
    executor = PipelineExecutor()

    def run_pipeline() -> None:
        executor.execute(pipeline)

    benchmark(run_pipeline)
