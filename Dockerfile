FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app/ ./app/

# Installs this package plus everything declared in pyproject.toml's
# dependencies — including rubra[judge] from PyPI — and registers
# rubra-server's own package metadata (needed by importlib.metadata
# at runtime for /api/v1/version).
RUN pip install --no-cache-dir .

# Persistent storage volume
VOLUME ["/data"]
ENV RUBRA_DATABASE_URL=sqlite:////data/rubra.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
