@echo off
setlocal EnableExtensions DisableDelayedExpansion
title PIXIE — Cute Edition (Web UI)

REM Change to the directory of this script
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Prefer the bundled virtual environment if available
set "VENV_PY=%SCRIPT_DIR%pixie-env\Scripts\python.exe"
if exist "%VENV_PY%" (
    "%VENV_PY%" "eel_app.py"
    goto :end
)

REM Try the Python launcher (Windows)
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "eel_app.py"
    goto :end
)

REM Fallback to python on PATH
where python >nul 2>nul
if %errorlevel%==0 (
    python "eel_app.py"
    goto :end
)

echo Could not find Python. Please install Python 3.8+ or use the bundled pixie-env.
pause

:end
popd
endlocal


