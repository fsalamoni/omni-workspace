import asyncio
import os
from typing import Optional, Dict, Any
from .base import BaseTool, ToolResult
from ..sandbox.models import SandboxAction

class TerminalTool(BaseTool):
    """Tool for executing shell commands."""
    
    def __init__(self, workspace_dir: str, docker_workspace=None, session_id: str=None):
        super().__init__(
            name="terminal",
            description="Executes a shell command.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Optional timeout in seconds."
                    }
                },
                "required": ["command"]
            }
        )
        self.workspace_dir = workspace_dir
        self.docker_workspace = docker_workspace
        self.session_id = session_id

    async def execute(self, command: str, timeout: int = 60, **kwargs) -> ToolResult:
        if self.docker_workspace and self.session_id:
            # Execute in Docker Sandbox
            action = SandboxAction(command=command, action_type="bash", timeout=timeout)
            obs = await self.docker_workspace.execute(self.session_id, action)
            output = f"Exit code: {obs.exit_code}\nSTDOUT:\n{obs.stdout}\nSTDERR:\n{obs.stderr}"
            return ToolResult(output=output, error=obs.stderr if obs.exit_code != 0 else "", metadata={"exit_code": obs.exit_code})

        # Local Fallback
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace_dir,
                env={**os.environ, "TERM": "xterm-256color"}
            )
            
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                stdout = stdout_bytes.decode('utf-8', errors='replace')
                stderr = stderr_bytes.decode('utf-8', errors='replace')
                exit_code = proc.returncode
                
                output = f"Exit code: {exit_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                return ToolResult(output=output, metadata={"exit_code": exit_code})
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(output="", error=f"Command timed out after {timeout} seconds")
        except Exception as e:
            return ToolResult(output="", error=str(e))
