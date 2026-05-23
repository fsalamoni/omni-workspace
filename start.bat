@echo off
echo ====================================================
echo    Iniciando SalomoneUI (Powered by SalomoneUI)
echo ====================================================

echo [1/2] Iniciando Servidor Python MCP em background...
start /B "" "D:\SalomoneWorkspace\salomoneui\backend\.venv\Scripts\python.exe" "d:\SalomoneWorkspace\salomoneui\backend\src\mcp_server.py"

echo [2/2] Iniciando SalomoneUI WebUI...
cd frontend
bun run server:start
