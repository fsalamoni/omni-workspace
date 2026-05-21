from typing import Dict, Any, List
from .client import MCPClient

class MCPHub:
    """Registry for MCP Servers."""
    
    def __init__(self):
        self.servers: Dict[str, MCPClient] = {}
        
    async def register_server(self, config: Dict[str, Any]):
        name = config.get("name")
        command = config.get("command")
        args = config.get("args", [])
        
        if not name or not command:
            raise ValueError("Server config must include 'name' and 'command'")
            
        client = MCPClient(name, command, args)
        await client.connect()
        self.servers[name] = client
        
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        tools = []
        for server in self.servers.values():
            tools.extend(await server.list_tools())
        return tools
        
    async def route_tool_call(self, server_name: str, tool_name: str, args: Dict[str, Any]) -> Any:
        server = self.servers.get(server_name)
        if not server:
            raise ValueError(f"Server {server_name} not found")
        return await server.call_tool(tool_name, args)
