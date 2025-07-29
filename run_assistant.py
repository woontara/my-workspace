#!/usr/bin/env python3
"""
Claude Code Assistant - Launcher Script
Enhanced launcher with plugin support and better integration.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from claude_assistant_core import ClaudeAssistant, Priority, TaskStatus
from claude_assistant_plugins import PluginManager
import logging

class EnhancedClaudeAssistant(ClaudeAssistant):
    """Enhanced assistant with plugin support"""
    
    def __init__(self, config_path=None):
        super().__init__(config_path)
        
        # Initialize plugin system
        self.plugin_manager = None
        if self.config.get('plugins', {}).get('enabled', True):
            try:
                self.plugin_manager = PluginManager()
                logging.info(f"Loaded {len(self.plugin_manager.plugins)} plugins")
            except Exception as e:
                logging.error(f"Failed to initialize plugin system: {e}")
    
    def execute_command(self, command, args=None):
        """Enhanced command execution with plugin support"""
        args = args or []
        
        # Check if it's a plugin command
        if self.plugin_manager and ':' in command:
            try:
                result = self.plugin_manager.execute_command(command, *args)
                return {
                    'success': not isinstance(result, dict) or 'error' not in result,
                    'output': str(result) if not isinstance(result, dict) else result,
                    'command': command
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'command': command
                }
        
        # Fall back to parent implementation
        return super().execute_command(command, args)
    
    def _show_help(self):
        """Enhanced help with plugin commands"""
        super()._show_help()
        
        if self.plugin_manager:
            print("\n🔌 Plugin Commands:")
            plugins = self.plugin_manager.list_plugins()
            for plugin in plugins:
                print(f"  {plugin['name']} v{plugin['version']}: {plugin['description']}")
            
            print("\nAvailable plugin commands:")
            for command in sorted(self.plugin_manager.list_commands()):
                print(f"  {command}")
    
    def _show_status(self):
        """Enhanced status with plugin information"""
        super()._show_status()
        
        if self.plugin_manager:
            plugins = self.plugin_manager.list_plugins()
            print(f"\nPlugins: {len(plugins)} loaded")
            for plugin in plugins:
                print(f"  {plugin['name']} v{plugin['version']}")
    
    def interactive_mode(self):
        """Enhanced interactive mode with better UX"""
        print("🚀 Enhanced Claude Code Assistant v1.1")
        print("🔥 Powered by SuperClaude Framework")
        
        if self.plugin_manager:
            plugin_count = len(self.plugin_manager.plugins)
            print(f"🔌 {plugin_count} plugins loaded")
        
        print("\nType 'help' for commands, 'quit' to exit")
        print("💡 Try plugin commands like 'code-analyzer:analyze-complexity'")
        
        # Auto-analyze current directory
        if self.config['assistant']['auto_context']:
            print("\n🔍 Analyzing project context...")
            self.analyze_project_context()
            if self.current_context:
                ctx = self.current_context
                print(f"📁 Project: {ctx.path.name}")
                print(f"🏷️  Language: {ctx.language or 'Unknown'}")
                print(f"⚙️  Framework: {ctx.framework or 'None detected'}")
                print(f"📦 Package Manager: {ctx.package_manager or 'None'}")
                print(f"🔀 Git Repository: {'Yes' if ctx.git_repo else 'No'}")
                
                if ctx.dependencies:
                    print(f"📚 Dependencies: {len(ctx.dependencies)} found")
        
        print("\n" + "="*60)
        
        while True:
            try:
                user_input = input("\n🤖 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Thanks for using Claude Code Assistant!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                if user_input.lower() == 'plugins':
                    self._show_plugins()
                    continue
                
                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Create task for complex operations
                if command.startswith('/') or ':' in command:
                    task = self.create_task(f"Execute: {command}", Priority.MEDIUM)
                    self.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                
                # Execute command
                print("⏳ Processing...")
                result = self.execute_command(command, args)
                
                if result['success']:
                    output = result['output']
                    if isinstance(output, dict):
                        self._pretty_print_dict(output)
                    else:
                        print(f"✅ {output}")
                    
                    # Update task status
                    if command.startswith('/') or ':' in command:
                        self.update_task_status(task.id, TaskStatus.COMPLETED)
                else:
                    print(f"❌ Error: {result['error']}")
                    if command.startswith('/') or ':' in command:
                        self.update_task_status(task.id, TaskStatus.FAILED)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using Claude Code Assistant!")
                break
            except Exception as e:
                logging.error(f"Error in interactive mode: {e}")
                print(f"❌ Internal error: {e}")
    
    def _show_plugins(self):
        """Show detailed plugin information"""
        if not self.plugin_manager:
            print("❌ Plugin system not available")
            return
        
        plugins = self.plugin_manager.list_plugins()
        
        if not plugins:
            print("📦 No plugins loaded")
            return
        
        print(f"\n📦 Loaded Plugins ({len(plugins)}):")
        print("=" * 50)
        
        for plugin in plugins:
            print(f"🔌 {plugin['name']} v{plugin['version']}")
            print(f"   {plugin['description']}")
            print()
        
        print("Available Commands:")
        commands = self.plugin_manager.list_commands()
        for cmd in sorted(commands):
            print(f"  • {cmd}")
    
    def _pretty_print_dict(self, data, indent=0):
        """Pretty print dictionary data"""
        if not isinstance(data, dict):
            print("  " * indent + str(data))
            return
        
        for key, value in data.items():
            if isinstance(value, dict):
                print("  " * indent + f"📋 {key}:")
                self._pretty_print_dict(value, indent + 1)
            elif isinstance(value, list):
                print("  " * indent + f"📝 {key}: [{len(value)} items]")
                for item in value[:5]:  # Limit to first 5 items
                    print("  " * (indent + 1) + f"• {item}")
                if len(value) > 5:
                    print("  " * (indent + 1) + f"... and {len(value) - 5} more")
            else:
                print("  " * indent + f"🏷️  {key}: {value}")

def create_desktop_shortcut():
    """Create desktop shortcut for the assistant"""
    try:
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            return False
        
        if os.name == 'nt':  # Windows
            import winshell
            from win32com.client import Dispatch
            
            shortcut_path = desktop / "Claude Assistant.lnk"
            target = sys.executable
            args = str(Path(__file__).resolve())
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = target
            shortcut.Arguments = args
            shortcut.WorkingDirectory = str(Path(__file__).parent)
            shortcut.IconLocation = target
            shortcut.save()
            
            return True
        else:  # Linux/Mac
            shortcut_path = desktop / "Claude Assistant.desktop"
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Claude Assistant
Comment=Enhanced Claude Code Assistant
Exec={sys.executable} {Path(__file__).resolve()}
Icon=terminal
Terminal=true
Categories=Development;
"""
            with open(shortcut_path, 'w') as f:
                f.write(content)
            
            os.chmod(shortcut_path, 0o755)
            return True
            
    except Exception as e:
        logging.error(f"Failed to create desktop shortcut: {e}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Claude Code Assistant with Plugin Support"
    )
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Start in interactive mode')
    parser.add_argument('--create-shortcut', action='store_true',
                       help='Create desktop shortcut')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('command', nargs='*', help='Command to execute')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Create desktop shortcut if requested
    if args.create_shortcut:
        if create_desktop_shortcut():
            print("✅ Desktop shortcut created successfully!")
        else:
            print("❌ Failed to create desktop shortcut")
        return
    
    try:
        # Use config file from same directory if not specified
        if not args.config:
            config_file = Path(__file__).parent / "claude_assistant_config.json"
            if config_file.exists():
                args.config = str(config_file)
        
        assistant = EnhancedClaudeAssistant(config_path=args.config)
        
        if args.interactive or not args.command:
            assistant.interactive_mode()
        else:
            # Execute single command
            command = args.command[0]
            cmd_args = args.command[1:] if len(args.command) > 1 else []
            result = assistant.execute_command(command, cmd_args)
            
            if result['success']:
                output = result['output']
                if isinstance(output, dict):
                    import json
                    print(json.dumps(output, indent=2))
                else:
                    print(output)
                sys.exit(0)
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()