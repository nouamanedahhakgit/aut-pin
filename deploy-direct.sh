#!/bin/bash
# Deploy directly from local to server (no Docker Hub - faster)
# Usage: ./deploy-direct.sh
#   SERVER=root@72.61.197.144 (default)
#   SUPABASE_DB_URL=postgresql://... (required — use transaction pooler :6543 on servers)
#   SUPABASE_POOL_MAX=10 (optional)
#
# Builds images locally, transfers via SSH, runs compose on server.
# No docker login needed. No Docker Hub rate limits.

set -e
SERVER="${SERVER:-root@72.61.197.144}"
USERNAME="${DOCKERHUB_USERNAME:-boarddash31}"
TAG="latest"
DB_URL="${SUPABASE_DB_URL:-}"
POOL_MAX="${SUPABASE_POOL_MAX:-12}"
if [ -z "$DB_URL" ]; then
  echo "Set SUPABASE_DB_URL (e.g. transaction pooler on port 6543). See deploy-supabase.sh header." >&2
  exit 1
fi

SERVICES=(
  "orchestrator:./orchestrator:./orchestrator/Dockerfile:aut-pin-orchestrator"
  "multi-domain-clean:./multi-domain-clean:./multi-domain-clean/Dockerfile:aut-pin-multi-domain-clean"
  "pin_generator:.:./pin_generator/Dockerfile:aut-pin-pin_generator"
  "articles-website-generator:.:./articles-website-generator/Dockerfile:aut-pin-articles-website-generator"
  "website-parts-generator:./website-parts-generator:./website-parts-generator/Dockerfile:aut-pin-website-parts-generator"
  "llamacpp_manager:.:./llamacpp_manager/Dockerfile:aut-pin-llamacpp_manager"
  "updater:./multi-domain-clean/updater:./multi-domain-clean/updater/Dockerfile:aut-pin-updater"
)

echo "=== Build and deploy to $SERVER (no Docker Hub) ==="

for s in "${SERVICES[@]}"; do
  IFS=':' read -r name ctx df img <<< "$s"
  echo ">>> Building $name"
  docker build -f "$df" -t "$USERNAME/$img:$TAG" "$ctx"
done

for s in "${SERVICES[@]}"; do
  IFS=':' read -r name ctx df img <<< "$s"
  echo ">>> Transferring $USERNAME/$img:$TAG"
  docker save "$USERNAME/$img:$TAG" | ssh "$SERVER" "docker load"
done

echo ">>> Copying docker-compose.hub.yml"
scp docker-compose.hub.yml "$SERVER:~/aut-pin/"

echo ">>> Starting containers on server"
ssh "$SERVER" "cd ~/aut-pin && mkdir -p output/static-projects articles-website-generator/generators && \
  docker volume create aut-pin_env-config 2>/dev/null || true && \
  docker run --rm -v aut-pin_env-config:/data -e URL=\"$DB_URL\" -e POOL_MAX=\"$POOL_MAX\" alpine sh -c '
    echo DB_BACKEND=supabase > /data/multi-domain-clean.env
    echo SUPABASE_DB_URL=\"\$URL\" >> /data/multi-domain-clean.env
    echo SUPABASE_POOL_MAX=\"\$POOL_MAX\" >> /data/multi-domain-clean.env
    echo SECRET_KEY=change-me-in-production >> /data/multi-domain-clean.env
    echo PIN_API_URL=http://pin_generator:5000 >> /data/multi-domain-clean.env
    echo GENERATE_ARTICLE_API_URL=http://articles-website-generator:5002 >> /data/multi-domain-clean.env
    echo WEBSITE_PARTS_API_URL=http://website-parts-generator:5003 >> /data/multi-domain-clean.env
    echo LLAMACPP_MANAGER_URL=http://llamacpp_manager:5004 >> /data/multi-domain-clean.env
  ' && \
  DOCKERHUB_USERNAME=$USERNAME docker compose -f docker-compose.hub.yml up -d"

echo ""
echo "Done. Admin: http://72.61.197.144:6001"
