"""
OmniWorkspace Sandbox Action Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Lightweight FastAPI server running INSIDE each sandbox container.
Receives execution commands from the orchestrator and returns results.

Provides:
- Persistent bash session (via subprocess)
- Python code execution (via exec/eval)
- File operations
"""

import asyncio
import os
import subprocess
import sys
import traceback
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="OmniWorkspace Sandbox Action Server", version="0.1.0")


# ── Models ────────────────────────────────────────────────────

class ExecuteRequest(BaseModel):
    """Request to execute a command in the sandbox."""
    command: str
    action_type: str = "bash"  # bash, python, file_read, file_write
    timeout: int = 60
    cwd: Optional[str] = None
    # For file operations
    file_path: Optional[str] = None
    file_content: Optional[str] = None


class ExecuteResponse(BaseModel):
    """Response from sandbox execution."""
    id: str
    action_type: str
    stdout: str
    stderr: str
    exit_code: int
    files_changed: list[str] = []
    duration_ms: float
    timestamp: str


# ── Global State ──────────────────────────────────────────────

_python_globals: dict = {"__builtins__": __builtins__}
_python_locals: dict = {}


# ── Execution Handlers ────────────────────────────────────────

async def execute_bash(command: str, timeout: int, cwd: Optional[str] = None) -> ExecuteResponse:
    """Execute a bash command with timeout."""
    start = asyncio.get_event_loop().time()
    work_dir = cwd or "/workspace"

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            env={**os.environ, "TERM": "xterm-256color"},
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        exit_code = proc.returncode or 0
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
    except asyncio.TimeoutError:
        proc.kill()
        stdout = ""
        stderr = f"Command timed out after {timeout}s"
        exit_code = 124
    except Exception as e:
        stdout = ""
        stderr = str(e)
        exit_code = 1

    duration = (asyncio.get_event_loop().time() - start) * 1000

    return ExecuteResponse(
        id=str(uuid.uuid4()),
        action_type="bash",
        stdout=stdout[-50000:],  # Limit output size
        stderr=stderr[-10000:],
        exit_code=exit_code,
        duration_ms=round(duration, 2),
        timestamp=datetime.utcnow().isoformat(),
    )


async def execute_python(code: str, timeout: int) -> ExecuteResponse:
    """Execute Python code in a persistent namespace."""
    global _python_globals, _python_locals
    start = asyncio.get_event_loop().time()

    import io
    from contextlib import redirect_stdout, redirect_stderr

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code = 0

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Try eval first (for expressions that return values)
            try:
                result = eval(code, _python_globals, _python_locals)
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                # Fall back to exec for statements
                exec(code, _python_globals, _python_locals)
    except Exception:
        stderr_capture.write(traceback.format_exc())
        exit_code = 1

    duration = (asyncio.get_event_loop().time() - start) * 1000
    stdout = stdout_capture.getvalue()
    stderr = stderr_capture.getvalue()

    return ExecuteResponse(
        id=str(uuid.uuid4()),
        action_type="python",
        stdout=stdout[-50000:],
        stderr=stderr[-10000:],
        exit_code=exit_code,
        duration_ms=round(duration, 2),
        timestamp=datetime.utcnow().isoformat(),
    )


async def read_file(file_path: str) -> ExecuteResponse:
    """Read a file from the workspace."""
    start = asyncio.get_event_loop().time()
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        stdout = content
        stderr = ""
        exit_code = 0
    except Exception as e:
        stdout = ""
        stderr = str(e)
        exit_code = 1

    duration = (asyncio.get_event_loop().time() - start) * 1000
    return ExecuteResponse(
        id=str(uuid.uuid4()),
        action_type="file_read",
        stdout=stdout[-100000:],
        stderr=stderr,
        exit_code=exit_code,
        duration_ms=round(duration, 2),
        timestamp=datetime.utcnow().isoformat(),
    )


async def write_file(file_path: str, content: str) -> ExecuteResponse:
    """Write content to a file in the workspace."""
    start = asyncio.get_event_loop().time()
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        stdout = f"File written: {file_path} ({len(content)} bytes)"
        stderr = ""
        exit_code = 0
        files_changed = [file_path]
    except Exception as e:
        stdout = ""
        stderr = str(e)
        exit_code = 1
        files_changed = []

    duration = (asyncio.get_event_loop().time() - start) * 1000
    return ExecuteResponse(
        id=str(uuid.uuid4()),
        action_type="file_write",
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        files_changed=files_changed,
        duration_ms=round(duration, 2),
        timestamp=datetime.utcnow().isoformat(),
    )


# ── API Endpoints ─────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "python_version": sys.version,
        "workspace": "/workspace",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute a command in the sandbox."""
    match request.action_type:
        case "bash":
            return await execute_bash(request.command, request.timeout, request.cwd)
        case "python":
            return await execute_python(request.command, request.timeout)
        case "file_read":
            if not request.file_path:
                raise HTTPException(400, "file_path required for file_read")
            return await read_file(request.file_path)
        case "file_write":
            if not request.file_path or request.file_content is None:
                raise HTTPException(400, "file_path and file_content required for file_write")
            return await write_file(request.file_path, request.file_content)
        case _:
            raise HTTPException(400, f"Unknown action_type: {request.action_type}")


@app.post("/reset")
async def reset():
    """Reset the Python execution namespace."""
    global _python_globals, _python_locals
    _python_globals = {"__builtins__": __builtins__}
    _python_locals = {}
    return {"status": "reset", "timestamp": datetime.utcnow().isoformat()}


# ── Entry Point ───────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
