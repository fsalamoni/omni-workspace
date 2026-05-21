from pydantic import BaseModel
from typing import Optional, List, Literal

class SandboxAction(BaseModel):
    command: str
    action_type: Literal['bash', 'python', 'file_edit']
    timeout: int = 30

class SandboxObservation(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    files_changed: Optional[List[str]] = None
