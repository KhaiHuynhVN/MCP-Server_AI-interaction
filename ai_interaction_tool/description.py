"""
Mô tả chi tiết cho công cụ AI Interaction Tool
"""

AI_INTERACTION_DESCRIPTION = """
🚀 AI_INTERACTION TOOL - INTEGRATION WITH SYSTEM PROMPT RULES 🚀
=======================================================================
📋 OUTPUT FORMAT - CLEAN TAG-BASED:
<user content with natural line breaks>

<AI_INTERACTION_ATTACHED_FILES>
FOLDERS:
- workspace_name/relative/path/to/folder

FILES:
- workspace_name/relative/path/to/file.js

</AI_INTERACTION_ATTACHED_FILES>

<AI_INTERACTION_WORKSPACE>workspace_name</AI_INTERACTION_WORKSPACE>
<AI_INTERACTION_CONTINUE_CHAT>true/false</AI_INTERACTION_CONTINUE_CHAT>

🔧 WORKSPACE PATH PROCESSING:
- Input format: "workspace_name/relative_path_from_workspace_root"
- Agent workspace detection logic:
  * CÙNG workspace → BỎ TIỀN TỐ workspace_name, dùng relative_path
  * KHÁC workspace → DÙNG NGUYÊN đường dẫn từ ai_interaction

📁 WORKSPACE HANDLING EXAMPLES:
- Cùng workspace: "ALT-WebClientV3/src/components/login/index.js" 
  → Agent processes: "src/components/login/index.js"
- Khác workspace: "AI-interaction/ai_interaction_tool/description.py" 
  → Agent processes: "AI-interaction/ai_interaction_tool/description.py"

⚠️ CRITICAL CONTROL TAGS:
- **<AI_INTERACTION_CONTINUE_CHAT>**: true = MANDATORY recall ai_interaction tool
- **<AI_INTERACTION_ATTACHED_FILES>**: Present only when files/folders attached
- **<AI_INTERACTION_WORKSPACE>**: Present only when files/folders attached

🚀 SYSTEM ARCHITECTURE:
[User Input] → [ai_interaction Tool] → [Pseudo-Object] → [System Prompt Rules] → [Enhanced AI Response]

⭐ DESIGN HIGHLIGHT:
Tool được thiết kế để integrate với system prompt rules framework, tạo ra effective AI interaction architecture!
=======================================================================
""" 