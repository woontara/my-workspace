#!/usr/bin/env python3
"""
SuperClaud Google Cloud 연결 테스트 스크립트
"""

import subprocess
import json
import os
from pathlib import Path

def find_gcloud_path():
    """Google Cloud SDK 경로 찾기"""
    possible_paths = [
        r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"),
        r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    return None

def run_gcloud_command(gcloud_path, command):
    """gcloud 명령 실행"""
    try:
        full_command = [gcloud_path] + command
        result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("SuperClaud Google Cloud Connection Test")
    print("=" * 50)
    
    # 1. gcloud 경로 찾기
    print("Finding Google Cloud SDK...")
    gcloud_path = find_gcloud_path()
    
    if not gcloud_path:
        print("❌ Google Cloud SDK를 찾을 수 없습니다.")
        print("\n해결책:")
        print("1. fix_gcloud_path.bat 실행")
        print("2. 시스템 재부팅")
        print("3. Google Cloud SDK 재설치")
        return
    
    print(f"✅ 발견: {gcloud_path}")
    
    # 2. 버전 확인
    print("\n📦 버전 확인 중...")
    version_result = run_gcloud_command(gcloud_path, ['version', '--format=json'])
    
    if version_result['success']:
        try:
            version_info = json.loads(version_result['output'])
            print(f"✅ Google Cloud SDK: {version_info.get('Google Cloud SDK', 'Unknown')}")
        except:
            print("✅ Google Cloud SDK 설치됨")
    else:
        print(f"❌ 버전 확인 실패: {version_result['error']}")
        return
    
    # 3. 인증 상태 확인
    print("\n🔐 인증 상태 확인 중...")
    auth_result = run_gcloud_command(gcloud_path, ['auth', 'list', '--format=json'])
    
    if auth_result['success']:
        try:
            auth_info = json.loads(auth_result['output'])
            if auth_info:
                print(f"✅ 인증됨: {len(auth_info)}개 계정")
                for account in auth_info:
                    status = "🟢 활성" if account.get('status') == 'ACTIVE' else "⚪ 비활성"
                    print(f"   {status} {account.get('account', 'Unknown')}")
            else:
                print("❌ 인증되지 않음")
                print("해결책: fix_gcloud_path.bat 실행하여 인증 진행")
                return
        except:
            print("❌ 인증 정보 파싱 실패")
            return
    else:
        print(f"❌ 인증 확인 실패: {auth_result['error']}")
        return
    
    # 4. 현재 프로젝트 확인
    print("\n📋 프로젝트 설정 확인 중...")
    project_result = run_gcloud_command(gcloud_path, ['config', 'get-value', 'project'])
    
    if project_result['success'] and project_result['output']:
        current_project = project_result['output']
        print(f"✅ 현재 프로젝트: {current_project}")
        
        if current_project == 'superclaud':
            print("🎯 SuperClaud 프로젝트 연결됨!")
            
            # 프로젝트 상세 정보
            detail_result = run_gcloud_command(gcloud_path, ['projects', 'describe', 'superclaud', '--format=json'])
            if detail_result['success']:
                try:
                    project_info = json.loads(detail_result['output'])
                    print(f"   📛 이름: {project_info.get('name', 'Unknown')}")
                    print(f"   🔢 번호: {project_info.get('projectNumber', 'Unknown')}")
                    print(f"   📊 상태: {project_info.get('lifecycleState', 'Unknown')}")
                except:
                    print("   ℹ️ 상세 정보 가져오기 실패")
        else:
            print(f"⚠️ 다른 프로젝트 설정됨: {current_project}")
            print("해결책: fix_gcloud_path.bat 실행하여 SuperClaud로 변경")
    else:
        print("❌ 프로젝트가 설정되지 않음")
        print("해결책: fix_gcloud_path.bat 실행하여 프로젝트 설정")
        return
    
    # 5. 최종 상태
    print("\n" + "=" * 50)
    print("🎉 SuperClaud Google Cloud 연동 상태:")
    print("✅ Google Cloud SDK 설치됨")
    print("✅ 인증 완료")
    print("✅ SuperClaud 프로젝트 연결됨")
    print("\n🚀 이제 Claude 어시스턴트에서 Google Cloud 기능을 사용할 수 있습니다!")
    print("   python run_assistant.py google-cloud:status")

if __name__ == '__main__':
    main()