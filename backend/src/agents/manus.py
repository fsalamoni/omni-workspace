from typing import Any
from .tool_agent import ToolCallAgent
from ..tools.base import ToolCollection
from ..tools.python_exec import PythonExecute
from ..tools.file_ops import ReadFileTool, WriteFileTool, ListDirectoryTool
from ..tools.web_search import WebSearchTool
from ..tools.terminal import TerminalTool

class ManusAgent(ToolCallAgent):
    """The flagship general-purpose agent with standard toolset."""
    
    def __init__(self, llm_router: Any, workspace_dir: str, model: str = None, docker_workspace=None, session_id: str=None):
        tools = ToolCollection()
        tools.register(PythonExecute(docker_workspace=docker_workspace, session_id=session_id))
        tools.register(ReadFileTool(workspace_dir))
        tools.register(WriteFileTool(workspace_dir))
        tools.register(ListDirectoryTool(workspace_dir))
        tools.register(WebSearchTool())
        tools.register(TerminalTool(workspace_dir, docker_workspace=docker_workspace, session_id=session_id))
        
        system_prompt = """You are OmniWorkspace Agent, an all-capable AI assistant.
You can write code, run terminal commands, manage files, and search the web.
Decompose problems, think step by step, and execute your actions using the tools provided.
When you are completely finished with a task, clearly state the final answer or result."""
        
        super().__init__(
            name="Manus",
            description="General purpose execution agent.",
            system_prompt=system_prompt,
            llm_router=llm_router,
            model=model,
            available_tools=tools
        )
