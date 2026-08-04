@echo off
:: ── startfrontend.bat ─────────────────────────────────────────────────────────
:: Starts the NovaCart frontend dev server on http://127.0.0.1:3000
:: 1. Checks Node.js is installed — installs via winget if missing
:: 2. Runs npm install only when package.json has changed
:: 3. Starts the Vite dev server
:: ─────────────────────────────────────────────────────────────────────────────

:: Pin all paths to the script's own directory so this bat works correctly
:: regardless of what CWD the caller set (e.g. double-clicked from anywhere).
set HERE=%~dp0
if "%HERE:~-1%"=="\" set HERE=%HERE:~0,-1%

:: All diagnostic output is also written to a log file next to this script.
set LOG=%HERE%\startfrontend.log
echo. > "%LOG%"
echo [%DATE% %TIME%] startfrontend.bat starting >> "%LOG%"

call :log "[DIAG] Script location  : %HERE%"
call :log "[DIAG] Working directory: %CD%"

if exist "%HERE%\package.json" (
    call :log "[DIAG] package.json      : FOUND"
) else (
    call :log "[DIAG] package.json      : NOT FOUND"
    call :log " ERROR: Cannot continue without package.json"
    pause
    exit /b 1
)

:: ── 1. Check / install Node.js ───────────────────────────────────────────────
call :log "Checking for Node.js..."

for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYS_PATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USR_PATH=%%B"
if defined USR_PATH (set "PATH=%SYS_PATH%;%USR_PATH%") else (set "PATH=%SYS_PATH%")

node --version >nul 2>&1
if errorlevel 1 (
    call :log "Node.js not found. Attempting to install via winget..."
    winget --version >nul 2>&1
    if errorlevel 1 (
        call :log " ERROR: winget not available. Install Node.js from https://nodejs.org/"
        pause
        exit /b 1
    )
    winget install OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
    for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYS_PATH=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USR_PATH=%%B"
    if defined USR_PATH (set "PATH=%SYS_PATH%;%USR_PATH%") else (set "PATH=%SYS_PATH%")
    node --version >nul 2>&1
    if errorlevel 1 (
        call :log " ERROR: Node.js still not found after install."
        pause
        exit /b 1
    )
    call :log "  Node.js installed successfully."
) else (
    call :log "  Node.js OK"
)

for /f %%V in ('node --version 2^>^&1') do call :log "[DIAG] node version: %%V"
for /f %%V in ('npm --version 2^>^&1')  do call :log "[DIAG] npm  version: %%V"

:: ── 2. Run npm install only if needed ────────────────────────────────────────
call :log "Checking dependencies..."

if not exist "%HERE%\node_modules\" (
    call :log "[DIAG] node_modules absent -- running npm install"
    goto :do_install
)

set STAMP=%HERE%\node_modules\.package.stamp
if not exist "%STAMP%" (
    call :log "[DIAG] stamp file absent -- running npm install"
    goto :do_install
)

fc /b "%HERE%\package.json" "%STAMP%" >nul 2>&1
if errorlevel 1 (
    call :log "[DIAG] package.json changed -- running npm install"
    goto :do_install
)

call :log "  Dependencies up to date, skipping install."
goto :start

:do_install
call :log "[DIAG] npm install starting in %HERE%"
cd /d "%HERE%"
:: Run npm install in a sub-shell so a non-zero exit code (npm 11.x emits
:: exit 1 for funding/allow-scripts warnings on success) cannot propagate
:: up and kill the parent cmd /k session.
cmd /c "npm install --no-audit"
copy /y "%HERE%\package.json" "%STAMP%" >nul
call :log "  npm install done -- proceeding to start"

:start
call :log "[DIAG] Reached :start -- launching Vite dev server"
cd /d "%HERE%"
echo.
echo Starting NovaCart frontend at http://127.0.0.1:3000
echo Press Ctrl+C to stop.
echo Log file: %LOG%
echo.
call :log "[DIAG] Calling npm start..."
npm start
set NPM_START_ERR=%errorlevel%
call :log "[DIAG] npm start exited with code: %NPM_START_ERR%"
if %NPM_START_ERR% neq 0 (
    echo.
    echo  ERROR: npm start failed ^(exit code %NPM_START_ERR%^). Check %LOG% for details.
)
pause
exit /b %NPM_START_ERR%

:: ── helper: echo to console AND append to log ────────────────────────────────
:log
echo %~1
echo %~1 >> "%LOG%"
exit /b 0
