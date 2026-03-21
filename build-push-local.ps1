# Build and push all aut-pin images to Docker Hub from local (bypass GitHub Actions rate limit)
# Usage: .\build-push-local.ps1 [SERVICE]
#   No args = build all services
#   SERVICE = orchestrator|multi-domain-clean|pin_generator|articles-website-generator|website-parts-generator|llamacpp_manager|updater
#
# Prerequisites: docker login -u boarddash31
# Set $env:DOCKERHUB_USERNAME if different from boarddash31

$ErrorActionPreference = "Stop"
$Username = if ($env:DOCKERHUB_USERNAME) { $env:DOCKERHUB_USERNAME } else { "boarddash31" }
$Tag = if ($env:TAG) { $env:TAG } else { "latest" }

$Services = @(
    @{ Name = "orchestrator"; Context = "./orchestrator"; Dockerfile = "./orchestrator/Dockerfile"; Image = "aut-pin-orchestrator" }
    @{ Name = "multi-domain-clean"; Context = "./multi-domain-clean"; Dockerfile = "./multi-domain-clean/Dockerfile"; Image = "aut-pin-multi-domain-clean" }
    @{ Name = "pin_generator"; Context = "."; Dockerfile = "./pin_generator/Dockerfile"; Image = "aut-pin-pin_generator" }
    @{ Name = "articles-website-generator"; Context = "."; Dockerfile = "./articles-website-generator/Dockerfile"; Image = "aut-pin-articles-website-generator" }
    @{ Name = "website-parts-generator"; Context = "./website-parts-generator"; Dockerfile = "./website-parts-generator/Dockerfile"; Image = "aut-pin-website-parts-generator" }
    @{ Name = "llamacpp_manager"; Context = "."; Dockerfile = "./llamacpp_manager/Dockerfile"; Image = "aut-pin-llamacpp_manager" }
    @{ Name = "updater"; Context = "./multi-domain-clean/updater"; Dockerfile = "./multi-domain-clean/updater/Dockerfile"; Image = "aut-pin-updater" }
)

function Build-One {
    param($s)
    Write-Host ">>> Building $($s.Name) ($Username/$($s.Image):$Tag)"
    docker build -f $s.Dockerfile -t "$Username/$($s.Image):$Tag" $s.Context
    Write-Host ">>> Pushing $Username/$($s.Image):$Tag"
    docker push "$Username/$($s.Image):$Tag"
    Write-Host ">>> Done $($s.Name)"
}

$target = $args[0]
if ($target) {
    $found = $Services | Where-Object { $_.Name -eq $target }
    if ($found) {
        Build-One $found
    } else {
        Write-Host "Unknown service: $target. Use: orchestrator|multi-domain-clean|pin_generator|articles-website-generator|website-parts-generator|llamacpp_manager|updater"
        exit 1
    }
} else {
    foreach ($s in $Services) {
        Build-One $s
    }
}

Write-Host ""
Write-Host "All images pushed. Deploy with the deploy command or Update button in admin UI."
