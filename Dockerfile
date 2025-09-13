# --- build stage ---
FROM python:3.11-slim AS build
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels .

# --- runtime stage ---
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN adduser --disabled-password --gecos '' app && chown -R app:app /app
COPY --from=build /wheels /wheels
RUN pip install --no-index --find-links=/wheels cognitive-core-engine && rm -rf /wheels
USER app
EXPOSE 8000
CMD ["uvicorn", "cognitive_core.api:app", "--host", "0.0.0.0", "--port", "8000"]
