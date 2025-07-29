#!/usr/bin/env python3
"""
Claude Code Assistant - Core Module
A comprehensive assistant built on top of Claude Code and SuperClaude framework.
"""

import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Task:
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

@dataclass
class ProjectContext:
    path: Path
    language: Optional[str] = None
    framework: Optional[str] = None
    package_manager: Optional[str] = None
    git_repo: bool = False
    dependencies: List[str] = field(default_factory=list)
    
class ClaudeAssistant:
    """
    Core Claude Code Assistant that integrates with SuperClaude framework
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.current_context: Optional[ProjectContext] = None
        self.tasks: Dict[str, Task] = {}
        self.session_id = self._generate_session_id()
        
        # Initialize Claude Code integration
        self._check_claude_code_installation()
        self._check_superclaude_installation()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration path"""
        home = Path.home()
        return str(home / ".claude" / "assistant_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load assistant configuration"""
        default_config = {
            "claude_code": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "timeout": 300
            },
            "assistant": {
                "auto_context": True,
                "task_persistence": True,
                "verbose_logging": False
            },
            "integrations": {
                "superclaude": True,
                "mcp_servers": ["context7", "sequential", "magic"]
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge configs
                return {**default_config, **user_config}
        except Exception as e:
            logger.warning(f"Error loading config: {e}. Using defaults.")
        
        return default_config
    
    def _check_claude_code_installation(self) -> bool:
        """Check if Claude Code is installed and accessible"""
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Claude Code detected: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.error("Claude Code not found. Please install Claude Code CLI.")
        return False
    
    def _check_superclaude_installation(self) -> bool:
        """Check if SuperClaude is installed and configured"""
        claude_dir = Path.home() / ".claude"
        superclaude_files = [
            "CLAUDE.md", "COMMANDS.md", "FLAGS.md", 
            "PERSONAS.md", "ORCHESTRATOR.md"
        ]
        
        missing_files = []
        for file in superclaude_files:
            if not (claude_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.warning(f"SuperClaude files missing: {missing_files}")
            return False
        
        logger.info("SuperClaude framework detected and configured")
        return True
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def analyze_project_context(self, path: str = ".") -> ProjectContext:
        """Analyze current project context"""
        project_path = Path(path).resolve()
        context = ProjectContext(path=project_path)
        
        # Detect language and framework
        context.language = self._detect_language(project_path)
        context.framework = self._detect_framework(project_path)
        context.package_manager = self._detect_package_manager(project_path)
        context.git_repo = (project_path / ".git").exists()
        
        # Load dependencies
        context.dependencies = self._get_dependencies(project_path)
        
        self.current_context = context
        logger.info(f"Project context loaded: {context.language}/{context.framework}")
        return context
    
    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect primary programming language"""
        language_files = {
            'python': ['*.py', 'requirements.txt', 'pyproject.toml'],
            'javascript': ['*.js', '*.ts', 'package.json', 'node_modules'],
            'java': ['*.java', 'pom.xml', 'build.gradle'],
            'go': ['*.go', 'go.mod'],
            'rust': ['*.rs', 'Cargo.toml'],
            'cpp': ['*.cpp', '*.hpp', 'CMakeLists.txt']
        }
        
        for lang, patterns in language_files.items():
            for pattern in patterns:
                if list(path.glob(pattern)):
                    return lang
        return None
    
    def _detect_framework(self, path: Path) -> Optional[str]:
        """Detect framework or library"""
        framework_indicators = {
            'react': ['package.json'],
            'vue': ['vue.config.js', 'vite.config.js'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'requirements.txt'],
            'express': ['package.json'],
            'spring': ['pom.xml', 'application.properties']
        }
        
        for framework, files in framework_indicators.items():
            if all((path / f).exists() for f in files):
                return framework
        return None
    
    def _detect_package_manager(self, path: Path) -> Optional[str]:
        """Detect package manager"""
        managers = {
            'npm': 'package.json',
            'yarn': 'yarn.lock',
            'pip': 'requirements.txt',
            'poetry': 'pyproject.toml',
            'maven': 'pom.xml',
            'gradle': 'build.gradle'
        }
        
        for manager, file in managers.items():
            if (path / file).exists():
                return manager
        return None
    
    def _get_dependencies(self, path: Path) -> List[str]:
        """Extract project dependencies"""
        deps = []
        
        # Python dependencies
        if (path / 'requirements.txt').exists():
            with open(path / 'requirements.txt') as f:
                deps.extend(line.strip() for line in f if line.strip())
        
        # Node.js dependencies
        if (path / 'package.json').exists():
            try:
                with open(path / 'package.json') as f:
                    pkg = json.load(f)
                    deps.extend(pkg.get('dependencies', {}).keys())
                    deps.extend(pkg.get('devDependencies', {}).keys())
            except json.JSONDecodeError:
                pass
        
        return deps
    
    def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute Claude Code or SuperClaude command"""
        args = args or []
        
        # Check if it's a SuperClaude command
        if command.startswith('/sc:'):
            return self._execute_superclaude_command(command, args)
        
        # Standard Claude Code command
        try:
            cmd = ['claude'] + [command] + args
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=self.config['claude_code']['timeout'])
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'command': ' '.join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'command': ' '.join(cmd)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(cmd)
            }
    
    def _execute_superclaude_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute SuperClaude-specific commands"""
        # Remove /sc: prefix
        cmd_name = command[4:]
        
        # Map to actual SuperClaude commands
        superclaude_commands = {
            'build': '/build',
            'implement': '/implement', 
            'analyze': '/analyze',
            'improve': '/improve',
            'test': '/test',
            'document': '/document'
        }
        
        if cmd_name in superclaude_commands:
            actual_cmd = superclaude_commands[cmd_name]
            return self.execute_command(actual_cmd, args)
        
        return {
            'success': False,
            'error': f'Unknown SuperClaude command: {cmd_name}'
        }
    
    def create_task(self, description: str, priority: Priority = Priority.MEDIUM, 
                   context: Dict[str, Any] = None) -> Task:
        """Create a new task"""
        import time
        
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            context=context or {},
            created_at=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id} - {description}")
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        if task_id in self.tasks:
            import time
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Updated task {task_id}: {status.value}")
            return True
        return False
    
    def get_task_summary(self) -> Dict[str, int]:
        """Get summary of tasks by status"""
        summary = {status.value: 0 for status in TaskStatus}
        for task in self.tasks.values():
            summary[task.status.value] += 1
        return summary
    
    def interactive_mode(self):
        """Start interactive assistant mode"""
        print(f"🤖 Claude Code Assistant v1.0 (Session: {self.session_id})")
        print("Type 'help' for commands, 'quit' to exit")
        
        # Auto-analyze current directory
        if self.config['assistant']['auto_context']:
            self.analyze_project_context()
            if self.current_context:
                print(f"📁 Project: {self.current_context.language}/{self.current_context.framework}")
        
        while True:
            try:
                user_input = input("\n🔥 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                result = self.execute_command(command, args)
                
                if result['success']:
                    print(f"✅ {result['output']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"❌ Internal error: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
🤖 Claude Code Assistant Commands:

Basic Commands:
  help                 Show this help
  status              Show project and task status
  quit/exit/q         Exit assistant

Claude Code Commands:
  All standard Claude Code commands are supported
  
SuperClaude Commands:
  /sc:build           Build project using SuperClaude
  /sc:implement       Implement features 
  /sc:analyze         Analyze codebase
  /sc:improve         Improve code quality
  /sc:test           Run tests
  /sc:document       Generate documentation

Task Management:
  Tasks are automatically created for complex operations
  Use 'status' to see current tasks
        """
        print(help_text)
    
    def _show_status(self):
        """Show current status"""
        print("\n📊 Assistant Status:")
        print(f"Session ID: {self.session_id}")
        
        if self.current_context:
            print(f"Project: {self.current_context.path}")
            print(f"Language: {self.current_context.language}")
            print(f"Framework: {self.current_context.framework}")
            print(f"Git Repo: {'Yes' if self.current_context.git_repo else 'No'}")
        
        task_summary = self.get_task_summary()
        print(f"\nTasks: {sum(task_summary.values())} total")
        for status, count in task_summary.items():
            if count > 0:
                print(f"  {status}: {count}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Claude Code Assistant")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Start in interactive mode')
    parser.add_argument('command', nargs='*', help='Command to execute')
    
    args = parser.parse_args()
    
    try:
        assistant = ClaudeAssistant(config_path=args.config)
        
        if args.interactive or not args.command:
            assistant.interactive_mode()
        else:
            # Execute single command
            command = args.command[0]
            cmd_args = args.command[1:] if len(args.command) > 1 else []
            result = assistant.execute_command(command, cmd_args)
            
            if result['success']:
                print(result['output'])
                sys.exit(0)
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()