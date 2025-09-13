import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head(tmp_path):
    """Run Alembic migrations and ensure tables are created."""

    db_url = f"sqlite:///{tmp_path/'test.sqlite'}"
    os.environ["DATABASE_URL"] = db_url

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    for table in ("pipelines", "runs", "events", "artifacts"):
        assert inspector.has_table(table)

