#!/bin/bash
# Build and push all aut-pin images to Docker Hub from local (bypass GitHub Actions rate limit)
# Usage: ./build-push-local.sh [SERVICE]
#   No args = build all services
#   SERVICE = orchestrator|multi-domain-clean|pin_generator|articles-website-generator|website-parts-generator|llamacpp_manager|updater
#
# Prerequisites: docker login -u boarddash31 (or your username)
# Set DOCKERHUB_USERNAME if different from boarddash31

set -e
USERNAME="${DOCKERHUB_USERNAME:-boarddash31}"
TAG="${TAG:-latest}"

SERVICES=(
  "orchestrator:./orchestrator:./orchestrator/Dockerfile:aut-pin-orchestrator"
  "multi-domain-clean:./multi-domain-clean:./multi-domain-clean/Dockerfile:aut-pin-multi-domain-clean"
  "pin_generator:.:./pin_generator/Dockerfile:aut-pin-pin_generator"
  "articles-website-generator:.:./articles-website-generator/Dockerfile:aut-pin-articles-website-generator"
  "website-parts-generator:./website-parts-generator:./website-parts-generator/Dockerfile:aut-pin-website-parts-generator"
  "llamacpp_manager:.:./llamacpp_manager/Dockerfile:aut-pin-llamacpp_manager"
  "updater:./multi-domain-clean/updater:./multi-domain-clean/updater/Dockerfile:aut-pin-updater"
)

build_one() {
  local name="$1" ctx="$2" df="$3" img="$4"
  echo ">>> Building $name ($USERNAME/$img:$TAG)"
  docker build -f "$df" -t "$USERNAME/$img:$TAG" "$ctx"
  echo ">>> Pushing $USERNAME/$img:$TAG"
  docker push "$USERNAME/$img:$TAG"
  echo ">>> Done $name"
}

if [ -n "$1" ]; then
  for s in "${SERVICES[@]}"; do
    IFS=':' read -r name ctx df img <<< "$s"
    if [ "$name" = "$1" ]; then
      build_one "$name" "$ctx" "$df" "$img"
      exit 0
    fi
  done
  echo "Unknown service: $1. Use: orchestrator|multi-domain-clean|pin_generator|articles-website-generator|website-parts-generator|llamacpp_manager|updater"
  exit 1
fi

for s in "${SERVICES[@]}"; do
  IFS=':' read -r name ctx df img <<< "$s"
  build_one "$name" "$ctx" "$df" "$img"
done

echo ""
echo "All images pushed. Deploy with:"
echo "  ssh root@72.61.197.144 \"export DOCKERHUB_TOKEN='...' && ... curl deploy-supabase.sh | bash\""
echo "  Or use Update button in admin UI at http://72.61.197.144:6001/admin/updates"
