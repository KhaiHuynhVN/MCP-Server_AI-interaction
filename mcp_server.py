import sys
import os
import logging

# ============================================================================
# CRITICAL FIX: Completely disable ALL stderr output for MCP stdio transport
# ============================================================================
# MCP uses stdin/stdout for JSON-RPC communication. FastMCP library logs to 
# stderr which corrupts the stream and causes BrokenResourceError.
# We must suppress stderr PERMANENTLY for the entire server lifetime.
# ============================================================================

# Redirect stderr to devnull PERMANENTLY
_devnull = open(os.devnull, 'w', encoding='utf-8')
sys.stderr = _devnull

# Also disable Python logging completely
logging.disable(logging.CRITICAL)

# Disable FastMCP logging if it has any
os.environ['PYTHONUNBUFFERED'] = '0'

# Disable exception traceback printing completely
# This prevents uncaught exceptions from printing to stderr
def silent_excepthook(_exc_type, _exc_value, _exc_traceback):
    """Silent exception hook - suppresses all exception output"""
    return  # Do nothing - no stderr output

sys.excepthook = silent_excepthook

# Also set threading excepthook for background threads (Python 3.8+)
import threading
def silent_threading_excepthook(_args):
    """Silent threading exception hook"""
    return  # Do nothing

# Only set if available (Python 3.8+)
if hasattr(threading, 'excepthook'):
    threading.excepthook = silent_threading_excepthook

# ============================================================================
# Now import everything - no logs will appear
# ============================================================================
from mcp.server.fastmcp import FastMCP
from ai_interaction_tool.core import ai_interaction_tool, get_tool_description

# Tạo MCP server
mcp = FastMCP("AI Interaction")

mcp.add_tool(ai_interaction_tool, description=get_tool_description())

if __name__ == "__main__":
    # Chạy server với transport=stdio
    # stderr remains suppressed throughout entire runtime
    mcp.run(transport="stdio")
    