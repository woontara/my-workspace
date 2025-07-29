#!/usr/bin/env python3
"""
Direct Google Cloud test for SuperClaud
"""

import subprocess
import os
from pathlib import Path

def find_gcloud():
    """Find gcloud path"""
    paths = [
        r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"),
        r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    ]
    
    for path in paths:
        if Path(path).exists():
            return path
    return None

def run_gcloud(gcloud_path, args):
    """Run gcloud command"""
    try:
        result = subprocess.run([gcloud_path] + args, 
                              capture_output=True, text=True, timeout=15)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("=== SuperClaud Google Cloud Direct Test ===")
    
    # Find gcloud
    gcloud_path = find_gcloud()
    if not gcloud_path:
        print("ERROR: Google Cloud SDK not found")
        return
    
    print(f"GCLOUD PATH: {gcloud_path}")
    
    # Test version
    print("\n1. Testing version...")
    result = run_gcloud(gcloud_path, ['version'])
    if result['success']:
        print("SUCCESS: gcloud working")
        # Extract version info
        lines = result['output'].split('\n')
        for line in lines:
            if 'Google Cloud SDK' in line:
                print(f"VERSION: {line}")
                break
    else:
        print(f"ERROR: {result['error']}")
        return
    
    # Test auth
    print("\n2. Testing authentication...")
    result = run_gcloud(gcloud_path, ['auth', 'list', '--format=value(account)'])
    if result['success'] and result['output']:
        accounts = result['output'].split('\n')
        print(f"SUCCESS: {len(accounts)} account(s) authenticated")
        for account in accounts:
            if account.strip():
                print(f"  - {account.strip()}")
    else:
        print("ERROR: Not authenticated")
        print("Run: setup_superclaud_final.bat")
        return
    
    # Test project
    print("\n3. Testing project...")
    result = run_gcloud(gcloud_path, ['config', 'get-value', 'project'])
    if result['success'] and result['output']:
        project = result['output']
        print(f"CURRENT PROJECT: {project}")
        
        if project == 'superclaud':
            print("SUCCESS: SuperClaud project is set!")
            
            # Get project details
            print("\n4. Getting project details...")
            result = run_gcloud(gcloud_path, ['projects', 'describe', 'superclaud'])
            if result['success']:
                lines = result['output'].split('\n')
                for line in lines:
                    if 'name:' in line or 'projectNumber:' in line or 'lifecycleState:' in line:
                        print(f"  {line.strip()}")
            
            print("\n=== SUPERCLAUD GOOGLE CLOUD READY! ===")
            print("You can now use Google Cloud features:")
            print("- python run_assistant.py google-cloud:status")
            print("- python run_assistant.py google-cloud:list-projects")
            
        else:
            print(f"WARNING: Wrong project set: {project}")
            print("Expected: superclaud")
            print("Run: setup_superclaud_final.bat")
    else:
        print("ERROR: No project set")
        print("Run: setup_superclaud_final.bat")

if __name__ == '__main__':
    main()