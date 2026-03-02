"""
Image processing utilities for AI Interaction Tool
Handles conversion of base64 image data to MCP ImageContent objects
"""

from mcp.types import ImageContent
import base64
import sys
from typing import List, Dict, Any

MIME_TYPE_MAP = {
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
}


def process_images(images_data: List[dict]) -> List[ImageContent]:
    """
    Process image data and convert to MCP ImageContent objects
    
    Args:
        images_data: List of image dictionaries containing base64_data, media_type, filename
        
    Returns:
        List[ImageContent]: Processed MCP ImageContent objects ready for server response
    """
    mcp_images = []
    
    for i, img in enumerate(images_data, 1):
        try:
            if not img.get("base64_data"):
                continue
            
            if not isinstance(img["base64_data"], str):
                continue
            
            image_bytes = base64.b64decode(img["base64_data"])
            if len(image_bytes) == 0:
                continue
            
            media_type = img.get("media_type", "image/png")
            filename = img.get("filename", "image.png")
            
            if "jpeg" in media_type or "jpg" in media_type or filename.lower().endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            elif "gif" in media_type or filename.lower().endswith('.gif'):
                mime_type = "image/gif"
            elif "webp" in media_type or filename.lower().endswith('.webp'):
                mime_type = "image/webp"
            else:
                mime_type = "image/png"
            
            b64_str = base64.b64encode(image_bytes).decode('utf-8')
            mcp_images.append(ImageContent(type="image", data=b64_str, mimeType=mime_type))
            
        except Exception:
            continue
    
    return mcp_images


def validate_image_data(image_data: dict) -> bool:
    """
    Validate if image data is properly formatted
    
    Args:
        image_data: Dictionary containing image information
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["base64_data"]
    
    for field in required_fields:
        if field not in image_data or not image_data[field]:
            return False
    
    # Check if base64_data is valid string
    if not isinstance(image_data["base64_data"], str):
        return False
    
    try:
        # Try to decode base64 to verify it's valid
        base64.b64decode(image_data["base64_data"])
        return True
    except Exception:
        return False


def get_image_info(image_data: dict) -> Dict[str, Any]:
    """
    Extract detailed information about an image
    
    Args:
        image_data: Dictionary containing image information
        
    Returns:
        Dict containing image metadata
    """
    info = {
        "media_type": image_data.get("media_type", "image/png"),
        "filename": image_data.get("filename", "image.png"),
        "size_bytes": 0,
        "format": "unknown",
        "is_valid": False
    }
    
    if validate_image_data(image_data):
        try:
            image_bytes = base64.b64decode(image_data["base64_data"])
            info["size_bytes"] = len(image_bytes)
            info["is_valid"] = True
            
            # Determine format
            media_type = info["media_type"]
            filename = info["filename"]
            
            if "jpeg" in media_type or "jpg" in media_type or filename.lower().endswith(('.jpg', '.jpeg')):
                info["format"] = 'jpeg'
            elif "gif" in media_type or filename.lower().endswith('.gif'):
                info["format"] = 'gif'
            else:
                info["format"] = 'png'
                
        except Exception as e:
            # print(f"Error getting image info: {e}", file=sys.stderr)
            pass  # Silently ignore to avoid breaking MCP stdio
    
    return info 