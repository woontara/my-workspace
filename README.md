# Claude Code Assistant 🤖

A comprehensive, extensible assistant built on top of Claude Code and the SuperClaude framework. This assistant provides enhanced project management, code analysis, and development workflow automation.

## ✨ Features

### Core Functionality
- **🔍 Smart Project Context Analysis** - Automatically detects language, framework, and dependencies
- **📋 Intelligent Task Management** - Creates and tracks tasks for complex operations
- **🔌 Extensible Plugin System** - Modular architecture with built-in and custom plugins
- **⚙️ SuperClaude Integration** - Leverages existing SuperClaude commands and personas
- **🛠️ Multi-Language Support** - Python, JavaScript, Java, Go, Rust, and more

### Built-in Plugins
- **Code Analyzer** - Complexity analysis, dependency scanning, security checks
- **Project Manager** - Project initialization, environment setup, README generation

### Enhanced UX
- **🎨 Interactive Mode** - Rich command-line interface with emojis and colors
- **📊 Smart Status Display** - Real-time project and task information
- **🔄 Auto-Context Loading** - Automatically analyzes current directory on startup
- **🚀 Quick Launch** - Windows batch script and desktop shortcut support

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ installed and in PATH
- Claude Code CLI (optional but recommended)
- SuperClaude framework (detected automatically)

### Installation

1. **Download the assistant files** to a directory:
   ```bash
   # All files should be in the same directory:
   # - claude_assistant_core.py
   # - claude_assistant_plugins.py  
   # - run_assistant.py
   # - claude_assistant_config.json
   # - claude_assistant.bat (Windows)
   # - requirements.txt
   ```

2. **For Windows users** - Double-click `claude_assistant.bat`

3. **For Linux/Mac users**:
   ```bash
   python run_assistant.py --interactive
   ```

### First Run

The assistant will automatically:
- ✅ Check for Claude Code CLI installation
- ✅ Detect SuperClaude framework
- ✅ Load plugins
- ✅ Analyze current project context
- ✅ Start interactive mode

## 🎮 Usage

### Interactive Mode
```bash
python run_assistant.py --interactive
```

### Command Examples

#### Built-in Commands
```bash
# Show help
help

# Show current status
status

# List plugins
plugins

# Clear screen
clear

# Exit
quit
```

#### Plugin Commands
```bash
# Analyze code complexity
code-analyzer:analyze-complexity

# Analyze project dependencies  
code-analyzer:analyze-dependencies

# Security scan
code-analyzer:analyze-security

# Initialize new project
project-manager:init-project python my_project

# Setup development environment
project-manager:setup-env python

# Generate README
project-manager:gen-readme
```

#### SuperClaude Commands
```bash
# All SuperClaude commands work with /sc: prefix
/sc:build
/sc:implement feature_name
/sc:analyze
/sc:improve
/sc:test
/sc:document
```

### Single Command Execution
```bash
# Execute one command and exit
python run_assistant.py code-analyzer:analyze-complexity

# With arguments
python run_assistant.py project-manager:init-project javascript my_app
```

## 🔧 Configuration

The assistant uses `claude_assistant_config.json` for configuration:

```json
{
  "claude_code": {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4096,
    "timeout": 300
  },
  "assistant": {
    "auto_context": true,
    "task_persistence": true, 
    "plugin_system": true
  },
  "integrations": {
    "superclaude": true,
    "mcp_servers": ["context7", "sequential", "magic"]
  }
}
```

## 🔌 Plugin System

### Creating Custom Plugins

1. Create a Python file in `~/.claude/plugins/`
2. Inherit from the `Plugin` base class:

```python
from claude_assistant_plugins import Plugin

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property 
    def description(self) -> str:
        return "My custom plugin"
    
    def initialize(self, assistant_context):
        return True
    
    def get_commands(self):
        return {
            'my-command': self.my_command
        }
    
    def my_command(self, arg1, arg2="default"):
        return f"Executed with {arg1} and {arg2}"
```

3. Use with: `my-plugin:my-command arg1 arg2`

### Available Plugins

#### Code Analyzer Plugin
- `analyze-complexity` - Code complexity metrics
- `analyze-dependencies` - Dependency analysis
- `analyze-security` - Basic security scanning

#### Project Manager Plugin
- `init-project <type> <name>` - Initialize new project
- `setup-env <type>` - Setup development environment
- `gen-readme [path]` - Generate README.md

## 🏗️ Architecture

```
Claude Code Assistant
├── Core Module (claude_assistant_core.py)
│   ├── ClaudeAssistant - Main orchestration
│   ├── ProjectContext - Project analysis
│   └── Task Management - Progress tracking
├── Plugin System (claude_assistant_plugins.py)
│   ├── PluginManager - Plugin loading/execution
│   ├── CodeAnalyzerPlugin - Code analysis tools
│   └── ProjectManagerPlugin - Project tools
└── Enhanced Launcher (run_assistant.py)
    ├── EnhancedClaudeAssistant - UI enhancements
    └── Interactive Mode - Rich CLI experience
```

## 🔗 Integration

### Claude Code CLI
- Seamless integration with Claude Code commands
- Automatic detection and error handling
- Full SuperClaude framework support

### SuperClaude Framework
- Leverages existing commands and personas
- Respects framework configuration
- Compatible with MCP servers

### Development Tools
- Git repository detection
- Package manager detection (npm, pip, maven, etc.)
- Multi-language project support

## 🛠️ Development

### Project Structure
```
claude_assistant/
├── claude_assistant_core.py      # Core functionality
├── claude_assistant_plugins.py   # Plugin system
├── run_assistant.py             # Enhanced launcher
├── claude_assistant_config.json # Configuration
├── claude_assistant.bat         # Windows launcher
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

### Testing
```bash
# Test help system
python run_assistant.py --help

# Test plugin loading
python run_assistant.py plugins

# Test code analysis
python run_assistant.py code-analyzer:analyze-complexity

# Test project creation
python run_assistant.py project-manager:init-project python test_project
```

## 🔍 Troubleshooting

### Common Issues

#### "Claude Code not found"
- Install Claude Code CLI from https://docs.anthropic.com/claude-code
- Or continue without it - core functionality still works

#### "SuperClaude files missing"
- Install SuperClaude framework
- Or disable SuperClaude integration in config

#### Plugin errors
- Check plugin file syntax
- Ensure plugin directory exists: `~/.claude/plugins/`
- Check logs with `--verbose` flag

### Debug Mode
```bash
python run_assistant.py --verbose --interactive
```

## 📈 Roadmap  

### v1.1 (Current)
- ✅ Core assistant functionality
- ✅ Plugin system
- ✅ SuperClaude integration
- ✅ Interactive mode

### v1.2 (Planned)
- 🔄 Web interface
- 🔄 More built-in plugins
- 🔄 Configuration GUI
- 🔄 Plugin marketplace

### v2.0 (Future)
- 🔄 Multi-project support
- 🔄 Cloud synchronization
- 🔄 Team collaboration features
- 🔄 Advanced AI workflows

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on top of [Claude Code](https://docs.anthropic.com/claude-code) by Anthropic
- Leverages the [SuperClaude Framework](https://github.com/NomenAK/SuperClaude)
- Inspired by the amazing AI coding assistant community

---

**Happy Coding!** 🚀

*Made with ❤️ by developers, for developers*