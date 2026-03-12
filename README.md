# Automation Project

Multi-service automation system: domain management, pin generation, article generation, and website parts generation.

## Prerequisites

- **Python 3.10+**
- **MySQL** (for multi-domain-clean)
- **Node.js** (optional, for pin editor at `PIN_EDITOR_URL`)

## Quick Start – Run All Services

### 1. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 2. Install Playwright browsers (for pin screenshots)

```bash
playwright install chromium
```

### 3. Configure environment

Copy `.env.example` from each service you need and set your values:

- **multi-domain-clean**: `multi-domain-clean/.env` (database, API keys, etc.)
- **articles-website-generator**: `articles-website-generator/.env` (optional)
- **pin_generator**: `pin_generator/.env` (optional)
- **website-parts-generator**: `website-parts-generator/.env` (optional)

### 4. Start all services

```bash
python run_all.py start
```

This starts:

| Service                 | Port | Description                        |
|-------------------------|------|------------------------------------|
| multi-domain-clean      | 5001 | Main admin UI, domain management   |
| pin_generator           | 5000 | Pin image generation API           |
| articles-website-generator | 5002 | Article content generation API     |
| website-parts-generator | 8010 | Header, footer, category templates |

### 5. Stop all services

```bash
python run_all.py stop
```

### 6. Restart all services

```bash
python run_all.py restart
```

## Other Commands

**Run in foreground** (see logs in terminal, Ctrl+C to stop):

```bash
python run_all.py start -f
```

**View logs** (when running in background):

- Logs are written to `.logs/<service>.log`
- Example: `.logs/multi-domain-clean.log`

## Run Services Individually

If a service fails, run it manually to see errors:

```bash
# Multi-domain-clean (main app)
cd multi-domain-clean && python app.py

# Pin generator API
cd pin_generator && python generator.py --serve --port 5000

# Articles generator API
cd articles-website-generator && python -m uvicorn route:app --host 0.0.0.0 --port 5002

# Website parts generator API
cd website-parts-generator && python -m uvicorn route:app --host 0.0.0.0 --port 8010
```

## Docker

Run all services with Docker: `docker compose up -d`. Access multi-domain-clean at http://localhost:5001. See [DOCKER.md](DOCKER.md) for Docker Hub.

## Environment Variables

See each service’s `.env.example` for details. Commonly used:

- **multi-domain-clean**: `MYSQL_*`, `SECRET_KEY`, `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
- **R2/Cloudflare**: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`
- **APIs**: `GENERATE_ARTICLE_API_URL`, `WEBSITE_PARTS_API_URL`, `PIN_API_URL`, `PIN_EDITOR_URL`
