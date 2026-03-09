# pin_generator: pin image generation API (requires Playwright for screenshots)
FROM python:3.11-slim

WORKDIR /app

# Install Playwright system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copy root requirements (build context = repo root when using docker-compose)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

# Copy pin_generator (when context=., use pin_generator/)
COPY pin_generator/ ./

EXPOSE 5000

CMD ["python", "generator.py", "--serve", "--port", "5000"]
