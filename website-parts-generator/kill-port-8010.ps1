# Free port 8010 (Windows). Run: .\kill-port-8010.ps1
$port = 8010
$found = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($found) {
    $found | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Write-Host "Stopped process(es) using port $port. You can now start website-parts-generator."
} else {
    Write-Host "No process found on port $port."
}
