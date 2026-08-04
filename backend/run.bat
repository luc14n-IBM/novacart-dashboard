@echo off
:: ── run.bat ───────────────────────────────────────────────────────────────────
:: One-stop local dev runner for the NovaCart backend.
:: 1. Checks Python 3.11 is installed
:: 2. Creates /venv/ if it doesn't exist
:: 3. Installs requirements if not already installed
:: 4. Starts the FastAPI dev server on http://localhost:8000
:: ─────────────────────────────────────────────────────────────────────────────

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
if not exist "venv\Scripts\activate" (
    echo Creating virtual environment with Python 3.11...
    py -3.11 -m venv venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   OK
) else (
    echo Virtual environment already exists.
)

:: ── 3. Install / sync requirements ───────────────────────────────────────────
echo Checking requirements...
venv\Scripts\pip install -q -r requirements.txt
if errorlevel 1 (
    echo  ERROR: Failed to install requirements.
    pause
    exit /b 1
)
echo   OK

:: ── 4. Start the server ───────────────────────────────────────────────────────
echo.
echo Starting NovaCart backend at http://localhost:8000
echo Press Ctrl+C to stop.
echo.
call venv\Scripts\activate
uvicorn main:app --reload --port 8000
