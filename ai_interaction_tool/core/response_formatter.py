"""
Response formatting utilities for AI Interaction Tool
Handles mixed content responses with text, images, and control tags
"""

from mcp.types import TextContent, ImageContent
from typing import List, Dict, Any, Union
from ..utils.image_processing import process_images


def format_mixed_response(result: Dict[str, Any]) -> List[Union[TextContent, ImageContent]]:
    """
    Format response containing both text and images with control tags
    """
    response_items = []
    
    user_text = result.get('text_content', '')
    attached_files = result.get('attached_files', [])
    attached_images = result.get('attached_images', [])
    continue_chat = result.get('continue_chat', False)

    full_text_content = _build_text_content_with_tags(
        user_text, attached_files, continue_chat
    )
    
    response_items.append(TextContent(type="text", text=full_text_content))
    
    if attached_images:
        mcp_images = process_images(attached_images)
        response_items.extend(mcp_images)
    
    return response_items


def format_text_only_response(result: Union[str, Dict[str, Any]]) -> List[TextContent]:
    """
    Format simple text-only response
    
    Args:
        result: String or dictionary containing text response
        
    Returns:
        List containing single TextContent object
    """
    return [TextContent(type="text", text=str(result))]


def _build_text_content_with_tags(
    user_text: str, 
    attached_files: List[Dict], 
    continue_chat: bool
) -> str:
    """
    Build complete text content with attached files and control tags
    
    Args:
        user_text: Main user message text
        attached_files: List of attached file information
        continue_chat: Whether to continue chat
        
    Returns:
        String containing formatted text with all tags
    """
    full_text_content = user_text
    
    # Add attached files section if any
    if attached_files:
        full_text_content += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
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
            full_text_content += "FOLDERS:\n"
            for folder in folders:
                full_text_content += f"- {folder}\n"
            full_text_content += "\n"
        
        if files:
            full_text_content += "FILES:\n"
            for file in files:
                full_text_content += f"- {file}\n"
            full_text_content += "\n"
        
        if errors:
            full_text_content += "ERRORS:\n"
            for error in errors:
                full_text_content += f"- {error}\n"
            full_text_content += "\n"
        
        full_text_content += "</AI_INTERACTION_ATTACHED_FILES>\n"
        
        # Add workspace info
        if workspace_name:
            full_text_content += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
    
    # Add control tags at the end (CRITICAL for agent behavior)
    full_text_content += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
    
    return full_text_content


def build_error_response(error_message: str) -> List[TextContent]:
    """
    Build standardized error response
    
    Args:
        error_message: Error message to display
        
    Returns:
        List containing error TextContent
    """
    return [TextContent(type="text", text=f"Error: {error_message}")]


def validate_response_data(result: Any) -> tuple[bool, str]:
    """
    Validate response data structure
    
    Args:
        result: Response data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if result is None:
        return False, "Result is None"
    
    if isinstance(result, str):
        return True, ""
    
    if isinstance(result, dict):
        # Check for required fields in structured response
        if 'attached_images' in result:
            # This should be a mixed response
            if not isinstance(result['attached_images'], list):
                return False, "attached_images must be a list"
            
            # Validate image data structure
            for img in result['attached_images']:
                if not isinstance(img, dict):
                    return False, "Each image must be a dictionary"
                if 'base64_data' not in img:
                    return False, "Image missing base64_data field"
        
        return True, ""
    
    return False, f"Unsupported result type: {type(result)}" 