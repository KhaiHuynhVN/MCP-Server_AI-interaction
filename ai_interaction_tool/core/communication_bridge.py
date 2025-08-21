# Communication Bridge for Persistent UI Mode
import os
import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile

class CommunicationBridge:
    """
    Handles communication between MCP tool calls and persistent UI
    Using file-based communication for simplicity and reliability
    """
    
    def __init__(self, bridge_dir: Optional[str] = None):
        if bridge_dir is None:
            # Use temp directory for communication files
            self.bridge_dir = os.path.join(tempfile.gettempdir(), "ai_interaction_bridge")
        else:
            self.bridge_dir = bridge_dir
        
        # Ensure bridge directory exists
        os.makedirs(self.bridge_dir, exist_ok=True)
        
        # Communication files
        self.request_file = os.path.join(self.bridge_dir, "request.json")
        self.response_file = os.path.join(self.bridge_dir, "response.json")
        self.status_file = os.path.join(self.bridge_dir, "status.json")
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def send_request(self, request_id: str, timeout: int = 300) -> Optional[str]:
        """
        Send request to persistent UI and wait for response
        Called by MCP tool when agent calls the tool
        
        Args:
            request_id: Unique identifier for this request
            timeout: Maximum seconds to wait for response
            
        Returns:
            Response string from UI or None if timeout
        """
        with self._lock:
            # Write request signal
            request_data = {
                "id": request_id,
                "timestamp": time.time(),
                "status": "waiting"
            }
            
            with open(self.request_file, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)
            
            # Update status to indicate waiting for input
            self._update_status("waiting_for_input", request_id)
        
        # Wait for response with timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(self.response_file):
                try:
                    with open(self.response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    # Check if response is for our request
                    if response_data.get("request_id") == request_id:
                        # Clean up response file
                        os.remove(self.response_file)
                        self._update_status("idle")
                        # Return complete response data instead of just content
                        return {
                            "content": response_data.get("content", ""),
                            "continue_chat": response_data.get("continue_chat", False)
                        }
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            time.sleep(0.1)  # Check every 100ms
        
        # Timeout occurred
        self._update_status("timeout", request_id)
        return None
    
    def send_response(self, request_id: str, content: str, continue_chat: bool = False) -> bool:
        """
        Send response from persistent UI to waiting tool
        Called by persistent UI when user submits message
        
        Args:
            request_id: Request ID this response belongs to
            content: Response content from user
            continue_chat: Whether to continue the chat
            
        Returns:
            True if response sent successfully
        """
        try:
            response_data = {
                "request_id": request_id,
                "content": content,
                "continue_chat": continue_chat,
                "timestamp": time.time()
            }
            
            with open(self.response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            
            # Also update status with continue_chat info
            self._update_status("response_sent", request_id, continue_chat)
            
            return True
            
        except Exception:
            return False
    
    def get_current_request(self) -> Optional[Dict[str, Any]]:
        """
        Get current pending request
        Called by persistent UI to check if there's a waiting request
        
        Returns:
            Request data or None if no pending request
        """
        try:
            if os.path.exists(self.request_file):
                with open(self.request_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current communication status
        
        Returns:
            Status information
        """
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return {"status": "idle"}
    
    def _update_status(self, status: str, request_id: Optional[str] = None, continue_chat: Optional[bool] = None):
        """Update status file with current state"""
        status_data = {
            "status": status,
            "timestamp": time.time()
        }
        
        if request_id:
            status_data["request_id"] = request_id
            
        if continue_chat is not None:
            status_data["continue_chat"] = continue_chat
        
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def cleanup(self):
        """Clean up communication files"""
        files_to_remove = [self.request_file, self.response_file, self.status_file]
        
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass

# Global bridge instance
_bridge = None

def get_bridge() -> CommunicationBridge:
    """Get global communication bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = CommunicationBridge()
    return _bridge
