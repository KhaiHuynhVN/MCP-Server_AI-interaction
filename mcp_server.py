import sys
import os

# ============================================================================
# CRITICAL: Suppress stderr during imports to prevent corrupting MCP stdio
# ============================================================================
# MCP uses stdio for JSON-RPC. ANY stderr output during imports will corrupt it.
# We suppress ONLY during import phase, then restore before mcp.run().
# ============================================================================

# Save original stderr
_original_stderr = sys.stderr

# Temporarily redirect stderr to devnull during imports
_devnull = open(os.devnull, 'w')
sys.stderr = _devnull

try:
    # ============================================================================
    # Import everything while stderr is suppressed
    # ============================================================================
    from mcp.server.fastmcp import FastMCP
    from ai_interaction_tool.core import ai_interaction_tool, get_tool_description
    
finally:
    # ============================================================================
    # RESTORE stderr before running MCP server
    # ============================================================================
    sys.stderr = _original_stderr
    _devnull.close()

# Tạo MCP server
mcp = FastMCP("AI Interaction")

mcp.add_tool(ai_interaction_tool, description=get_tool_description())

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")