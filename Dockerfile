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

ARG APP_USER=appuser
ARG APP_UID=1000
ARG APP_GID=1000

RUN set -eux; \
    groupadd --gid "${APP_GID}" "${APP_USER}"; \
    useradd \
        --uid "${APP_UID}" \
        --gid "${APP_GID}" \
        --create-home \
        --shell /bin/bash \
        "${APP_USER}"

COPY --chown=${APP_USER}:${APP_USER} . /app

RUN set -eux; \
    install -d -m 0755 \
        /app/alembic \
        /app/bin \
        /app/config \
        /app/deployment \
        /app/docs \
        /app/src \
        /app/tests \
        /app/tools; \
    for path in /app/bin/example_run.py /app/tools/validate.py; do \
        if [ -f "${path}" ]; then chmod +x "${path}"; fi; \
    done; \
    chown -R ${APP_USER}:${APP_USER} /app

USER ${APP_USER}

EXPOSE 8000
CMD ["uvicorn", "cognitive_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import os, urllib.request as u; raw=os.environ.get('COG_API_PREFIX', '/api'); prefix='/' + raw.strip('/') if raw else ''; prefix='' if prefix == '/' else prefix; u.urlopen(f'http://127.0.0.1:8000{prefix}/health')" || exit 1
