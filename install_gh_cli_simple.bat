@echo off
echo Installing GitHub CLI...
echo.

REM Try winget first (if available)
echo Attempting winget installation...
winget install --id GitHub.cli --accept-source-agreements --accept-package-agreements
echo.

REM Check if installation was successful
gh --version >nul 2>&1
if %errorlevel% == 0 (
    echo GitHub CLI installed successfully!
    echo.
    echo Next steps:
    echo 1. Run: gh auth login
    echo 2. Test: python run_assistant.py github:check-setup
    echo.
) else (
    echo GitHub CLI installation may have failed.
    echo Please try manual installation from: https://cli.github.com/
    echo.
)

pause