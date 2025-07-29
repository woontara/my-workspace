@echo off
echo ===============================================
echo SuperClaud GitHub Integration Setup
echo ===============================================

echo.
echo Current Git Configuration:
git config --global --list
echo.

echo Step 1: Download GitHub CLI
echo Opening GitHub CLI download page...
start https://cli.github.com/

echo.
echo Step 2: Manual Installation Instructions
echo 1. Download the .msi installer from the opened page
echo 2. Run the installer
echo 3. Restart this command prompt after installation
echo.

echo Step 3: Authentication (after installing GitHub CLI)
echo Run these commands in a NEW command prompt:
echo.
echo   gh auth login
echo   python run_assistant.py github:whoami
echo   python run_assistant.py github:check-setup
echo.

echo Step 4: Test Complete Integration
echo   python run_assistant.py github:list-repos
echo   python run_assistant.py github:create-repo test-superclaud "Test repository for SuperClaud"
echo.

echo ===============================================
echo GitHub CLI Download:  https://cli.github.com/
echo ===============================================
pause