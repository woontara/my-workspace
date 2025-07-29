@echo off
echo 🔧 Google Cloud SDK PATH 수정 스크립트
echo.

REM Common Google Cloud SDK installation paths
set "GCLOUD_PATH1=C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
set "GCLOUD_PATH2=%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
set "GCLOUD_PATH3=C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"

echo 📍 Google Cloud SDK 설치 위치 찾는 중...

if exist "%GCLOUD_PATH1%\gcloud.cmd" (
    echo ✅ 발견: %GCLOUD_PATH1%
    set "FOUND_PATH=%GCLOUD_PATH1%"
    goto :found
)

if exist "%GCLOUD_PATH2%\gcloud.cmd" (
    echo ✅ 발견: %GCLOUD_PATH2%
    set "FOUND_PATH=%GCLOUD_PATH2%"
    goto :found
)

if exist "%GCLOUD_PATH3%\gcloud.cmd" (
    echo ✅ 발견: %GCLOUD_PATH3%
    set "FOUND_PATH=%GCLOUD_PATH3%"
    goto :found
)

echo ❌ Google Cloud SDK를 찾을 수 없습니다.
echo 다음 중 하나를 시도해보세요:
echo 1. 재설치: GoogleCloudSDKInstaller.exe
echo 2. 수동 PATH 추가
echo 3. 시스템 재부팅
pause
exit /b 1

:found
echo.
echo 🎯 SuperClaud 프로젝트 설정 중...
echo.

REM Add to PATH temporarily
set "PATH=%FOUND_PATH%;%PATH%"

echo 🔐 Google Cloud 인증...
"%FOUND_PATH%\gcloud.cmd" auth login

echo.
echo 📋 SuperClaud 프로젝트 설정...
"%FOUND_PATH%\gcloud.cmd" config set project superclaud

echo.
echo 🌏 서울 리전 설정...
"%FOUND_PATH%\gcloud.cmd" config set compute/region asia-northeast3
"%FOUND_PATH%\gcloud.cmd" config set compute/zone asia-northeast3-a

echo.
echo 📊 설정 확인:
"%FOUND_PATH%\gcloud.cmd" config list

echo.
echo ✅ SuperClaud 프로젝트 연동 완료!
echo.
echo 📋 프로젝트 정보:
echo   - 프로젝트 ID: superclaud
echo   - 프로젝트 번호: 227137013364
echo   - 리전: asia-northeast3 (서울)
echo.
echo 🔧 PATH 영구 추가를 위해 시스템을 재부팅하거나
echo    새 명령 프롬프트를 열어주세요.
echo.
pause