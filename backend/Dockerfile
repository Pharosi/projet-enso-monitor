# Image unique du backend : utilisée par l'API, le worker ETL et les migrations
# (seule la commande change, définie dans deploy/compose.yaml).
FROM python:3.14-slim

# Pas de fichiers .pyc, journaux affichés immédiatement, pas de cache pip dans l'image.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dépendances d'abord : cette couche reste en cache tant que pyproject.toml ne change pas.
COPY pyproject.toml ./
COPY enso ./enso
RUN pip install .

COPY alembic.ini ./
COPY alembic ./alembic

# Le processus ne tourne jamais en root (limite les dégâts en cas de faille).
RUN useradd --create-home --uid 10001 enso
USER enso

EXPOSE 8000
CMD ["uvicorn", "enso.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
