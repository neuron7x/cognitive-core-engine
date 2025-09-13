"""PII detection helpers."""
from __future__ import annotations
import re

EMAIL_RE = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")


def contains_email(text: str) -> bool:
    """Return True if text contains an email address."""
    return bool(EMAIL_RE.search(text))
