#!/usr/bin/env python3
"""
Simple Google Cloud SDK check for SuperClaud project
"""

import subprocess
import os
from pathlib import Path

def find_gcloud():
    """Find gcloud executable"""
    paths = [
        r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"),
        r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    ]
    
    for path in paths:
        if Path(path).exists():
            return path
    return None

def run_cmd(gcloud_path, args):
    """Run gcloud command"""
    try:
        result = subprocess.run([gcloud_path] + args, 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except:
        return False, "", "Command failed"

def main():
    print("SuperClaud Google Cloud Check")
    print("-" * 30)
    
    # Find gcloud
    gcloud = find_gcloud()
    if not gcloud:
        print("ERROR: Google Cloud SDK not found")
        print("Solution: Run fix_gcloud_path.bat")
        return
    
    print(f"FOUND: {gcloud}")
    
    # Check version
    success, out, err = run_cmd(gcloud, ['version'])
    if not success:
        print("ERROR: Cannot run gcloud")
        return
    
    print("VERSION: OK")
    
    # Check auth
    success, out, err = run_cmd(gcloud, ['auth', 'list'])
    if not success or not out.strip():
        print("ERROR: Not authenticated")
        print("Solution: Run fix_gcloud_path.bat")
        return
    
    print("AUTH: OK")
    
    # Check project
    success, out, err = run_cmd(gcloud, ['config', 'get-value', 'project'])
    if not success or not out.strip():
        print("ERROR: No project set")
        print("Solution: Run fix_gcloud_path.bat")
        return
    
    current_project = out.strip()
    print(f"PROJECT: {current_project}")
    
    if current_project == 'superclaud':
        print("SUCCESS: SuperClaud project connected!")
        print("Ready to use Google Cloud features!")
    else:
        print(f"WARNING: Different project set: {current_project}")
        print("Expected: superclaud")
        print("Solution: Run fix_gcloud_path.bat")

if __name__ == '__main__':
    main()