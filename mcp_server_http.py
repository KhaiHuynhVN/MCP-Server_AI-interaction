from mcp.server.fastmcp import FastMCP
# Import MCP tool function and description from ai_interaction_tool
from ai_interaction_tool.core import ai_interaction_tool, get_tool_description

# Tạo MCP server
mcp = FastMCP("AI Interaction")

mcp.add_tool(ai_interaction_tool, description=get_tool_description())

if __name__ == "__main__":
    # Chạy server với SSE transport trên HTTP
    # File này dành riêng cho Antigravity (để tránh vấn đề stdio trên Windows)
    # Các IDE khác (VSCode, Cursor) vẫn dùng mcp_server.py với stdio mode
    print("🚀 Starting AI Interaction MCP Server (HTTP Mode for Antigravity)", flush=True)
    print("📡 Server: http://127.0.0.1:8000", flush=True)
    print("📡 SSE endpoint: http://127.0.0.1:8000/sse", flush=True)
    print("⚠️  This is the HTTP version for Antigravity compatibility", flush=True)
    print("Press Ctrl+C to stop the server\n", flush=True)
    
    mcp.run(transport="sse")
