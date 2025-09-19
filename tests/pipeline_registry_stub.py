from __future__ import annotations

from cognitive_core.domain.pipelines import Artifact, Pipeline


def _demo_step() -> Artifact:
    return Artifact(name="demo_step", data={"value": 42})


PIPELINES = {
    "demo": Pipeline(id="demo", name="Demo", steps=[_demo_step])
}
