# GitHub CLI 수동 설치 가이드

## 현재 상태
- ✅ Git 설치 및 설정 완료 (didwk <didwk89@gmail.com>)
- ❌ GitHub CLI 미설치

## GitHub CLI 설치 방법

### 방법 1: 공식 웹사이트에서 다운로드 (권장)
1. https://cli.github.com/ 접속
2. "Download for Windows" 클릭
3. 다운로드된 .msi 파일 실행
4. 설치 완료 후 **새 PowerShell/명령 프롬프트 열기**

### 방법 2: Scoop 사용 (있는 경우)
```powershell
scoop install gh
```

### 방법 3: Chocolatey 사용 (있는 경우)
```cmd
choco install gh
```

## 설치 후 확인
새 명령 프롬프트에서:
```cmd
gh --version
```

## GitHub 인증
```cmd
gh auth login
```
- "GitHub.com" 선택
- "HTTPS" 선택
- 브라우저에서 인증 완료

## 설정 완료 확인
```cmd
python run_assistant.py github:check-setup
python run_assistant.py github:whoami
```

## 예상 결과
```json
{
  "git_installed": true,
  "gh_cli_installed": true,
  "git_configured": true,
  "gh_authenticated": true,
  "status": "ready",
  "git_user": {
    "name": "didwk",
    "email": "didwk89@gmail.com"
  },
  "github_user": {
    "login": "your_username",
    "name": "Your Name",
    "email": "didwk89@gmail.com"
  }
}
```

## 완료 후 사용 가능한 기능
- 저장소 생성/복제
- 코드 커밋/푸시
- GitHub 프로젝트 관리
- Claude Assistant GitHub 통합 기능