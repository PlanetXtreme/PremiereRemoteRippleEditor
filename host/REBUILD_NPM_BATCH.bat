@echo off
:: === Script: elevate_and_build.bat ===
setlocal

:: Check if running as admin
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Not elevated. Requesting admin rights...
    :: Launch a new elevated instance of this same script
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    echo Exiting current non-elevated instance.
    :: pause
    exit /b
)

:: === Elevated instance starts here ===
echo Running as admin.

:: Move to the script's folder
cd /d "%~dp0"
echo Current directory: %cd%

:: Optional: run npm (will only work if npm is in PATH for admin)
echo Running npm run build...
npm run build

:: echo Done. Press any key to exit.
:: pause
