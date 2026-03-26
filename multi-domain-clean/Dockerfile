# multi-domain-clean: main admin UI and orchestrator
FROM python:3.11-slim

WORKDIR /app

# Install system deps for psycopg2, Pillow, etc.
# Node.js + npm are required for Cloudflare deploy (wrangler via npx).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
