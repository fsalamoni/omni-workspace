@echo off
echo ====================================================
echo    Iniciando OmniWorkspace (Powered by AionUI)
echo ====================================================

echo [1/2] Iniciando Servidor Python MCP em background...
start /B "" "D:\SalomoneWorkspace\omni-workspace\backend\.venv\Scripts\python.exe" "d:\SalomoneWorkspace\omni-workspace\backend\src\mcp_server.py"

echo [2/2] Iniciando AionUI WebUI...
cd frontend
bun run server:start
