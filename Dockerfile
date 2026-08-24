FROM python:3.11-slim

WORKDIR /app

# Install deps first (layer caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic-settings

# Install rubra-sdk
# In production: pip install rubra>=0.1.0
# For local dev build: COPY ../rubra-sdk /rubra-sdk && pip install /rubra-sdk
ARG RUBRA_SDK_VERSION=0.1.0
RUN pip install --no-cache-dir rubra==${RUBRA_SDK_VERSION} || \
    echo "rubra not yet on PyPI — mount or COPY rubra-sdk manually"

COPY app/ ./app/

# Persistent storage volume
VOLUME ["/data"]
ENV RUBRA_DATABASE_URL=sqlite:////data/rubra.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
