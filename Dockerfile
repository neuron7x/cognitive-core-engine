
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY . /app
RUN pip install --upgrade pip && pip install --no-cache-dir requests httpx redis sqlalchemy alembic psycopg2-binary prometheus-client structlog
EXPOSE 8000
CMD ["uvicorn", "cognitive_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health')" || exit 1
