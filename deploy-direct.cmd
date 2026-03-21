@echo off
REM Deploy direct from local - bypasses PowerShell execution policy
powershell -ExecutionPolicy Bypass -File "%~dp0deploy-direct.ps1" %*
