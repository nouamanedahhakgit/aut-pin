# articles-website-generator: article content generation API
FROM python:3.11-slim

WORKDIR /app

# Copy root requirements (build context = repo root)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy service
COPY articles-website-generator/ ./

EXPOSE 5002

CMD ["uvicorn", "route:app", "--host", "0.0.0.0", "--port", "5002"]
