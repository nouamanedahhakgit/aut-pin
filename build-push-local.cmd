@echo off
REM Build and push to Docker Hub - bypasses PowerShell execution policy
powershell -ExecutionPolicy Bypass -File "%~dp0build-push-local.ps1" %*
