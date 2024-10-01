@echo off
setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on this system.
    echo Please download and install Python 3.6 or later from https://www.python.org/downloads/
    echo Make sure to check the box that says "Add Python to PATH" during installation.
    echo After installing Python, please run this batch file again.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

REM Check Python version
for /f "tokens=2 delims=." %%a in ('python --version 2^>^&1') do set pyver=%%a
if %pyver% lss 6 (
    echo Your Python version is too old. Please install Python 3.6 or later.
    echo Current version: 
    python --version
    pause
    exit /b 1
)

REM Create and activate virtual environment
IF NOT EXIST venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
)

REM Run the Python script
python hcheck.py
pause