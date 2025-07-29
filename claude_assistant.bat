@echo off
REM Claude Code Assistant - Windows Launcher
REM This script launches the Claude Code Assistant with proper Python environment

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+ and add it to PATH.
    echo You can download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Claude Code is installed
claude --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Claude Code not found! Please install Claude Code CLI.
    echo Visit: https://docs.anthropic.com/claude-code
    pause
    exit /b 1
)

REM Display banner
echo.
echo 🚀 Starting Claude Code Assistant...
echo 📂 Working directory: %SCRIPT_DIR%
echo.

REM Run the assistant
python "%SCRIPT_DIR%run_assistant.py" %*

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo ❌ Assistant exited with error code %errorlevel%
    pause
)

endlocal