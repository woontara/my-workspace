#!/usr/bin/env python3
"""
Windows-specific Google Cloud test
"""

import subprocess
import os

def test_gcloud():
    gcloud_path = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
    
    print(f"Testing: {gcloud_path}")
    print(f"Exists: {os.path.exists(gcloud_path)}")
    
    if not os.path.exists(gcloud_path):
        print("Google Cloud SDK not found at expected location")
        return
    
    # Try to run version command
    try:
        # Use shell=True on Windows
        result = subprocess.run(f'"{gcloud_path}" version', 
                              shell=True, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:200]}...")
        print(f"Error: {result.stderr[:200]}...")
        
        if result.returncode == 0:
            print("SUCCESS: Google Cloud SDK is working!")
            
            # Test auth
            auth_result = subprocess.run(f'"{gcloud_path}" auth list', 
                                       shell=True, capture_output=True, text=True, timeout=15)
            
            if auth_result.returncode == 0 and auth_result.stdout.strip():
                print("AUTH: OK")
                
                # Test project
                proj_result = subprocess.run(f'"{gcloud_path}" config get-value project', 
                                           shell=True, capture_output=True, text=True, timeout=15)
                
                if proj_result.returncode == 0 and proj_result.stdout.strip():
                    project = proj_result.stdout.strip()
                    print(f"PROJECT: {project}")
                    
                    if project == 'superclaud':
                        print("🎉 SUPERCLAUD PROJECT READY!")
                    else:
                        print(f"⚠️ Wrong project: {project} (expected: superclaud)")
                else:
                    print("❌ No project set")
            else:
                print("❌ Not authenticated")
        else:
            print("❌ Google Cloud SDK not working properly")
            
    except Exception as e:
        print(f"Error testing gcloud: {e}")

if __name__ == '__main__':
    test_gcloud()