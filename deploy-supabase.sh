#!/bin/bash
# Deploy aut-pin with Supabase. Pulls images from Docker Hub. Fetches compose from GitHub.
# Usage: SUPABASE_DB_URL='postgresql://...pooler...:6543/postgres' curl -sSL URL | bash
# Prefer Supabase Transaction pooler (port 6543) to avoid MaxClientsInSessionMode on :5432.
# Optional: SUPABASE_POOL_MAX (default 12) — cap DB connections per app process; see multi-domain-clean/db.py

set -e
GITHUB_RAW="https://raw.githubusercontent.com/nouamanedahhakgit/aut-pin/main"
URL="${SUPABASE_DB_URL:-$1}"
POOL_MAX="${SUPABASE_POOL_MAX:-12}"
if [ -z "$URL" ]; then
  echo "Set SUPABASE_DB_URL to your Postgres URI (transaction pooler :6543 recommended), e.g.:" >&2
  echo "  export SUPABASE_DB_URL='postgresql://postgres.[ref]:[pass]@aws-0-[region].pooler.supabase.com:6543/postgres'" >&2
  exit 1
fi

mkdir -p ~/aut-pin && cd ~/aut-pin
curl -sSLo docker-compose.hub.yml "$GITHUB_RAW/docker-compose.hub.yml"
# Docker Hub login + pass token to updater (for Update button in admin UI)
if [ -n "$DOCKERHUB_TOKEN" ]; then
  echo "$DOCKERHUB_TOKEN" | docker login -u "${DOCKERHUB_USERNAME:-boarddash31}" --password-stdin 2>/dev/null || true
fi
mkdir -p output/static-projects
docker volume create aut-pin_env-config 2>/dev/null || true

docker run --rm -v aut-pin_env-config:/data -e URL="$URL" -e POOL_MAX="$POOL_MAX" alpine sh -c '
  echo DB_BACKEND=supabase > /data/multi-domain-clean.env
  echo SUPABASE_DB_URL="$URL" >> /data/multi-domain-clean.env
  echo SUPABASE_POOL_MAX="$POOL_MAX" >> /data/multi-domain-clean.env
  echo SECRET_KEY=change-me-in-production >> /data/multi-domain-clean.env
  echo PIN_API_URL=http://pin_generator:5000 >> /data/multi-domain-clean.env
  echo GENERATE_ARTICLE_API_URL=http://articles-website-generator:5002 >> /data/multi-domain-clean.env
  echo WEBSITE_PARTS_API_URL=http://website-parts-generator:5003 >> /data/multi-domain-clean.env
  echo LLAMACPP_MANAGER_URL=http://llamacpp_manager:5004 >> /data/multi-domain-clean.env
'

docker compose -f docker-compose.hub.yml pull --ignore-pull-failures 2>/dev/null || true
docker compose -f docker-compose.hub.yml up -d
echo "Done. Admin UI: http://$(hostname -I | awk '{print $1}'):6001"
