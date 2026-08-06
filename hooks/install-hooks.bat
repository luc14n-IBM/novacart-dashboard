@echo off
:: hooks/install-hooks.bat — installs the project Git hooks for Windows.
:: Run once after cloning:  hooks\install-hooks.bat

setlocal

:: Resolve repo root (two levels up from this script's location)
for /f "delims=" %%i in ('git rev-parse --show-toplevel') do set REPO_ROOT=%%i

set HOOKS_SRC=%REPO_ROOT%\hooks
set HOOKS_DST=%REPO_ROOT%\.git\hooks

echo.
echo Installing NovaCart Git hooks...

:: Git on Windows reads the pre-push hook as a shell script run by Git's
:: bundled bash (Git Bash / MINGW). Copy the shell script directly.
copy /Y "%HOOKS_SRC%\pre-push" "%HOOKS_DST%\pre-push" >nul

echo   [OK] pre-push hook installed
echo.
echo The hook runs backend (pytest) and frontend (Vitest) tests before
echo every "git push". To skip in an emergency: git push --no-verify
echo.

endlocal
