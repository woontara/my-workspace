@echo off
echo GitHub Setup Script for SuperClaud
echo ====================================

echo Step 1: Git Configuration Check
git config --global --list
echo.

echo Step 2: Downloading GitHub CLI
echo Please download GitHub CLI manually from:
echo https://cli.github.com/
echo.
echo Or use winget (if available):
winget install --id GitHub.cli

echo.
echo Step 3: After GitHub CLI installation
echo Open a NEW command prompt and run:
echo gh auth login
echo.
echo Step 4: Test GitHub integration
echo python run_assistant.py github:check-setup
echo python run_assistant.py github:whoami
echo.
pause