@echo off
:: ── startapp.bat ──────────────────────────────────────────────────────────────
:: Starts the full NovaCart app (backend + frontend) for local development.
:: 1. Launches the backend in a new window
:: 2. Polls /health until the backend is ready (max 60 s)
:: 3. Launches the frontend in a new window
:: ─────────────────────────────────────────────────────────────────────────────

:: ── Kill any existing backend ─────────────────────────────────────────────────
echo Stopping any existing backend...

:: Kill uvicorn and its entire process tree (reloader + server worker)
for /f "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq uvicorn.exe" /FO list ^| findstr "PID:"') do (
    taskkill /PID %%p /F /T >nul 2>&1
)

:: Wait for OS to release the port
timeout /t 3 /nobreak >nul

echo Starting NovaCart backend in a new window...
start "NovaCart Backend" /d "%~dp0backend" cmd /k "startbackend.bat"

:: ── Poll /health until backend responds ──────────────────────────────────────
echo Waiting for backend to be ready at http://127.0.0.1:8000/health ...
set RETRIES=0
set MAX_RETRIES=30

:wait_loop
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/health 2>nul | findstr /x "200" >nul
if not errorlevel 1 (
    echo   Backend is up!
    goto :launch_frontend
)
set /a RETRIES+=1
if %RETRIES% geq %MAX_RETRIES% (
    echo.
    echo  WARNING: Backend did not respond after 60 s. Starting frontend anyway.
    goto :launch_frontend
)
timeout /t 2 /nobreak >nul
goto :wait_loop

:launch_frontend
echo Starting NovaCart frontend in a new window...
start "NovaCart Frontend" /d "%~dp0frontend" cmd /k "startfrontend.bat"

echo Both servers are starting. You can close this window.
