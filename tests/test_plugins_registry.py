from cognitive_core.plugins import REGISTRY, dispatch


def test_math_plugin_registration_and_execution():
    import cognitive_core.plugins.example.math_plugin  # noqa: F401

    assert "math.dot" in REGISTRY
    result = dispatch("math.dot", {"a": [1, 2], "b": [3, 4]})
    assert result["result"] == 11

