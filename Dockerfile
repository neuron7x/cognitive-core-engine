FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
        requests \
        httpx \
        redis \
        sqlalchemy \
        alembic \
        psycopg2-binary \
        prometheus-client \
        structlog

RUN groupadd -g 1000 appuser \
    && useradd -m -u 1000 -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser . /app

EXPOSE 8000
CMD ["uvicorn", "cognitive_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health')" || exit 1
