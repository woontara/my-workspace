#!/usr/bin/env python3
"""
Google Cloud Plugin for Claude Code Assistant
Provides integration with Google Cloud Platform services.
"""

import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from claude_assistant_plugins import Plugin

logger = logging.getLogger(__name__)

class GoogleCloudPlugin(Plugin):
    """Plugin for Google Cloud Platform integration"""
    
    @property
    def name(self) -> str:
        return "google-cloud"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Google Cloud Platform integration and project management"
    
    def initialize(self, assistant_context: Any) -> bool:
        self.context = assistant_context
        self.gcloud_installed = self._check_gcloud_installation()
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        return {
            'check-setup': self.check_setup,
            'auth-login': self.auth_login,
            'list-projects': self.list_projects,
            'set-project': self.set_project,
            'get-project': self.get_current_project,
            'create-project': self.create_project,
            'init-app-engine': self.init_app_engine,
            'deploy': self.deploy_app,
            'status': self.get_status,
            'setup-config': self.setup_config
        }
    
    def _check_gcloud_installation(self) -> bool:
        """Check if gcloud CLI is installed"""
        # Try standard command first
        try:
            result = subprocess.run(['gcloud', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try direct path lookup
        gcloud_path = self._find_gcloud_path()
        if gcloud_path:
            try:
                result = subprocess.run([gcloud_path, 'version'], 
                                      capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except:
                pass
        
        return False
    
    def _find_gcloud_path(self) -> str:
        """Find gcloud executable path"""
        import os
        from pathlib import Path
        
        possible_paths = [
            r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"),
            r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        return None
    
    def _run_gcloud_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run gcloud command and return result"""
        # Try standard gcloud command first
        try:
            full_command = ['gcloud'] + command
            result = subprocess.run(full_command, 
                                  capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout.strip(),
                    'error': result.stderr.strip(),
                    'command': ' '.join(full_command)
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try direct path
        gcloud_path = self._find_gcloud_path()
        if not gcloud_path:
            return {
                'success': False,
                'error': 'Google Cloud SDK not found',
                'command': ' '.join(['gcloud'] + command)
            }
        
        try:
            full_command = [gcloud_path] + command
            result = subprocess.run(full_command, 
                                  capture_output=True, text=True, timeout=timeout)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'command': ' '.join(full_command)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout}s',
                'command': ' '.join([gcloud_path] + command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join([gcloud_path] + command)
            }
    
    def check_setup(self) -> Dict[str, Any]:
        """Check Google Cloud setup status"""
        if not self.gcloud_installed:
            return {
                'gcloud_installed': False,
                'message': 'Google Cloud CLI not installed',
                'install_instructions': {
                    'windows': 'Run GoogleCloudSDKInstaller.exe',
                    'mac': 'brew install google-cloud-sdk',
                    'linux': 'curl https://sdk.cloud.google.com | bash'
                }
            }
        
        # Check authentication
        auth_result = self._run_gcloud_command(['auth', 'list', '--format=json'])
        
        # Check current project
        project_result = self._run_gcloud_command(['config', 'get-value', 'project'])
        
        return {
            'gcloud_installed': True,
            'authenticated': auth_result['success'] and auth_result['output'],
            'current_project': project_result['output'] if project_result['success'] else None,
            'auth_accounts': json.loads(auth_result['output']) if auth_result['success'] else [],
            'status': 'ready' if auth_result['success'] and project_result['output'] else 'needs_setup'
        }
    
    def auth_login(self) -> Dict[str, Any]:
        """Authenticate with Google Cloud"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        print("🔐 Opening browser for Google Cloud authentication...")
        result = self._run_gcloud_command(['auth', 'login'], timeout=120)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Successfully authenticated with Google Cloud',
                'next_steps': ['Set a project with: google-cloud:set-project PROJECT_ID']
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'troubleshooting': [
                    'Make sure you have internet connection',
                    'Check if your browser allows popups',
                    'Try running: gcloud auth login --no-browser'
                ]
            }
    
    def list_projects(self) -> Dict[str, Any]:
        """List all Google Cloud projects"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        result = self._run_gcloud_command(['projects', 'list', '--format=json'])
        
        if result['success']:
            try:
                projects = json.loads(result['output'])
                return {
                    'success': True,
                    'projects': projects,
                    'count': len(projects),
                    'formatted_list': [
                        f"{p['projectId']} - {p['name']} ({p['lifecycleState']})"
                        for p in projects
                    ]
                }
            except json.JSONDecodeError:
                return {'error': 'Failed to parse projects list'}
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestion': 'Try authenticating first with: google-cloud:auth-login'
            }
    
    def set_project(self, project_id: str) -> Dict[str, Any]:
        """Set current Google Cloud project"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        if not project_id:
            return {'error': 'Project ID is required'}
        
        result = self._run_gcloud_command(['config', 'set', 'project', project_id])
        
        if result['success']:
            return {
                'success': True,
                'message': f'Project set to: {project_id}',
                'project_id': project_id
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestions': [
                    'Check if project ID is correct',
                    'Verify you have access to this project',
                    'List available projects with: google-cloud:list-projects'
                ]
            }
    
    def get_current_project(self) -> Dict[str, Any]:
        """Get current Google Cloud project"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        result = self._run_gcloud_command(['config', 'get-value', 'project'])
        
        if result['success'] and result['output']:
            # Get project details
            project_info = self._run_gcloud_command([
                'projects', 'describe', result['output'], '--format=json'
            ])
            
            if project_info['success']:
                try:
                    details = json.loads(project_info['output'])
                    return {
                        'success': True,
                        'project_id': result['output'],
                        'project_name': details.get('name', 'Unknown'),
                        'project_number': details.get('projectNumber', 'Unknown'),
                        'status': details.get('lifecycleState', 'Unknown'),
                        'details': details
                    }
                except json.JSONDecodeError:
                    pass
            
            return {
                'success': True,
                'project_id': result['output'],
                'message': f'Current project: {result["output"]}'
            }
        else:
            return {
                'success': False,
                'message': 'No project set',
                'suggestion': 'Set a project with: google-cloud:set-project PROJECT_ID'
            }
    
    def create_project(self, project_id: str, project_name: str = None) -> Dict[str, Any]:
        """Create a new Google Cloud project"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        if not project_id:
            return {'error': 'Project ID is required'}
        
        command = ['projects', 'create', project_id]
        if project_name:
            command.extend(['--name', project_name])
        
        result = self._run_gcloud_command(command, timeout=60)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Project created: {project_id}',
                'project_id': project_id,
                'next_steps': [
                    f'Set as current project: google-cloud:set-project {project_id}',
                    'Enable required APIs for your use case',
                    'Set up billing if needed'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestions': [
                    'Project ID must be unique globally',
                    'Use only lowercase letters, numbers, and hyphens',
                    'Project ID must be 6-30 characters long'
                ]
            }
    
    def init_app_engine(self, region: str = 'asia-northeast3') -> Dict[str, Any]:
        """Initialize App Engine for current project"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        result = self._run_gcloud_command([
            'app', 'create', '--region', region
        ], timeout=120)
        
        if result['success']:
            return {
                'success': True,
                'message': f'App Engine initialized in region: {region}',
                'region': region,
                'next_steps': [
                    'Create app.yaml file for your application',
                    'Deploy with: google-cloud:deploy'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'available_regions': [
                    'asia-northeast3 (Seoul)',
                    'asia-northeast1 (Tokyo)', 
                    'us-central1 (Iowa)',
                    'europe-west1 (Belgium)'
                ]
            }
    
    def deploy_app(self, app_yaml: str = 'app.yaml') -> Dict[str, Any]:
        """Deploy application to App Engine"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        app_yaml_path = Path(app_yaml)
        if not app_yaml_path.exists():
            return {
                'error': f'app.yaml not found at: {app_yaml_path}',
                'suggestion': 'Create app.yaml file first or specify correct path'
            }
        
        print("🚀 Deploying to Google App Engine...")
        result = self._run_gcloud_command([
            'app', 'deploy', str(app_yaml_path), '--quiet'
        ], timeout=600)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Application deployed successfully',
                'app_yaml': str(app_yaml_path),
                'next_steps': [
                    'View your app: gcloud app browse',
                    'Check logs: gcloud app logs tail -s default'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'troubleshooting': [
                    'Check app.yaml syntax',
                    'Ensure App Engine is initialized',
                    'Verify all required files are present'
                ]
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Google Cloud status"""
        status = self.check_setup()
        
        if status.get('gcloud_installed') and status.get('authenticated'):
            # Get additional info
            project_info = self.get_current_project()
            
            # Check App Engine status
            app_engine_result = self._run_gcloud_command([
                'app', 'describe', '--format=json'
            ])
            
            app_engine_status = None
            if app_engine_result['success']:
                try:
                    app_info = json.loads(app_engine_result['output'])
                    app_engine_status = {
                        'initialized': True,
                        'id': app_info.get('id'),
                        'location': app_info.get('locationId'),
                        'serving_status': app_info.get('servingStatus')
                    }
                except json.JSONDecodeError:
                    app_engine_status = {'initialized': False}
            else:
                app_engine_status = {'initialized': False}
            
            return {
                **status,
                'project_info': project_info,
                'app_engine': app_engine_status,
                'summary': f"✅ Ready - Project: {project_info.get('project_id', 'None')}"
            }
        
        return status
    
    def setup_config(self, region: str = 'asia-northeast3') -> Dict[str, Any]:
        """Setup default configuration for Korean users"""
        if not self.gcloud_installed:
            return {'error': 'Google Cloud CLI not installed'}
        
        configs = [
            (['config', 'set', 'compute/region', region], f'Set region to {region}'),
            (['config', 'set', 'compute/zone', f'{region}-a'], f'Set zone to {region}-a'),
            (['config', 'set', 'core/disable_usage_reporting', 'true'], 'Disable usage reporting')
        ]
        
        results = []
        for command, description in configs:
            result = self._run_gcloud_command(command)
            results.append({
                'description': description,
                'success': result['success'],
                'error': result.get('error')
            })
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success': success_count == len(configs),
            'message': f'Configuration setup: {success_count}/{len(configs)} successful',
            'region': region,
            'results': results
        }