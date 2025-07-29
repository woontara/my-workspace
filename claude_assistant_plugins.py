#!/usr/bin/env python3
"""
Claude Code Assistant - Plugin System
Extensible plugin architecture for custom functionality.
"""

import json
import os
import importlib
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """Base plugin interface"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod 
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @abstractmethod
    def initialize(self, assistant_context: Any) -> bool:
        """Initialize plugin with assistant context"""
        pass
    
    @abstractmethod
    def get_commands(self) -> Dict[str, Callable]:
        """Return available commands"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

class CodeAnalyzerPlugin(Plugin):
    """Plugin for advanced code analysis"""
    
    @property
    def name(self) -> str:
        return "code-analyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Advanced code analysis and metrics"
    
    def initialize(self, assistant_context: Any) -> bool:
        self.context = assistant_context
        return True
    
    def get_commands(self) -> Dict[str, Callable]:
        return {
            'analyze-complexity': self.analyze_complexity,
            'analyze-dependencies': self.analyze_dependencies,
            'analyze-security': self.analyze_security
        }
    
    def analyze_complexity(self, path: str = ".") -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        try:
            # Basic complexity analysis
            project_path = Path(path)
            results = {
                'total_files': 0,
                'total_lines': 0,
                'languages': {},
                'complexity_score': 0
            }
            
            # Count files and lines by language
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and not self._should_ignore(file_path):
                    suffix = file_path.suffix.lower()
                    
                    if suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.go']:
                        results['total_files'] += 1
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                results['total_lines'] += lines
                                
                                if suffix not in results['languages']:
                                    results['languages'][suffix] = {'files': 0, 'lines': 0}
                                
                                results['languages'][suffix]['files'] += 1
                                results['languages'][suffix]['lines'] += lines
                        except Exception:
                            continue
            
            # Calculate basic complexity score
            if results['total_files'] > 0:
                avg_lines_per_file = results['total_lines'] / results['total_files']
                results['complexity_score'] = min(10, avg_lines_per_file / 100)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing complexity: {e}")
            return {'error': str(e)}
    
    def analyze_dependencies(self, path: str = ".") -> Dict[str, Any]:
        """Analyze project dependencies"""
        try:
            project_path = Path(path)
            results = {
                'package_managers': [],
                'dependencies': {},
                'vulnerabilities': []
            }
            
            # Check for different package managers
            if (project_path / 'package.json').exists():
                results['package_managers'].append('npm')
                with open(project_path / 'package.json') as f:
                    pkg_data = json.load(f)
                    results['dependencies']['npm'] = {
                        'production': list(pkg_data.get('dependencies', {}).keys()),
                        'development': list(pkg_data.get('devDependencies', {}).keys())
                    }
            
            if (project_path / 'requirements.txt').exists():
                results['package_managers'].append('pip')
                with open(project_path / 'requirements.txt') as f:
                    deps = [line.strip().split('==')[0] for line in f if line.strip()]
                    results['dependencies']['pip'] = {'production': deps}
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {'error': str(e)}
    
    def analyze_security(self, path: str = ".") -> Dict[str, Any]:
        """Basic security analysis"""
        try:
            project_path = Path(path)
            issues = []
            
            # Check for common security issues
            for file_path in project_path.rglob('*.py'):
                if self._should_ignore(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Basic security checks
                        if 'password' in content.lower() and ('=' in content or ':' in content):
                            issues.append({
                                'file': str(file_path),
                                'type': 'potential_hardcoded_password',
                                'severity': 'high'
                            })
                        
                        if 'api_key' in content.lower() and ('=' in content or ':' in content):
                            issues.append({
                                'file': str(file_path),
                                'type': 'potential_hardcoded_api_key',
                                'severity': 'high'
                            })
                        
                        if 'eval(' in content or 'exec(' in content:
                            issues.append({
                                'file': str(file_path),
                                'type': 'dangerous_function_usage',
                                'severity': 'medium'
                            })
                            
                except Exception:
                    continue
            
            return {
                'issues_found': len(issues),
                'issues': issues,
                'risk_level': 'high' if any(i['severity'] == 'high' for i in issues) else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            return {'error': str(e)}
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '.git', '__pycache__', 'node_modules', '.venv',
            'venv', 'dist', 'build', '.pytest_cache'
        ]
        
        for pattern in ignore_patterns:
            if pattern in str(path):
                return True
        
        return False

class ProjectManagerPlugin(Plugin):
    """Plugin for project management features"""
    
    @property
    def name(self) -> str:
        return "project-manager"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Project initialization and management tools"
    
    def initialize(self, assistant_context: Any) -> bool:
        self.context = assistant_context
        return True
    
    def get_commands(self) -> Dict[str, Callable]:
        return {
            'init-project': self.init_project,
            'setup-env': self.setup_environment,
            'gen-readme': self.generate_readme
        }
    
    def init_project(self, project_type: str = "python", name: str = "my_project") -> Dict[str, Any]:
        """Initialize a new project"""
        try:
            project_path = Path(name)
            
            if project_path.exists():
                return {'error': f'Directory {name} already exists'}
            
            project_path.mkdir()
            
            if project_type.lower() == "python":
                self._init_python_project(project_path)
            elif project_type.lower() == "javascript":
                self._init_javascript_project(project_path)
            else:
                return {'error': f'Unsupported project type: {project_type}'}
            
            return {
                'success': True,
                'project_path': str(project_path),
                'project_type': project_type
            }
            
        except Exception as e:
            logger.error(f"Error initializing project: {e}")
            return {'error': str(e)}
    
    def _init_python_project(self, path: Path):
        """Initialize Python project structure"""
        # Create basic structure
        (path / "src").mkdir()
        (path / "tests").mkdir()
        (path / "docs").mkdir()
        
        # Create basic files
        with open(path / "README.md", 'w') as f:
            f.write(f"# {path.name}\n\nA Python project.\n")
        
        with open(path / "requirements.txt", 'w') as f:
            f.write("# Add your dependencies here\n")
        
        with open(path / ".gitignore", 'w') as f:
            f.write("__pycache__/\n*.pyc\n.venv/\ndist/\nbuild/\n")
        
        with open(path / "src" / "__init__.py", 'w') as f:
            f.write("")
    
    def _init_javascript_project(self, path: Path):
        """Initialize JavaScript project structure"""
        # Create basic structure
        (path / "src").mkdir()
        (path / "tests").mkdir()
        
        # Create package.json
        package_json = {
            "name": path.name,
            "version": "1.0.0",
            "description": "A JavaScript project",
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "dependencies": {},
            "devDependencies": {}
        }
        
        with open(path / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        with open(path / "README.md", 'w') as f:
            f.write(f"# {path.name}\n\nA JavaScript project.\n")
        
        with open(path / ".gitignore", 'w') as f:
            f.write("node_modules/\ndist/\nbuild/\n")
        
        with open(path / "src" / "index.js", 'w') as f:
            f.write("console.log('Hello, World!');\n")
    
    def setup_environment(self, env_type: str = "python") -> Dict[str, Any]:
        """Setup development environment"""
        try:
            if env_type.lower() == "python":
                return self._setup_python_env()
            elif env_type.lower() == "javascript":
                return self._setup_javascript_env()
            else:
                return {'error': f'Unsupported environment type: {env_type}'}
                
        except Exception as e:
            logger.error(f"Error setting up environment: {e}")
            return {'error': str(e)}
    
    def _setup_python_env(self) -> Dict[str, Any]:
        """Setup Python virtual environment"""
        import subprocess
        
        try:
            # Create virtual environment
            result = subprocess.run(['python', '-m', 'venv', '.venv'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Python virtual environment created',
                    'activation': 'Run: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)'
                }
            else:
                return {'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _setup_javascript_env(self) -> Dict[str, Any]:
        """Setup JavaScript/Node.js environment"""
        import subprocess
        
        try:
            # Install dependencies if package.json exists
            if Path('package.json').exists():
                result = subprocess.run(['npm', 'install'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'message': 'Node.js dependencies installed'
                    }
                else:
                    return {'error': result.stderr}
            else:
                return {'error': 'No package.json found'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def generate_readme(self, project_path: str = ".") -> Dict[str, Any]:
        """Generate README.md for project"""
        try:
            path = Path(project_path)
            
            # Analyze project to generate README
            readme_content = self._generate_readme_content(path)
            
            with open(path / "README.md", 'w') as f:
                f.write(readme_content)
            
            return {
                'success': True,
                'file': str(path / "README.md")
            }
            
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return {'error': str(e)}
    
    def _generate_readme_content(self, path: Path) -> str:
        """Generate README content based on project analysis"""
        project_name = path.name
        
        # Detect project type
        project_type = "Unknown"
        if (path / "package.json").exists():
            project_type = "JavaScript/Node.js"
        elif (path / "requirements.txt").exists() or any(path.glob("*.py")):
            project_type = "Python"
        elif (path / "pom.xml").exists():
            project_type = "Java/Maven"
        
        readme = f"""# {project_name}

A {project_type} project.

## Description

Add your project description here.

## Installation

"""
        
        # Add installation instructions based on project type
        if project_type == "Python":
            readme += """```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```
"""
        elif project_type == "JavaScript/Node.js":
            readme += """```bash
# Install dependencies
npm install

# Or with yarn
yarn install
```
"""
        
        readme += """
## Usage

Add usage instructions here.

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Add license information here.
"""
        
        return readme

class PluginManager:
    """Manages plugin loading and execution"""
    
    def __init__(self, plugin_dir: Optional[str] = None):
        self.plugin_dir = plugin_dir or self._get_default_plugin_dir()
        self.plugins: Dict[str, Plugin] = {}
        self.commands: Dict[str, Callable] = {}
        
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins
        self._load_external_plugins()
    
    def _get_default_plugin_dir(self) -> str:
        """Get default plugin directory"""
        return str(Path.home() / ".claude" / "plugins")
    
    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        builtin_plugins = [
            CodeAnalyzerPlugin(),
            ProjectManagerPlugin()
        ]
        
        # Try to load Google Cloud plugin
        try:
            import sys
            from pathlib import Path
            
            # Add current directory to path if not already there
            current_dir = str(Path(__file__).parent)
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from google_cloud_plugin import GoogleCloudPlugin
            builtin_plugins.append(GoogleCloudPlugin())
        except ImportError as e:
            logger.warning(f"Google Cloud plugin not available: {e}")
        
        # Try to load GitHub plugin
        try:
            from github_plugin import GitHubPlugin
            builtin_plugins.append(GitHubPlugin())
        except ImportError as e:
            logger.warning(f"GitHub plugin not available: {e}")
        
        for plugin in builtin_plugins:
            self._register_plugin(plugin)
    
    def _load_external_plugins(self):
        """Load external plugins from plugin directory"""
        plugin_path = Path(self.plugin_dir)
        
        if not plugin_path.exists():
            return
        
        for plugin_file in plugin_path.glob("*.py"):
            try:
                self._load_plugin_from_file(plugin_file)
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_file}: {e}")
    
    def _load_plugin_from_file(self, plugin_file: Path):
        """Load plugin from Python file"""
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem, plugin_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Plugin classes in module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, Plugin) and 
                obj != Plugin and 
                not obj.__name__.startswith('_')):
                
                plugin_instance = obj()
                self._register_plugin(plugin_instance)
    
    def _register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        try:
            if plugin.initialize(None):  # TODO: Pass assistant context
                self.plugins[plugin.name] = plugin
                
                # Register plugin commands
                commands = plugin.get_commands()
                for cmd_name, cmd_func in commands.items():
                    full_cmd_name = f"{plugin.name}:{cmd_name}"
                    self.commands[full_cmd_name] = cmd_func
                
                logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            else:
                logger.warning(f"Failed to initialize plugin: {plugin.name}")
                
        except Exception as e:
            logger.error(f"Error registering plugin {plugin.name}: {e}")
    
    def execute_command(self, command: str, *args, **kwargs) -> Any:
        """Execute a plugin command"""
        if command in self.commands:
            try:
                return self.commands[command](*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}")
                return {'error': str(e)}
        else:
            return {'error': f'Command not found: {command}'}
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins"""
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description
            }
            for plugin in self.plugins.values()
        ]
    
    def list_commands(self) -> List[str]:
        """List all available commands"""
        return list(self.commands.keys())
    
    def cleanup(self):
        """Cleanup all plugins"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin.name}: {e}")