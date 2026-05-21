"""PythonExecute tool — run Python code in a subprocess with timeout."""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Any

from src.tools.base import BaseTool, ToolResult
from src.sandbox.models import SandboxAction

class PythonExecute(BaseTool):
    """Execute Python code in an isolated subprocess or Docker Sandbox."""

    name: str = "python_execute"
    description: str = (
        "Execute Python code and return the output. "
        "Use this for calculations, data processing, file manipulation, "
        "or any task best solved with Python. Print results to stdout."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute.",
            },
            "timeout": {
                "type": "integer",
                "description": "Maximum execution time in seconds (default 30).",
                "default": 30,
            },
        },
        "required": ["code"],
    }

    def __init__(self, default_timeout: int = 30, docker_workspace=None, session_id: str=None) -> None:
        self._default_timeout = default_timeout
        self.docker_workspace = docker_workspace
        self.session_id = session_id

    async def execute(self, **kwargs: Any) -> ToolResult:
        code: str = kwargs.get("code", "")
        timeout: int = int(kwargs.get("timeout", self._default_timeout))

        if not code.strip():
            return ToolResult(error="No code provided.")

        if self.docker_workspace and self.session_id:
            # Execute in Docker Sandbox
            action = SandboxAction(command=code, action_type="python", timeout=timeout)
            obs = await self.docker_workspace.execute(self.session_id, action)
            output = obs.stdout
            if obs.stderr:
                output = f"{obs.stdout}\n--- stderr ---\n{obs.stderr}" if obs.stdout else obs.stderr
            return ToolResult(output=output, error=obs.stderr if obs.exit_code != 0 else "", metadata={"exit_code": obs.exit_code})

        # Local Fallback
        tmp = Path(tempfile.mktemp(suffix=".py"))
        try:
            tmp.write_text(code, encoding="utf-8")
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(tmp),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return ToolResult(
                    error=f"Execution timed out after {timeout}s.",
                    metadata={"exit_code": -1, "timeout": True},
                )

            stdout = stdout_bytes.decode(errors="replace").strip()
            stderr = stderr_bytes.decode(errors="replace").strip()
            exit_code = proc.returncode or 0

            if exit_code != 0:
                return ToolResult(
                    output=stdout,
                    error=stderr or f"Process exited with code {exit_code}.",
                    metadata={"exit_code": exit_code},
                )

            output = stdout
            if stderr:
                output = f"{stdout}\n--- stderr ---\n{stderr}" if stdout else stderr

            return ToolResult(output=output, metadata={"exit_code": exit_code})

        finally:
            tmp.unlink(missing_ok=True)
