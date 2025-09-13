from cognitive_core.plugins import REGISTRY, dispatch
from cognitive_core.plugins.plugin_loader import load_plugins


def test_math_plugin_registration_and_execution():
    load_plugins()

    assert "math.dot" in REGISTRY
    meta, _ = REGISTRY["math.dot"]
    assert meta.version == "1.0.0"
    result = dispatch("math.dot", {"a": [1, 2], "b": [3, 4]})
    assert result["result"] == 11
