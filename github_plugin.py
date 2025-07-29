#!/usr/bin/env python3
"""
GitHub Plugin for Claude Code Assistant
Provides integration with GitHub repositories and workflows.
"""

import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from claude_assistant_plugins import Plugin

logger = logging.getLogger(__name__)

class GitHubPlugin(Plugin):
    """Plugin for GitHub integration"""
    
    @property
    def name(self) -> str:
        return "github"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "GitHub integration and repository management"
    
    def initialize(self, assistant_context: Any) -> bool:
        self.context = assistant_context
        self.git_installed = self._check_git_installation()
        self.gh_installed = self._check_gh_installation()
        return True
    
    def get_commands(self) -> Dict[str, callable]:
        return {
            'check-setup': self.check_setup,
            'setup-git': self.setup_git,
            'install-gh-cli': self.install_gh_cli,
            'auth-login': self.auth_login,
            'whoami': self.whoami,
            'create-repo': self.create_repo,
            'clone-repo': self.clone_repo,
            'init-repo': self.init_repo,
            'status': self.get_status,
            'commit': self.commit_changes,
            'push': self.push_changes,
            'pull': self.pull_changes,
            'list-repos': self.list_repos,
            'repo-info': self.repo_info
        }
    
    def _check_git_installation(self) -> bool:
        """Check if Git is installed"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_gh_installation(self) -> bool:
        """Check if GitHub CLI is installed"""
        try:
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _run_git_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run git command and return result"""
        try:
            full_command = ['git'] + command
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
                'command': ' '.join(['git'] + command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(['git'] + command)
            }
    
    def _run_gh_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run GitHub CLI command and return result"""
        try:
            full_command = ['gh'] + command
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
                'command': ' '.join(['gh'] + command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(['gh'] + command)
            }
    
    def check_setup(self) -> Dict[str, Any]:
        """Check GitHub setup status"""
        setup_status = {
            'git_installed': self.git_installed,
            'gh_cli_installed': self.gh_installed,
            'git_configured': False,
            'gh_authenticated': False,
            'status': 'needs_setup'
        }
        
        if not self.git_installed:
            setup_status['message'] = 'Git not installed'
            setup_status['install_instructions'] = {
                'windows': 'Download from https://git-scm.com/download/win',
                'mac': 'brew install git',
                'linux': 'sudo apt install git'
            }
            return setup_status
        
        # Check Git configuration
        git_config = self._run_git_command(['config', '--global', '--list'])
        if git_config['success']:
            config_lines = git_config['output'].split('\n')
            has_name = any('user.name=' in line for line in config_lines)
            has_email = any('user.email=' in line for line in config_lines)
            setup_status['git_configured'] = has_name and has_email
            
            if setup_status['git_configured']:
                setup_status['git_user'] = {}
                for line in config_lines:
                    if 'user.name=' in line:
                        setup_status['git_user']['name'] = line.split('=', 1)[1]
                    elif 'user.email=' in line:
                        setup_status['git_user']['email'] = line.split('=', 1)[1]
        
        # Check GitHub CLI authentication
        if self.gh_installed:
            gh_auth = self._run_gh_command(['auth', 'status'])
            setup_status['gh_authenticated'] = gh_auth['success']
            
            if setup_status['gh_authenticated']:
                # Get GitHub user info
                whoami = self._run_gh_command(['api', 'user'])
                if whoami['success']:
                    try:
                        user_info = json.loads(whoami['output'])
                        setup_status['github_user'] = {
                            'login': user_info.get('login'),
                            'name': user_info.get('name'),
                            'email': user_info.get('email')
                        }
                    except json.JSONDecodeError:
                        pass
        
        # Determine overall status
        if (setup_status['git_configured'] and 
            setup_status['gh_cli_installed'] and 
            setup_status['gh_authenticated']):
            setup_status['status'] = 'ready'
        elif setup_status['git_configured']:
            setup_status['status'] = 'partial'
        
        return setup_status
    
    def setup_git(self, name: str, email: str) -> Dict[str, Any]:
        """Setup Git with user name and email"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        if not name or not email:
            return {'error': 'Name and email are required'}
        
        # Set user name
        name_result = self._run_git_command(['config', '--global', 'user.name', name])
        if not name_result['success']:
            return {
                'success': False,
                'error': f"Failed to set name: {name_result['error']}"
            }
        
        # Set user email
        email_result = self._run_git_command(['config', '--global', 'user.email', email])
        if not email_result['success']:
            return {
                'success': False,
                'error': f"Failed to set email: {email_result['error']}"
            }
        
        # Set additional useful configs
        configs = [
            (['config', '--global', 'init.defaultBranch', 'main'], 'Default branch'),
            (['config', '--global', 'pull.rebase', 'false'], 'Merge strategy'),
            (['config', '--global', 'core.autocrlf', 'true'], 'Line endings (Windows)')
        ]
        
        config_results = []
        for command, description in configs:
            result = self._run_git_command(command)
            config_results.append({
                'description': description,
                'success': result['success']
            })
        
        return {
            'success': True,
            'message': f'Git configured for {name} <{email}>',
            'user': {'name': name, 'email': email},
            'additional_configs': config_results,
            'next_steps': ['Install GitHub CLI: github:install-gh-cli']
        }
    
    def install_gh_cli(self) -> Dict[str, Any]:
        """Install GitHub CLI"""
        if self.gh_installed:
            return {
                'success': True,
                'message': 'GitHub CLI already installed'
            }
        
        # Download GitHub CLI installer
        installer_url = 'https://github.com/cli/cli/releases/latest/download/gh_windows_amd64.msi'
        installer_path = Path.home() / 'gh_installer.msi'
        
        try:
            import urllib.request
            print("🔽 Downloading GitHub CLI installer...")
            urllib.request.urlretrieve(installer_url, installer_path)
            
            return {
                'success': True,
                'message': 'GitHub CLI installer downloaded',
                'installer_path': str(installer_path),
                'next_steps': [
                    f'Run installer: {installer_path}',
                    'Restart terminal after installation',
                    'Authenticate: github:auth-login'
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to download installer: {e}',
                'manual_install': 'Visit https://cli.github.com/ for manual installation'
            }
    
    def auth_login(self) -> Dict[str, Any]:
        """Authenticate with GitHub"""
        if not self.gh_installed:
            return {'error': 'GitHub CLI not installed. Use: github:install-gh-cli'}
        
        print("🔐 Opening browser for GitHub authentication...")
        result = self._run_gh_command(['auth', 'login', '--web'], timeout=120)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Successfully authenticated with GitHub',
                'next_steps': [
                    'Check status: github:whoami',
                    'Create repository: github:create-repo REPO_NAME'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'troubleshooting': [
                    'Make sure you have internet connection',
                    'Check if browser allows popups',
                    'Try: gh auth login --web'
                ]
            }
    
    def whoami(self) -> Dict[str, Any]:
        """Get current GitHub user info"""
        if not self.gh_installed:
            return {'error': 'GitHub CLI not installed'}
        
        result = self._run_gh_command(['api', 'user'])
        
        if result['success']:
            try:
                user_info = json.loads(result['output'])
                return {
                    'success': True,
                    'user': {
                        'login': user_info.get('login'),
                        'name': user_info.get('name'),
                        'email': user_info.get('email'),
                        'public_repos': user_info.get('public_repos'),
                        'followers': user_info.get('followers'),
                        'following': user_info.get('following'),
                        'created_at': user_info.get('created_at'),
                        'location': user_info.get('location'),
                        'bio': user_info.get('bio')
                    }
                }
            except json.JSONDecodeError:
                return {'error': 'Failed to parse user information'}
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestion': 'Try authenticating first: github:auth-login'
            }
    
    def create_repo(self, repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        if not self.gh_installed:
            return {'error': 'GitHub CLI not installed'}
        
        if not repo_name:
            return {'error': 'Repository name is required'}
        
        command = ['repo', 'create', repo_name]
        if description:
            command.extend(['--description', description])
        if private:
            command.append('--private')
        else:
            command.append('--public')
        
        result = self._run_gh_command(command, timeout=60)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Repository created: {repo_name}',
                'repository': repo_name,
                'visibility': 'private' if private else 'public',
                'next_steps': [
                    f'Clone: github:clone-repo {repo_name}',
                    f'View: https://github.com/[username]/{repo_name}'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestions': [
                    'Check if repository name is available',
                    'Ensure you have permission to create repositories',
                    'Repository names must be unique in your account'
                ]
            }
    
    def clone_repo(self, repo_url: str, directory: str = None) -> Dict[str, Any]:
        """Clone a GitHub repository"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        if not repo_url:
            return {'error': 'Repository URL is required'}
        
        command = ['clone', repo_url]
        if directory:
            command.append(directory)
        
        result = self._run_git_command(command, timeout=120)
        
        if result['success']:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            target_dir = directory or repo_name
            
            return {
                'success': True,
                'message': f'Repository cloned: {repo_name}',
                'directory': target_dir,
                'repository': repo_url,
                'next_steps': [
                    f'cd {target_dir}',
                    'Start working on your project'
                ]
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestions': [
                    'Check if repository URL is correct',
                    'Ensure you have access to the repository',
                    'Check your internet connection'
                ]
            }
    
    def init_repo(self, directory: str = ".") -> Dict[str, Any]:
        """Initialize a new Git repository"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        # Change to target directory
        original_dir = os.getcwd()
        try:
            if directory != ".":
                os.chdir(directory)
            
            # Initialize git repo
            init_result = self._run_git_command(['init'])
            if not init_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to initialize repository: {init_result['error']}"
                }
            
            # Create initial commit
            commands = [
                (['add', '.'], 'Stage files'),
                (['commit', '-m', 'Initial commit'], 'Initial commit')
            ]
            
            results = []
            for command, description in commands:
                result = self._run_git_command(command)
                results.append({
                    'description': description,
                    'success': result['success'],
                    'error': result.get('error') if not result['success'] else None
                })
            
            return {
                'success': True,
                'message': f'Git repository initialized in {directory}',
                'directory': directory,
                'operations': results,
                'next_steps': [
                    'Create GitHub repo: github:create-repo REPO_NAME',
                    'Connect remote: git remote add origin URL'
                ]
            }
            
        finally:
            os.chdir(original_dir)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive GitHub status"""
        status = self.check_setup()
        
        # Add current repository info if in a git repo
        repo_status = self._run_git_command(['status', '--porcelain'])
        if repo_status['success']:
            status['current_repo'] = {
                'is_git_repo': True,
                'has_changes': bool(repo_status['output']),
                'changes_count': len(repo_status['output'].split('\n')) if repo_status['output'] else 0
            }
            
            # Get current branch
            branch_result = self._run_git_command(['branch', '--show-current'])
            if branch_result['success']:
                status['current_repo']['branch'] = branch_result['output']
            
            # Get remote info
            remote_result = self._run_git_command(['remote', '-v'])
            if remote_result['success'] and remote_result['output']:
                remotes = {}
                for line in remote_result['output'].split('\n'):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        url = parts[1]
                        if name not in remotes:
                            remotes[name] = url
                status['current_repo']['remotes'] = remotes
        
        return status
    
    def commit_changes(self, message: str) -> Dict[str, Any]:
        """Commit changes to Git"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        if not message:
            return {'error': 'Commit message is required'}
        
        # Check if there are changes
        status_result = self._run_git_command(['status', '--porcelain'])
        if not status_result['success']:
            return {'error': 'Failed to check repository status'}
        
        if not status_result['output']:
            return {
                'success': True,
                'message': 'No changes to commit',
                'status': 'clean'
            }
        
        # Add all changes
        add_result = self._run_git_command(['add', '.'])
        if not add_result['success']:
            return {
                'success': False,
                'error': f"Failed to stage changes: {add_result['error']}"
            }
        
        # Commit changes
        commit_result = self._run_git_command(['commit', '-m', message])
        if commit_result['success']:
            return {
                'success': True,
                'message': f'Changes committed: {message}',
                'commit_message': message,
                'next_steps': ['Push changes: github:push']
            }
        else:
            return {
                'success': False,
                'error': f"Failed to commit: {commit_result['error']}"
            }
    
    def push_changes(self, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Push changes to GitHub"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        # Get current branch if not specified
        if not branch:
            branch_result = self._run_git_command(['branch', '--show-current'])
            if branch_result['success']:
                branch = branch_result['output']
            else:
                branch = 'main'
        
        # Push changes
        push_result = self._run_git_command(['push', remote, branch], timeout=60)
        
        if push_result['success']:
            return {
                'success': True,
                'message': f'Changes pushed to {remote}/{branch}',
                'remote': remote,
                'branch': branch
            }
        else:
            return {
                'success': False,
                'error': push_result['error'],
                'suggestions': [
                    'Check if remote repository exists',
                    'Ensure you have push permissions',
                    'Try: git push --set-upstream origin main'
                ]
            }
    
    def pull_changes(self, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """Pull changes from GitHub"""
        if not self.git_installed:
            return {'error': 'Git not installed'}
        
        # Get current branch if not specified
        if not branch:
            branch_result = self._run_git_command(['branch', '--show-current'])
            if branch_result['success']:
                branch = branch_result['output']
            else:
                branch = 'main'
        
        # Pull changes
        pull_result = self._run_git_command(['pull', remote, branch], timeout=60)
        
        if pull_result['success']:
            return {
                'success': True,
                'message': f'Changes pulled from {remote}/{branch}',
                'remote': remote,
                'branch': branch,
                'output': pull_result['output']
            }
        else:
            return {
                'success': False,
                'error': pull_result['error'],
                'suggestions': [
                    'Check if remote repository exists',
                    'Resolve any merge conflicts',
                    'Ensure you have pull permissions'
                ]
            }
    
    def list_repos(self, limit: int = 10) -> Dict[str, Any]:
        """List user's GitHub repositories"""
        if not self.gh_installed:
            return {'error': 'GitHub CLI not installed'}
        
        result = self._run_gh_command(['repo', 'list', '--limit', str(limit), '--json', 'name,description,visibility,updatedAt'])
        
        if result['success']:
            try:
                repos = json.loads(result['output'])
                return {
                    'success': True,
                    'repositories': repos,
                    'count': len(repos),
                    'formatted_list': [
                        f"{repo['name']} ({repo['visibility']}) - {repo.get('description', 'No description')}"
                        for repo in repos
                    ]
                }
            except json.JSONDecodeError:
                return {'error': 'Failed to parse repositories list'}
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestion': 'Try authenticating first: github:auth-login'
            }
    
    def repo_info(self, repo_name: str = None) -> Dict[str, Any]:
        """Get repository information"""
        if not self.gh_installed:
            return {'error': 'GitHub CLI not installed'}
        
        command = ['repo', 'view']
        if repo_name:
            command.append(repo_name)
        command.extend(['--json', 'name,description,visibility,stars,forks,language,createdAt,updatedAt'])
        
        result = self._run_gh_command(command)
        
        if result['success']:
            try:
                repo_info = json.loads(result['output'])
                return {
                    'success': True,
                    'repository': repo_info,
                    'summary': {
                        'name': repo_info.get('name'),
                        'description': repo_info.get('description'),
                        'visibility': repo_info.get('visibility'),
                        'language': repo_info.get('language'),
                        'stars': repo_info.get('stars'),
                        'forks': repo_info.get('forks'),
                        'created': repo_info.get('createdAt'),
                        'updated': repo_info.get('updatedAt')
                    }
                }
            except json.JSONDecodeError:
                return {'error': 'Failed to parse repository information'}
        else:
            return {
                'success': False,
                'error': result['error'],
                'suggestion': 'Check repository name and permissions'
            }