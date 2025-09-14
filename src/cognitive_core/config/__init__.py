"""Application configuration objects."""

from .settings import Settings

# Instantiate a single settings object that can be shared across the
# application.  Individual modules can import `settings` to access
# configuration values without repeatedly instantiating `Settings()`.
settings = Settings()

__all__ = ["Settings", "settings"]



