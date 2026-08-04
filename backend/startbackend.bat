@echo off
:: ── startbackend.bat ──────────────────────────────────────────────────────────
:: One-stop local dev runner for the NovaCart backend.
:: 1. Checks Python 3.11 is installed
:: 2. Creates /venv/ if it doesn't exist
:: 3. Installs requirements only when requirements.txt has changed
:: 4. Starts the FastAPI dev server on http://localhost:8000
:: ─────────────────────────────────────────────────────────────────────────────

:: Pin all relative paths to the script's own directory so this bat works
:: correctly regardless of what CWD the caller set.
set HERE=%~dp0
:: Strip trailing backslash so we can append cleanly.
if "%HERE:~-1%"=="\" set HERE=%HERE:~0,-1%

echo [DIAG] Script location  : %HERE%
echo [DIAG] Working directory: %CD%
echo [DIAG] requirements.txt :
if exist "%HERE%\requirements.txt" (echo   FOUND) else (echo   NOT FOUND ^<-- problem^>)
echo.

:: ── 1. Check Python 3.11 ─────────────────────────────────────────────────────
echo Checking for Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python 3.11 is not installed.
    echo  Run the following command to install it:
    echo.
    echo    winget install Python.Python.3.11
    echo.
    echo  Then re-run this script.
    pause
    exit /b 1
)
echo   OK

:: ── 2. Create venv if missing ─────────────────────────────────────────────────
if not exist "%HERE%\venv\Scripts\activate" (
    echo Creating virtual environment with Python 3.11...
    py -3.11 -m venv "%HERE%\venv"
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   OK
) else (
    echo Virtual environment already exists.
)

:: ── 3. Install requirements only if requirements.txt has changed ──────────────
echo Checking requirements...
set STAMP=%HERE%\venv\.requirements.stamp

:: Compare current requirements.txt against the stamp from the last install.
:: fc /b does a binary comparison — exits 0 if identical, 1 if different/missing.
fc /b "%HERE%\requirements.txt" "%STAMP%" >nul 2>&1
if errorlevel 1 (
    echo Requirements changed or first run -- installing packages...
    "%HERE%\venv\Scripts\pip" install -q -r "%HERE%\requirements.txt"
    if errorlevel 1 (
        echo  ERROR: Failed to install requirements.
        pause
        exit /b 1
    )
    :: Save a copy of requirements.txt as the new stamp
    copy /y "%HERE%\requirements.txt" "%STAMP%" >nul
    echo   OK
) else (
    echo   Requirements up to date, skipping install.
)

:: ── 4. Start the server ───────────────────────────────────────────────────────
echo.
echo Starting NovaCart backend at http://localhost:8000
echo Press Ctrl+C to stop.
echo.
call "%HERE%\venv\Scripts\activate"
cd /d "%HERE%"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
