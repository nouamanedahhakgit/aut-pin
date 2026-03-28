@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   Remote Supabase deploy
echo   Server: root@72.61.197.144
echo   Script: aut-pin/main/deploy-supabase.sh (GitHub raw)
echo ============================================================
echo.

rem --- Connection string: env var OR one-line file (not committed) ---
if not defined SUPABASE_DB_URL (
  if exist "%~dp0supabase-url.local.env" (
    for /f "usebackq delims=" %%L in ("%~dp0supabase-url.local.env") do set "SUPABASE_DB_URL=%%L"
  )
)

if not defined SUPABASE_DB_URL (
  echo [ERROR] SUPABASE_DB_URL is not set.
  echo.
  echo   Option A — in this CMD window, then run this script again:
  echo     set SUPABASE_DB_URL=postgresql://USER:PASS@HOST:5432/postgres
  echo.
  echo   Option B — copy supabase-url.local.env.example to supabase-url.local.env
  echo     and put your URL on one line (no quotes).
  echo.
  exit /b 1
)

echo [OK] Using SUPABASE_DB_URL from environment or supabase-url.local.env
echo.
echo [1/2] SSH reachability (15s timeout^)...
ssh -o ConnectTimeout=15 -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@72.61.197.144 "echo ssh_ok" 2>nul
if errorlevel 1 (
  echo [WARN] SSH quick check failed — wrong key, firewall, or host down.
  echo        Continuing anyway; you may be prompted for a password.
  echo.
) else (
  echo [OK] SSH is reachable.
  echo.
)

echo [2/2] Running remote deploy (all output from the server is below^)
echo ------------------------------------------------------------

rem Single-quoted value on the remote shell avoids most bash metachar issues.
ssh -tt root@72.61.197.144 "export SUPABASE_DB_URL='!SUPABASE_DB_URL!' && curl -sSL https://raw.githubusercontent.com/nouamanedahhakgit/aut-pin/main/deploy-supabase.sh | bash"
set "REMOTE_RC=!errorlevel!"

echo ------------------------------------------------------------
if !REMOTE_RC! neq 0 (
  echo.
  echo [FAILED] Remote script exited with code !REMOTE_RC!
  echo          Fix errors above, then run this batch again.
  echo.
  endlocal
  exit /b !REMOTE_RC!
)

echo.
echo [SUCCESS] Remote deploy finished with exit code 0.
echo.
endlocal
exit /b 0
