@echo off
:: ── startapp.bat ──────────────────────────────────────────────────────────────
:: Starts the full NovaCart app (backend + frontend) for local development.
:: 1. Launches the backend in a new window
:: 2. Polls /health until the backend is ready (max 60 s)
:: 3. Launches the frontend in a new window
:: ─────────────────────────────────────────────────────────────────────────────

:: ── Kill any existing backend (by port AND process name) ─────────────────────
echo Stopping any existing backend...

:: Close the existing "NovaCart Backend" console window if open
taskkill /FI "WINDOWTITLE eq NovaCart Backend" /F >nul 2>&1

:: Kill any uvicorn process still holding port 8000
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)

:: Kill any lingering uvicorn processes by name
taskkill /IM uvicorn.exe /F >nul 2>&1

:: Wait for OS to fully release the port (TIME_WAIT can hold it for several seconds)
timeout /t 4 /nobreak >nul

echo Starting NovaCart backend in a new window...
start "NovaCart Backend" /d "%~dp0backend" /b cmd /c "startbackend.bat"

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
start "NovaCart Frontend" /d "%~dp0frontend" /b cmd /c "startfrontend.bat"

echo Both servers are starting. You can close this window.
