import time
from pathlib import Path

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


def test_load_role_returns_cached_config_without_reopen(tmp_path, monkeypatch):
    config_dir = Path(tmp_path)
    role_path = config_dir / "cached.yaml"
    role_path.write_text("""name: cached
system_prompt: hello
model: mock
""")

    router = AgentsRouter(config_dir=config_dir)

    first_config = router.load_role("cached")

    original_open = Path.open

    def fail_if_reopened(self, *args, **kwargs):
        if self == role_path:
            raise AssertionError("Cached role configuration should not be reopened")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_if_reopened)

    cached_config = router.load_role("cached")

    assert cached_config == first_config


def test_load_role_reloads_when_modified(tmp_path):
    config_dir = Path(tmp_path)
    role_path = config_dir / "reload.yaml"
    role_path.write_text("""name: original
system_prompt: hello
model: mock
""")

    router = AgentsRouter(config_dir=config_dir)

    original_config = router.load_role("reload")

    time.sleep(1)

    role_path.write_text("""name: updated
system_prompt: hi
model: mock
""")

    updated_config = router.load_role("reload")

    assert updated_config.role.name == "updated"
    assert updated_config != original_config
