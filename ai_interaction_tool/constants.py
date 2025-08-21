# Constants for AI Interaction Tool
import os

# Window settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 750
MIN_INPUT_HEIGHT = 200
MAX_FILE_LIST_HEIGHT = 80

# File settings
CONFIG_FILENAME = "config.json"
SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

# UI settings
TREE_DEPTH_EXPANSION = 0
SHADOW_BLUR_RADIUS = 15
SHADOW_OFFSET = (0, 0)
SHADOW_OPACITY = 80

# Default paths
DEFAULT_PATH = os.path.expanduser("~")

# File settings - không giới hạn gì cả để sử dụng tự do
# (Có thể uncomment và điều chỉnh nếu gặp performance issues)
# MAX_FILE_SIZE_MB = 100  
# MAX_ATTACHMENT_SIZE_MB = 10000

# Languages
SUPPORTED_LANGUAGES = ["en", "vi"]
DEFAULT_LANGUAGE = "en" 

# Auto keep-alive settings
AUTO_KEEPALIVE_MINUTES = 10  # Thời gian timeout cho auto keep-alive feature (phút) 