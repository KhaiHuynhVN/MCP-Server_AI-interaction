# AI Interaction Tool - MCP Server

**Modern AI interaction tool with advanced UI and powerful features for Model Context Protocol (MCP)**

## 🚀 Core Features

### 🎯 Main Capabilities
- **Interactive UI Popup** for content input and conversation control
- **File/Folder Attachment** from workspace with validation and preview
- **🖼️ Image Attachment System** with drag & drop, multi-image support
- **Multi-language Support** (English/Vietnamese)
- **Maximum Cognitive Power** activation for peak AI performance
- **Tag-based Output Format** integrated with system prompt rules
- **Workspace-aware Path Processing** for cross-project compatibility

### 🔧 New in v2.2.0 (Latest)
- **🖼️ Image Attachment Support** with drag & drop functionality
- **🛡️ Security Enhanced** - secure path storage in user_images directory
- **💾 Persistent Image State** - checkbox state saves correctly
- **🎯 Multi-image Management** - attach, preview, and remove multiple images
- **🔄 Database Auto-cleanup** - automatic image cleanup when disabled

### 🔧 Previous v2.1.0
- **Enhanced UI/UX** with modern PyQt5 interface
- **Structured Tag-based Output** for perfect AI agent integration
- **Debounce Configuration** with smart auto-save mechanisms
- **Cursor IDE Integration** with comprehensive setup guide

## 📋 Installation & Setup Guide

### 📥 Step 1: Clone Repository
```bash
git clone https://github.com/your-username/AI-interaction.git
cd AI-interaction
```

### 🐍 Step 2: Install Python
- **Requirement**: Python 3.8+ 
- Download from [python.org](https://www.python.org/downloads/)
- Or use package manager:
  ```bash
  # Windows with Chocolatey
  choco install python
  
  # macOS with Homebrew
  brew install python
  
  # Ubuntu/Debian
  sudo apt update && sudo apt install python3 python3-pip
  ```

### 📦 Step 3: Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended for performance)
pip install uv
uv pip install -r requirements.txt
```

### ⚙️ Step 4: Configure MCP Server in Claude Desktop

Add the following configuration to Claude Desktop config file:

**Config file paths:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Configuration content:**
```json
{
  "mcpServers": {
    "AI_interaction": {
      "command": "python",
      "args": ["E:/MCP-servers-github/AI-interaction/mcp_server.py"],
      "stdio": true,
      "enabled": true
    }
  }
}
```

**⚠️ Important**: Replace `E:/MCP-servers-github/AI-interaction/mcp_server.py` with the absolute path to `mcp_server.py` on your system.

### 🧠 Step 5: Configure AI Agent Rules (REQUIRED)

**For proper AI agent operation with ai_interaction tool, you MUST setup custom instructions:**

#### 📋 **How to Add Custom Instructions:**

1. **Open Claude Desktop** or access Claude web interface
2. **Find "Custom Instructions"** or "Add custom instructions" in settings
3. **Copy entire content** from one of the rule files:
   - **🇻🇳 Vietnamese**: `rule_for_ai_VI.txt`
   - **🇺🇸 English**: `rule_for_ai_EN.txt`
4. **Paste into custom instructions** field and save

#### 🎯 **Why This is Necessary:**

- ✅ **Behavioral Framework**: Rules define how AI agent processes ai_interaction output
- ✅ **Thinking Protocols**: Activates high-level thinking patterns for quality responses
- ✅ **Ultra-Enhancement Modes**: 10 cognitive modes for maximum performance
- ✅ **Tag Processing**: Reads and processes control tags like `<AI_INTERACTION_CONTINUE_CHAT>`
- ✅ **Continue Logic**: Auto-recall ai_interaction when `continue_chat=true`

#### 📁 **Rule Files Location:**
```
AI-interaction/
├── rule_for_ai_VI.txt    # Vietnamese rules 
├── rule_for_ai_EN.txt    # English rules
└── ...
```

#### ⚡ **Quick Setup Commands:**
```bash
# View Vietnamese rules content
cat rule_for_ai_VI.txt

# View English rules content  
cat rule_for_ai_EN.txt

# Copy to clipboard (Windows)
type rule_for_ai_VI.txt | clip

# Copy to clipboard (macOS)
cat rule_for_ai_VI.txt | pbcopy

# Copy to clipboard (Linux)
cat rule_for_ai_VI.txt | xclip -selection clipboard
```

### 🚀 Step 6: Configure Cursor IDE (Recommended)

**Cursor is the recommended IDE for AI development with this tool:**

#### 📋 **Cursor Setup Steps:**

1. **Download Cursor**: [https://cursor.sh/](https://cursor.sh/)
2. **Install and open workspace**: Open AI-interaction folder
3. **Configure MCP in Cursor**:
   - Open Command Palette (`Cmd/Ctrl + Shift + P`)
   - Search "Configure MCP Servers"
   - Add AI_interaction server config
4. **Setup custom instructions**:
   - Copy content from `rule_for_ai_VI.txt` or `rule_for_ai_EN.txt`
   - Paste into "Custom Instructions" field in custom mode Agent:
   ![image](https://github.com/user-attachments/assets/2459fedd-ae0a-4850-aa1f-59866c50a4c4)
   ![image](https://github.com/user-attachments/assets/2b584b18-7231-4fab-baf4-81bec4ea942a)
   ![image](https://github.com/user-attachments/assets/12e385ee-1c01-4080-b25a-52daca25f15a)

#### 🎯 **Cursor Advantages:**
- ✅ **Native MCP Support**: Built-in integration with MCP servers
- ✅ **AI-First IDE**: Optimized for AI development workflows  
- ✅ **Real-time Suggestions**: Context-aware code completion
- ✅ **Advanced Debugging**: Enhanced debugging for MCP tools
- ✅ **Performance**: Faster than traditional IDEs for AI projects

### 🚀 Step 7: Launch and Test

!!! -----> In your terminal: python E:\MCP-servers-github\AI-interaction\main.py --ui
**⚠️ Important**: Replace `E:/MCP-servers-github/AI-interaction/mcp_server.py` with the absolute path to `mcp_server.py` on your system.
---> AUTO SHOW UI:
<img width="1164" height="930" alt="image" src="https://github.com/user-attachments/assets/b2b633d1-bc62-4c66-ad21-1c2b8eb71eb5" />

1. **Restart Claude Desktop/Cursor** after configuring MCP server
2. **Test connection** by calling `ai_interaction` tool
3. **Test UI popup** to verify functionality
4. **Validate rule integration** through AI agent responses

## 📦 Package Structure

```
AI-interaction/
├── ai_interaction_tool/       # Main interaction tool package
│   ├── core/                 # Core dialog and configuration
│   │   ├── dialog.py         # InputDialog with PyQt5 UI
│   │   └── config.py         # Configuration management
│   ├── ui/                   # Interface and styling
│   │   ├── file_dialog.py    # File attachment dialogs
│   │   ├── file_tree.py      # File system tree view
│   │   ├── image_attachment.py # 🖼️ Image attachment with drag & drop
│   │   └── styles.py         # Modern UI styling
│   ├── utils/                # Utilities and multi-language
│   │   ├── translations.py   # Multi-language support
│   │   └── file_utils.py     # File operation utilities
│   ├── engine.py             # Main entry point
│   ├── description.py        # Detailed tool description
│   └── __init__.py           # Package exports
├── user_images/              # 🛡️ Secure image storage directory
├── main.py                   # Legacy entry point
├── mcp_server.py             # MCP server implementation
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## 🎮 Usage Guide

### Available Tools in MCP Server

#### 1. **ai_interaction**: Main Interactive Tool
- **Function**: Creates UI popup for user input with file/image attachment
- **Output**: Structured tag-based format with image support
- **Integration**: Perfect integration with system prompt rules
- **Use cases**: 
  - Input complex content with formatting
  - Attach files/folders from workspace
  - **🖼️ Attach images with drag & drop functionality**
  - **📷 Multi-image support with preview and management**
  - Control AI thinking modes and reasoning levels

### Basic Usage Examples

```python
# Programmatic usage
from ai_interaction_tool import ai_interaction

# Launch interactive interface
result = ai_interaction()
print(result)  # Structured output with tags
```

### 🖼️ Image Attachment Features

#### 📷 **Core Image Capabilities**
- **Drag & Drop Support**: Drag images directly into the UI
- **Multi-image Management**: Attach, preview, and remove multiple images
- **Format Support**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Secure Storage**: Images stored safely in `user_images/` directory
- **Base64 Encoding**: Automatic conversion for AI processing
- **Preview System**: Click images to view larger versions
- **Persistent State**: Save images option with checkbox persistence

#### 🎯 **How to Use Image Attachment**
1. **Attach Button**: Click "📷 Attach Images" to select files
2. **Drag & Drop**: Drag images from file explorer directly to UI
3. **Paste Support**: Paste images from clipboard (Ctrl+V) 
4. **Multiple Images**: Attach as many images as needed
5. **Remove Images**: Click X button on individual image previews
6. **Clear All**: Use "🗑️ Clear Images" to remove all at once
7. **Save Toggle**: Check/uncheck "Save images" to control persistence

#### 🛡️ **Security & Privacy**
- **Local Only**: All images stored locally in `user_images/`
- **No External Access**: No uploads or external connections
- **Relative Paths**: Only relative paths stored in config for security
- **User Control**: Users control what images to attach and save
- **Auto-cleanup**: Images automatically cleaned when save disabled

### Output Format
AI Interaction Tool uses clean tag-based format:

```
User message content with natural line breaks

<AI_INTERACTION_ATTACHED_FILES>
FOLDERS:
- workspace_name/relative/path/to/folder

FILES:
- workspace_name/relative/path/to/file.js
</AI_INTERACTION_ATTACHED_FILES>

<AI_INTERACTION_WORKSPACE>workspace_name</AI_INTERACTION_WORKSPACE>
<AI_INTERACTION_CONTINUE_CHAT>true/false</AI_INTERACTION_CONTINUE_CHAT>
```

**Note**: When images are attached, they are automatically converted to base64 format and included in the response for AI processing.

## 🔧 Troubleshooting

### Common Issues

1. **"Command not found" error**
   - Check Python is installed and in PATH
   - Verify absolute path in MCP config

2. **"Module not found" error**
   - Run `pip install -r requirements.txt`
   - Check virtual environment if using one

3. **UI not displaying**
   - Ensure PyQt5 is installed correctly
   - Check display settings and desktop environment

4. **File attachment not working**
   - Verify file permissions and access rights
   - Check workspace path configuration

5. **🖼️ Image attachment issues**
   - Ensure PyQt5 is properly installed for image processing
   - Check `user_images/` directory permissions
   - Verify image formats: PNG, JPG, JPEG, GIF, BMP, WEBP supported
   - Clear config if images not loading: Remove `last_attached_images` from config.json

6. **MCP Connection Issues in Cursor**
   - Verify MCP server configuration in Cursor settings
   - Check process running with `ps aux | grep mcp_server`
   - Restart Cursor after config changes

### Debug Mode
To debug issues, run server directly:
```bash
python mcp_server.py
```

For Cursor debugging:
```bash
# Check MCP server logs in Cursor
# Open Developer Tools → Console
# Look for MCP connection messages
```

## 🔄 Version History

- **v2.2.0** (Latest): 🖼️ **Image Attachment System** - Complete image support with drag & drop, multi-image management, security enhancements, and persistent state
- **v2.1.0**: Enhanced UI/UX, Cursor IDE integration, Debounce config system
- **v2.0.0**: Refactored architecture with modern PyQt5 UI  
- **v1.x**: Core functionality and basic features

### 🎯 **v2.2.0 Detailed Changes:**
- ✅ **Image Attachment UI**: Full drag & drop interface with preview system
- ✅ **Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, WEBP compatibility
- ✅ **Security Hardening**: Secure path storage, local-only processing
- ✅ **Database Management**: Auto-cleanup, persistent storage, state management
- ✅ **UX Improvements**: Click-to-enlarge, remove buttons, checkbox persistence
- ✅ **Performance**: Optimized image loading with base64 conversion
- ✅ **Bug Fixes**: Checkbox state persistence, config loading issues resolved

## 🎯 Integration Workflow & System Architecture

### 🔄 **Complete Integration Flow:**
```
[User Input] → [ai_interaction Tool] → [Tag-based Output] → [AI Agent Rules] → [Enhanced Response]
     ↑                                                                              ↓
     └─────────────── [Auto-recall if continue_chat=true] ←─────────────────────────┘
```

### 🧠 **Cognitive Enhancement System:**
- **Standard Mode**: High-level thinking with 1+ thinking blocks
- **Ultra-Enhancement Mode**: 10 breakthrough cognitive modes simultaneously
  - Quantum Cognitive Mode
  - Meta-Cognitive Orchestration  
  - Expert Persona Simulation
  - Time-Dilated Processing
  - Systems-Level Integration
  - Psychological Priming Mode
  - Maximum Cognitive Resource Allocation
  - Adversarial Self-Testing Mode
  - Obsessive Quality Standards
  - Breakthrough Innovation Mode

### 📊 **Output Tag System:**
```xml
<AI_INTERACTION_CONTINUE_CHAT>true/false</AI_INTERACTION_CONTINUE_CHAT>
<AI_INTERACTION_ATTACHED_FILES>
FOLDERS:
- workspace_name/relative/path/folder
FILES:  
- workspace_name/relative/path/file.ext
</AI_INTERACTION_ATTACHED_FILES>
<AI_INTERACTION_WORKSPACE>workspace_name</AI_INTERACTION_WORKSPACE>
```

## 💡 Advanced Features & Best Practices

### 🎨 **UI/UX Enhancements:**
- **Responsive Design**: Adaptive sizing with minimum 800x700 resolution
- **Multi-language Support**: Seamless EN/VI switching with persistent config
- **Modern PyQt5 Styling**: Semantic color system with button properties
- **File Drag-Drop**: Intuitive file attachment with validation
- **Context Menu**: Right-click operations for file management
- **Debounce Saving**: Smart config persistence with QTimer optimization

### 🔧 **Technical Specifications:**
- **Python**: 3.8+ required with PyQt5 dependencies
- **Memory**: Minimum 512MB RAM for UI components
- **Storage**: ~50MB for tool installation and config
- **Platform**: Cross-platform (Windows/macOS/Linux) with native styling
- **Performance**: Event-driven architecture with minimal CPU usage

### 📈 **Performance Optimization:**
- **Lazy Loading**: Components load only when needed
- **Efficient Config**: JSON-based with automatic compression
- **Resource Management**: Proper cleanup and memory management
- **Caching Strategy**: Workspace state persistence for faster startup

## 🛡️ Security & Privacy

### 🔒 **Security Features:**
- **Local Processing**: All file operations are local only, no uploads
- **Path Validation**: Robust security checks for file access
- **Sandboxed Execution**: Tool runs in controlled environment
- **No Data Collection**: Zero telemetry or external data transmission

### 🔐 **Privacy Protection:**
- **Config Encryption**: Local config with secure storage options
- **File Access Control**: User-controlled file attachment permissions
- **Workspace Isolation**: Project boundaries are enforced
- **Audit Trail**: Optional logging for security monitoring

## 🌟 System Requirements & Compatibility

### 💻 **Minimum System Requirements:**
```
OS: Windows 10+ / macOS 10.14+ / Ubuntu 18.04+
Python: 3.8 or higher
RAM: 512MB available
Storage: 100MB free space
Display: 1024x768 minimum resolution
```

### 🎯 **Recommended Setup:**
```
OS: Windows 11 / macOS 12+ / Ubuntu 20.04+
Python: 3.10+ with virtual environment
RAM: 2GB available  
Storage: 500MB free space
Display: 1920x1080 or higher
GPU: Optional for enhanced UI rendering
```

### 🔧 **Compatibility Matrix:**
| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| Python | 3.8-3.11 | ✅ Tested | Recommended 3.10+ |
| PyQt5 | 5.15+ | ✅ Required | Core UI framework |
| Claude Desktop | Latest | ✅ Optimized | MCP integration |
| **Cursor IDE** | **Latest** | **🚀 Recommended** | **AI-first development** |
| VS Code | Any | ✅ Compatible | Alternative IDE option |

## 🤝 Contributing

**Note**: This is a private repository. Only the owner has push access.

For suggestions or issues:
1. Create detailed issue reports
2. Provide reproduction steps
3. Include system information
4. Attach relevant logs or screenshots

## 📚 Documentation & Resources

### 📖 **Documentation Files:**
- `rule_for_ai_VI.txt` - Vietnamese agent behavior rules
- `rule_for_ai_EN.txt` - English agent behavior rules
- `SYSTEM_PROMPT_Claude-4-sonnet-max.txt` - Full system prompt example
- `pyproject.toml` - Project configuration and dependencies

### 🔗 **Useful Links:**
- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop Official Guide](https://claude.ai/desktop)
- [Cursor IDE Official Site](https://cursor.sh/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython-5/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

### 💡 **Related Projects:**
[- https://github.com/KhaiHuynhVN/mcp-server-agent-comm](https://github.com/KhaiHuynhVN/mcp-server-agent-comm)

## 📄 License & Legal

### 📜 **License:**
```
MIT License

Copyright (c) 2025 DemonVN - AI Interaction Tool
```

### ⚖️ **Legal Notes:**
- Tool complies with local processing requirements
- No personal data collection
- Respects user privacy and data sovereignty
- Compatible with enterprise security policies

### 🎯 **Special Thanks:**
- Model Context Protocol team for standardized interface
- Claude Desktop integration ecosystem
- Cursor IDE team for AI-first development tools
- Open source Python community
- Beta testers and early adopters

### 🔥 **Inspiration:**
Project inspired by the need for seamless AI interaction tools with modern UX principles and professional-grade architecture.

---

**🚀 Happy Coding with AI Interaction Tool!**

*For support, issues, or feature requests, please open an issue on the GitHub repository.*

