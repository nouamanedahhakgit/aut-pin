# llamacpp_manager: manage llama.cpp models, launch llama-server, expose API
# llama-server expected on PATH or in ./bin; models mounted via volume
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (Flask, requests)
RUN pip install --no-cache-dir flask requests

# Copy package (build context = repo root)
COPY llamacpp_manager/ /app/llamacpp_manager/
ENV PYTHONPATH=/app

WORKDIR /app

# Volumes for models and SQLite (override via compose)
VOLUME ["/app/llamacpp_manager/models", "/app/llamacpp_manager/data"]

EXPOSE 5004

# Use port from env
ENV LLAMACPP_MANAGER_PORT=5004
CMD ["python", "-m", "llamacpp_manager.app"]
