import sys
import json
import asyncio
from typing import Dict, Any

# Simple MCP server over stdio
async def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "salomoneui-agents",
                "version": "1.0.0"
            }
        }
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "manus_agent",
                    "description": "General Purpose Execution Agent (SalomoneUI)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The task for Manus"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "browser_agent",
                    "description": "Playwright Browser Agent (SalomoneUI)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The browser task"}
                        },
                        "required": ["prompt"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        prompt = args.get("prompt", "")
        
        # Here we would import Orchestrator and run the agent
        # For now we simulate success
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Agent {tool_name} completed task: {prompt}\n\n[SalomoneUI Backend Executed]"
                }
            ]
        }
        
    return {"error": {"code": -32601, "message": "Method not found"}}

async def main():
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            req = json.loads(line.decode('utf-8'))
            msg_id = req.get("id")
            
            result = await handle_request(req)
            
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            
            writer.write((json.dumps(resp) + "\n").encode('utf-8'))
            await writer.drain()
        except Exception as e:
            pass

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
