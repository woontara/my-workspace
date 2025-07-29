@echo off
echo 🌟 SuperClaud 프로젝트 설정 스크립트
echo.

REM Check if gcloud is installed
gcloud version >nul 2>&1
if errorlevel 1 (
    echo ❌ Google Cloud SDK가 설치되지 않았습니다.
    echo setup_google_cloud.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)

echo ✅ Google Cloud SDK 감지됨
echo.

echo 🔐 Google Cloud 인증 중...
gcloud auth login

echo.
echo 📋 프로젝트 설정 중: superclaud
gcloud config set project superclaud

echo.
echo 🌏 기본 리전 설정 (서울)
gcloud config set compute/region asia-northeast3
gcloud config set compute/zone asia-northeast3-a

echo.
echo 📊 현재 설정 확인:
gcloud config list

echo.
echo ✅ SuperClaud 프로젝트 설정 완료!
echo.
echo 📋 프로젝트 정보:
echo   - 프로젝트 ID: superclaud  
echo   - 프로젝트 번호: 227137013364
echo   - 리전: asia-northeast3 (서울)
echo.
echo 🚀 이제 Claude 어시스턴트에서 Google Cloud 명령어를 사용할 수 있습니다:
echo   python run_assistant.py google-cloud:status
echo.
pause