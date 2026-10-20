@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===================================================
echo           StreamYT Downloader Launcher
echo ===================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.11+ from https://www.python.org/
    echo Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Check Node.js installation (Recommended for YouTube 403 Forbidden bypass)
where node >nul 2>nul
if %errorlevel% neq 0 (
    if not exist "C:\Program Files\nodejs\node.exe" (
        echo [WARNING] Node.js not detected on PATH.
        echo To prevent YouTube HTTP 403 Forbidden errors, installing Node.js is strongly recommended:
        echo Download from: https://nodejs.org/
        echo.
    )
)

:: 3. Setup Virtual Environment on first run
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] First-time setup detected.
    echo [INFO] Creating Python virtual environment in .venv ...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )

    echo [INFO] Installing required packages from requirements.txt ...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [INFO] Environment setup completed successfully!
    echo.
)

:: 4. Launch Streamlit Application
echo [INFO] Starting StreamYT Downloader on http://localhost:8501 ...
start "" ".venv\Scripts\python.exe" -m streamlit run app.py --server.port=8501 --server.headless=false

exit /b 0
