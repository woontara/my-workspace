#!/usr/bin/env python3
"""
GitHub 인증 상태 확인 스크립트
"""

import subprocess
import json

def test_gh_auth():
    """GitHub CLI 인증 상태 테스트"""
    
    print("GitHub CLI 인증 테스트")
    print("=" * 30)
    
    # GitHub CLI 버전 확인
    try:
        result = subprocess.run(['gh', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ GitHub CLI 설치됨")
            print(f"   버전: {result.stdout.split()[2]}")
        else:
            print("❌ GitHub CLI 실행 실패")
            return
    except Exception as e:
        print(f"❌ GitHub CLI 확인 실패: {e}")
        return
    
    # 인증 상태 확인
    try:
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ GitHub 인증 완료")
            print("   인증 정보:")
            for line in result.stderr.split('\n'):  # gh auth status는 stderr로 출력
                if line.strip():
                    print(f"   {line.strip()}")
        else:
            print("❌ GitHub 인증 필요")
            print("다음 명령어를 실행하세요:")
            print("   gh auth login")
            return
    
    except Exception as e:
        print(f"❌ 인증 상태 확인 실패: {e}")
        return
    
    # 사용자 정보 확인
    try:
        result = subprocess.run(['gh', 'api', 'user'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            user_info = json.loads(result.stdout)
            print("✅ GitHub 사용자 정보:")
            print(f"   사용자명: {user_info.get('login', 'Unknown')}")
            print(f"   이름: {user_info.get('name', 'Unknown')}")
            print(f"   이메일: {user_info.get('email', 'Unknown')}")
            print(f"   저장소: {user_info.get('public_repos', 0)}개")
            
            print("\n🎉 GitHub 연동 완료!")
            print("이제 Claude Assistant GitHub 기능을 사용할 수 있습니다:")
            print("   python run_assistant.py github:list-repos")
            print("   python run_assistant.py github:create-repo test-repo")
            
        else:
            print("⚠️ 사용자 정보 가져오기 실패")
            print("인증이 완료되었지만 API 접근에 문제가 있을 수 있습니다.")
    
    except Exception as e:
        print(f"❌ 사용자 정보 확인 실패: {e}")

if __name__ == '__main__':
    test_gh_auth()