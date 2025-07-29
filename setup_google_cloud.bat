@echo off
echo 🚀 Google Cloud SDK 설치 및 설정 스크립트
echo.

REM Check if installer exists
if not exist "GoogleCloudSDKInstaller.exe" (
    echo ❌ GoogleCloudSDKInstaller.exe 파일이 없습니다.
    echo 다운로드 중...
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
)

echo 📦 Google Cloud SDK 설치 중...
echo 브라우저가 열리면 설치를 진행해주세요.
start /wait GoogleCloudSDKInstaller.exe

echo.
echo ✅ 설치가 완료되었습니다.
echo.
echo 🔧 다음 단계:
echo 1. 새 명령 프롬프트를 열어주세요 (현재 창 닫고)
echo 2. 다음 명령어로 인증하세요:
echo    gcloud auth login
echo.
echo 3. 프로젝트 설정:
echo    gcloud config set project superclaud
echo.
echo 4. 확인:
echo    gcloud config list
echo.
pause