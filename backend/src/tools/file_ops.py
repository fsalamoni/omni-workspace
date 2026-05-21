import os
from typing import Optional, List, Dict, Any
from .base import BaseTool, ToolResult

class ReadFileTool(BaseTool):
    """Tool for reading file contents."""
    
    def __init__(self, workspace_dir: str):
        super().__init__(
            name="read_file",
            description="Reads the content of a file.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file relative to the workspace directory."
                    }
                },
                "required": ["file_path"]
            }
        )
        self.workspace_dir = workspace_dir

    async def execute(self, file_path: str, **kwargs) -> ToolResult:
        full_path = os.path.join(self.workspace_dir, file_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult(output=content)
        except Exception as e:
            return ToolResult(output="", error=str(e))

class WriteFileTool(BaseTool):
    """Tool for writing content to a file."""
    
    def __init__(self, workspace_dir: str):
        super().__init__(
            name="write_file",
            description="Writes content to a file, overwriting if it exists.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file relative to the workspace directory."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        )
        self.workspace_dir = workspace_dir

    async def execute(self, file_path: str, content: str, **kwargs) -> ToolResult:
        full_path = os.path.join(self.workspace_dir, file_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(output=f"Successfully wrote to {file_path}")
        except Exception as e:
            return ToolResult(output="", error=str(e))

class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""
    
    def __init__(self, workspace_dir: str):
        super().__init__(
            name="list_directory",
            description="Lists all files and directories in a given path.",
            parameters={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Directory path relative to the workspace directory. Use '.' for the root."
                    }
                },
                "required": ["dir_path"]
            }
        )
        self.workspace_dir = workspace_dir

    async def execute(self, dir_path: str, **kwargs) -> ToolResult:
        full_path = os.path.join(self.workspace_dir, dir_path)
        try:
            items = os.listdir(full_path)
            result = "\n".join(items)
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(output="", error=str(e))
