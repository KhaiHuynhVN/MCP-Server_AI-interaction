# Main engine for AI Interaction Tool
# Refactored version - uses components from separate modules
from PyQt5 import QtWidgets, QtGui
import sys
import json
import uuid
import time
from .core.dialog import InputDialog
from .core.communication_bridge import get_bridge

# Legacy classes for backward compatibility (now imported from separate modules)
from .ui.file_tree import FileSystemModel, FileTreeView, FileTreeDelegate
from .ui.file_dialog import FileAttachDialog

def run_ui(*args, **kwargs):
    """
    Original UI mode - called by MCP tool for backward compatibility
    Now communicates with persistent UI if available, otherwise falls back to popup mode
    """
    # Try to communicate with persistent UI first
    bridge = get_bridge()
    request_id = str(uuid.uuid4())
    
    # Create timestamp file for countdown timer
    _create_countdown_timestamp_file()
    
    # Send request to persistent UI  
    # Dynamic timeout: ensure bridge timeout > agent keepalive timeout to prevent race condition
    from .constants import AGENT_AUTO_KEEPALIVE_SECONDS
    dynamic_timeout = max(300, AGENT_AUTO_KEEPALIVE_SECONDS + 60)  # At least 1 minute buffer
    response = bridge.send_request(request_id, timeout=dynamic_timeout)
    
    if response is not None:
        # Got response from persistent UI - response is now dict with content and continue_chat
        if isinstance(response, dict):
            # Extract content and continue_chat from response dict
            content = response.get("content", "")
            continue_chat = response.get("continue_chat", False)
        else:
            # Fallback for old string response (shouldn't happen)
            content = response
            continue_chat = False
        
        # Process response exactly like original popup mode
        return process_ui_response(content, continue_chat)
    else:
        # No response from persistent UI - send keep-alive message instead of opening popup
        # This prevents opening UI without auto keep-alive feature
        import random
        from .core.config import ConfigManager
        from .utils.translations import get_translation
        
        # Get current language
        try:
            config_manager = ConfigManager()
            current_language = config_manager.get_language()
        except Exception:
            current_language = "en"
        
        # Random template selection (1-10) to avoid spam detection
        random_variation = random.randint(1, 10)
        
        # Get auto keep-alive message template
        keepalive_message = get_translation(
            current_language, 
            "auto_keepalive_message", 
            random_variation
        )
        
        # Return keep-alive message with continue_chat=true to maintain conversation
        return process_ui_response(keepalive_message, continue_chat=True)

def process_ui_response(text, continue_chat):
    """
    Process UI response - shared logic between popup and persistent modes
    """
    if text:
        # Phân tích nội dung từ dialog
        try:
            # Parse JSON từ kết quả của dialog
            result_dict = json.loads(text)
            user_text = result_dict.get("text", "")
            attached_files = result_dict.get("attached_files", [])
            attached_images = result_dict.get("attached_images", [])
            language = result_dict.get("language", "vi")  # Mặc định tiếng Việt
            # ====== THINKING LOGIC COMPLETELY REMOVED - Natural Behavior ======
            
            # Check if we have images - return structured data for MCP processing
            if attached_images:
                return {
                    'text_content': user_text,
                    'attached_files': attached_files,
                    'attached_images': attached_images,
                    'continue_chat': continue_chat,
                    'language': language
                }
            
            # ====== TAG-BASED FORMAT - Clean and Simple ======
            # Start with clean user content
            full_response_text = user_text
            
            # Add attached files using collision-proof structured format
            if attached_files:
                full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
                workspace_name = None
                
                # Separate files and folders
                folders = []
                files = []
                errors = []
                
                for file_info in attached_files:
                    if "relative_path" in file_info:
                        relative_path = file_info.get('relative_path', 'unknown_path')
                        item_type = file_info.get('type', 'unknown')
                        workspace_name = file_info.get('workspace_name', '')
                        
                        if item_type.lower() == 'folder':
                            folders.append(relative_path)
                        elif item_type.lower() == 'file':
                            files.append(relative_path)
                    elif "error" in file_info:
                        error_name = file_info.get('name', 'unknown')
                        error_msg = file_info.get('error', 'Unknown error')
                        errors.append(f"{error_name} - {error_msg}")
                
                # Output structured sections
                if folders:
                    full_response_text += "FOLDERS:\n"
                    for folder in folders:
                        full_response_text += f"- {folder}\n"
                    full_response_text += "\n"
                
                if files:
                    full_response_text += "FILES:\n"
                    for file in files:
                        full_response_text += f"- {file}\n"
                    full_response_text += "\n"
                
                if errors:
                    full_response_text += "ERRORS:\n"
                    for error in errors:
                        full_response_text += f"- {error}\n"
                    full_response_text += "\n"
                
                full_response_text += "</AI_INTERACTION_ATTACHED_FILES>\n"
                
                # Add workspace info
                if workspace_name:
                    full_response_text += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
            
            # Add control tags at the end
            full_response_text += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
            return full_response_text
            
        except json.JSONDecodeError:
            # Handle non-JSON case with clean tag format
            result_text = text
            result_text += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
            return result_text
    else:
        # Empty case with clean tag format
        return """
<AI_INTERACTION_CONTINUE_CHAT>false</AI_INTERACTION_CONTINUE_CHAT>"""

def run_popup_ui(*args, **kwargs):
    """
    DEPRECATED: Original popup UI mode - creates temporary dialog
    
    WARNING: This function should NOT be used anymore!
    It creates UI without auto keep-alive feature, which causes issues.
    
    Use persistent UI mode instead, or return keep-alive message.
    This function is kept only for backward compatibility.
    """
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Thiết lập font mặc định cho toàn ứng dụng
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)
    
    text, continue_chat, ok = InputDialog.getText()

    if ok:
        return process_ui_response(text, continue_chat)
    else:
        return process_ui_response("", False)

def run_persistent_ui():
    """
    Persistent UI mode - runs continuously and communicates via bridge
    Called by CLI command to launch persistent interface
    """
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Thiết lập font mặc định cho toàn ứng dụng
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Import here to avoid circular import
    from .core.dialog import PersistentInputDialog
    
    # Create persistent dialog
    dialog = PersistentInputDialog()
    dialog.show()
    
    # Start Qt event loop
    return app.exec_()

def _create_countdown_timestamp_file():
    """Create timestamp file when agent calls tool for countdown timer"""
    import os
    from .constants import AGENT_AUTO_KEEPALIVE_SECONDS
    
    # Create timestamp file in current workspace directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp_file = os.path.join(current_dir, "ai_interaction_countdown.json")
    
    timestamp_data = {
        "start_time": time.time(),
        "timeout_seconds": AGENT_AUTO_KEEPALIVE_SECONDS
    }
    
    try:
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            json.dump(timestamp_data, f, ensure_ascii=False, indent=2)
        # Debug: print success
        print(f"Countdown file created: {timestamp_file}", file=sys.stderr)
    except Exception as e:
        # Debug: print error
        print(f"Error creating countdown file: {e}", file=sys.stderr)
        pass  # Ignore errors, countdown will just not work

def get_countdown_remaining_time():
    """Get remaining countdown time from timestamp file"""
    import os
    from .constants import AGENT_AUTO_KEEPALIVE_SECONDS
    
    # Read timestamp file from workspace directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp_file = os.path.join(current_dir, "ai_interaction_countdown.json")
    
    try:
        if os.path.exists(timestamp_file):
            with open(timestamp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            start_time = data.get("start_time", 0)
            timeout_seconds = data.get("timeout_seconds", AGENT_AUTO_KEEPALIVE_SECONDS)
            
            elapsed = time.time() - start_time
            remaining = timeout_seconds - elapsed
            
            print(f"Countdown file found: elapsed={elapsed:.1f}s, remaining={remaining:.1f}s", file=sys.stderr)
            
            if remaining > 0:
                return remaining
            else:
                # Expired, remove file
                print("Countdown expired, removing file", file=sys.stderr)
                os.remove(timestamp_file)
                return None
        else:
            print(f"Countdown file not found: {timestamp_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading countdown file: {e}", file=sys.stderr)
        pass
    
    return None

def clear_countdown_timestamp_file():
    """Clear countdown timestamp file when response is sent"""
    import os
    
    # Clear timestamp file from workspace directory (same as create function)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp_file = os.path.join(current_dir, "ai_interaction_countdown.json")
    
    try:
        if os.path.exists(timestamp_file):
            os.remove(timestamp_file)
    except Exception:
        pass