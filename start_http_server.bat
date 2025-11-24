@echo off
echo ========================================
echo   AI Interaction MCP Server (HTTP Mode)
echo   For Antigravity Compatibility
echo ========================================
echo.
echo Starting MCP server in HTTP SSE mode...
echo Server will run on http://127.0.0.1:8000
echo.

cd /d "E:\MCP-servers-github\AI-interaction"
python mcp_server_http.py

pause
