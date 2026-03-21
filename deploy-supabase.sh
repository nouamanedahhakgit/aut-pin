#!/bin/bash
# Deploy aut-pin with Supabase. Pulls images from Docker Hub. Fetches compose from GitHub.
# Usage: SUPABASE_DB_URL='...' curl -sSL URL | bash

set -e
GITHUB_RAW="https://raw.githubusercontent.com/nouamanedahhakgit/aut-pin/main"
DEFAULT_URL="postgresql://postgres.rlfsnobastwcrttdbbag:Supabase101@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
URL="${SUPABASE_DB_URL:-$1}"
URL="${URL:-$DEFAULT_URL}"

mkdir -p ~/aut-pin && cd ~/aut-pin
curl -sSLo docker-compose.hub.yml "$GITHUB_RAW/docker-compose.hub.yml"
# Docker Hub login + save token for updater (Update button in admin UI)
if [ -n "$DOCKERHUB_TOKEN" ]; then
  echo "$DOCKERHUB_TOKEN" | docker login -u "${DOCKERHUB_USERNAME:-boarddash31}" --password-stdin 2>/dev/null || true
  echo "DOCKERHUB_TOKEN=$DOCKERHUB_TOKEN" > .dockerhub.env
  echo "DOCKERHUB_USERNAME=${DOCKERHUB_USERNAME:-boarddash31}" >> .dockerhub.env
fi
mkdir -p output/static-projects articles-website-generator/generators
docker volume create aut-pin_env-config 2>/dev/null || true

docker run --rm -v aut-pin_env-config:/data -e URL="$URL" alpine sh -c '
  echo DB_BACKEND=supabase > /data/multi-domain-clean.env
  echo SUPABASE_DB_URL="$URL" >> /data/multi-domain-clean.env
  echo SECRET_KEY=change-me-in-production >> /data/multi-domain-clean.env
  echo PIN_API_URL=http://pin_generator:5000 >> /data/multi-domain-clean.env
  echo GENERATE_ARTICLE_API_URL=http://articles-website-generator:5002 >> /data/multi-domain-clean.env
  echo WEBSITE_PARTS_API_URL=http://website-parts-generator:5003 >> /data/multi-domain-clean.env
  echo LLAMACPP_MANAGER_URL=http://llamacpp_manager:5004 >> /data/multi-domain-clean.env
'

docker compose -f docker-compose.hub.yml pull --ignore-pull-failures 2>/dev/null || true
docker compose -f docker-compose.hub.yml up -d
echo "Done. Admin UI: http://$(hostname -I | awk '{print $1}'):6001"
