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
    exit /b
)
Q
:: === Elevated instance starts here ===
echo Running as admin.

:: Move to the script's folder
cd /d "%~dp0"
echo Current directory: %cd%

:: Run npm run build
echo Running npm run build...
:: (will only work if npm is in PATH for admin)
call npm run build

:: Check if the previous command failed
if %errorlevel% neq 0 (
    :: Optional: Change text color to Red on Black for visibility
    color 0C
    echo.
    echo  ================================================
    echo   ERROR: An error occurred during the build.
    echo   Check that you have nodejs intalled -----------        nodejs.org/en/download
    echo  ================================================
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo Build finished successfully.
pause
