import os
import shutil
import subprocess
import tempfile

import pytest


def test_alembic_migrations_smoke():
    if shutil.which("alembic") is None:
        pytest.skip("alembic not installed")
    if not os.path.exists("alembic.ini"):
        pytest.skip("alembic.ini not found")
    migrations_path = os.path.join("alembic", "versions")
    if not os.path.isdir(migrations_path):
        pytest.skip("no migrations folder")
    with tempfile.TemporaryDirectory() as d:
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///" + os.path.join(d, "t.sqlite3")
        proc = subprocess.run(
            ["alembic", "upgrade", "head"], env=env, capture_output=True, text=True
        )
        assert proc.returncode == 0, proc.stderr
        proc = subprocess.run(
            ["alembic", "downgrade", "base"], env=env, capture_output=True, text=True
        )
        assert proc.returncode == 0, proc.stderr
