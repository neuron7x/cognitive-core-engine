import pytest

from cognitive_core.core.agents_router import AgentsRouter


def test_run_rejects_parent_directory_role(tmp_path):
    router = AgentsRouter(config_dir=tmp_path)

    with pytest.raises(ValueError):
        router.run("prompt", roles=["../malicious"])


def test_run_rejects_windows_style_parent_directory_role(tmp_path):
    router = AgentsRouter(config_dir=tmp_path)

    with pytest.raises(ValueError):
        router.run("prompt", roles=["..\\malicious"])


def test_load_role_rejects_parent_directory_role(tmp_path):
    router = AgentsRouter(config_dir=tmp_path)

    with pytest.raises(ValueError):
        router.load_role("../malicious")
