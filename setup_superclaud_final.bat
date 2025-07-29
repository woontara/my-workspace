@echo off
echo SuperClaud Google Cloud Setup
echo ===============================

REM Set the correct path
set "GCLOUD_PATH=%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
set "PATH=%GCLOUD_PATH%;%PATH%"

echo Found Google Cloud SDK at: %GCLOUD_PATH%
echo.

echo Step 1: Authentication
echo Opening browser for login...
"%GCLOUD_PATH%\gcloud.cmd" auth login

echo.
echo Step 2: Set SuperClaud project
"%GCLOUD_PATH%\gcloud.cmd" config set project superclaud

echo.
echo Step 3: Set Seoul region
"%GCLOUD_PATH%\gcloud.cmd" config set compute/region asia-northeast3
"%GCLOUD_PATH%\gcloud.cmd" config set compute/zone asia-northeast3-a

echo.
echo Step 4: Verify setup
"%GCLOUD_PATH%\gcloud.cmd" config list

echo.
echo SuperClaud Project Setup Complete!
echo Project ID: superclaud
echo Project Number: 227137013364
echo Region: Seoul (asia-northeast3)
echo.
echo Now you can use: python run_assistant.py google-cloud:status
pause