# Deploy directly from local to server (no Docker Hub - faster)
# Usage: .\deploy-direct.ps1
#   $env:SERVER = "root@72.61.197.144" (default)
#   $env:SUPABASE_DB_URL = "postgresql://...:6543/postgres" (required — transaction pooler on servers)
#   $env:SUPABASE_POOL_MAX = "10" (optional)
#
# Builds images locally, transfers via SSH, runs compose on server.
# No docker login needed. No Docker Hub rate limits.

$ErrorActionPreference = "Stop"
$Server = if ($env:SERVER) { $env:SERVER } else { "root@72.61.197.144" }
$Username = if ($env:DOCKERHUB_USERNAME) { $env:DOCKERHUB_USERNAME } else { "boarddash31" }
$Tag = "latest"
$DbUrl = $env:SUPABASE_DB_URL
if (-not $DbUrl) {
    Write-Error "Set `$env:SUPABASE_DB_URL to your Supabase Postgres URI (use transaction pooler port 6543 on production)."
    exit 1
}
$PoolMax = if ($env:SUPABASE_POOL_MAX) { $env:SUPABASE_POOL_MAX } else { "12" }

$Services = @(
    @{ Name = "orchestrator"; Context = "./orchestrator"; Dockerfile = "./orchestrator/Dockerfile"; Image = "aut-pin-orchestrator" }
    @{ Name = "multi-domain-clean"; Context = "./multi-domain-clean"; Dockerfile = "./multi-domain-clean/Dockerfile"; Image = "aut-pin-multi-domain-clean" }
    @{ Name = "pin_generator"; Context = "."; Dockerfile = "./pin_generator/Dockerfile"; Image = "aut-pin-pin_generator" }
    @{ Name = "articles-website-generator"; Context = "."; Dockerfile = "./articles-website-generator/Dockerfile"; Image = "aut-pin-articles-website-generator" }
    @{ Name = "website-parts-generator"; Context = "./website-parts-generator"; Dockerfile = "./website-parts-generator/Dockerfile"; Image = "aut-pin-website-parts-generator" }
    @{ Name = "llamacpp_manager"; Context = "."; Dockerfile = "./llamacpp_manager/Dockerfile"; Image = "aut-pin-llamacpp_manager" }
    @{ Name = "updater"; Context = "./multi-domain-clean/updater"; Dockerfile = "./multi-domain-clean/updater/Dockerfile"; Image = "aut-pin-updater" }
)

Write-Host "=== Build and deploy to $Server (no Docker Hub) ===" -ForegroundColor Cyan

# 1. Build all images
foreach ($s in $Services) {
    Write-Host ">>> Building $($s.Name)" -ForegroundColor Yellow
    docker build -f $s.Dockerfile -t "$Username/$($s.Image):$Tag" $s.Context
}

# 2. Transfer images to server (docker save | ssh docker load)
foreach ($s in $Services) {
    $img = "$Username/$($s.Image):$Tag"
    Write-Host ">>> Transferring $img" -ForegroundColor Yellow
    docker save $img | ssh $Server "docker load"
}

# 3. Copy compose file
Write-Host ">>> Copying docker-compose.hub.yml" -ForegroundColor Yellow
scp docker-compose.hub.yml "${Server}:~/aut-pin/"

# 4. Setup env + run compose on server
$remote = @"
set -e
mkdir -p ~/aut-pin && cd ~/aut-pin
mkdir -p output/static-projects articles-website-generator/generators
docker volume create aut-pin_env-config 2>/dev/null || true
docker run --rm -v aut-pin_env-config:/data -e URL='$DbUrl' -e POOL_MAX='$PoolMax' alpine sh -c '
  echo DB_BACKEND=supabase > /data/multi-domain-clean.env
  echo SUPABASE_DB_URL="`$URL" >> /data/multi-domain-clean.env
  echo SUPABASE_POOL_MAX="`$POOL_MAX" >> /data/multi-domain-clean.env
  echo SECRET_KEY=change-me-in-production >> /data/multi-domain-clean.env
  echo PIN_API_URL=http://pin_generator:5000 >> /data/multi-domain-clean.env
  echo GENERATE_ARTICLE_API_URL=http://articles-website-generator:5002 >> /data/multi-domain-clean.env
  echo WEBSITE_PARTS_API_URL=http://website-parts-generator:5003 >> /data/multi-domain-clean.env
  echo LLAMACPP_MANAGER_URL=http://llamacpp_manager:5004 >> /data/multi-domain-clean.env
'
export DOCKERHUB_USERNAME=$Username
docker compose -f docker-compose.hub.yml up -d
echo Done. Admin: http://72.61.197.144:6001
"@

Write-Host ">>> Starting containers on server" -ForegroundColor Yellow
$remote | ssh $Server "bash -s"

Write-Host ""
Write-Host "Done. Admin: http://72.61.197.144:6001" -ForegroundColor Green
