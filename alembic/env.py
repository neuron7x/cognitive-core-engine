from alembic import context
from sqlalchemy import engine_from_config, pool
import os
config = context.config
target_metadata = None
def run_migrations_offline():
    url = os.environ.get("DATABASE_URL", "sqlite:///./local.sqlite3")
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()
def run_migrations_online():
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = os.environ.get("DATABASE_URL", "sqlite:///./local.sqlite3")
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
