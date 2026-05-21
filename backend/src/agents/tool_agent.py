import json
from typing import Optional, Any
from .react_agent import ReActAgent, ThinkResult
from ..tools.base import ToolCollection

class ToolCallAgent(ReActAgent):
    """Agent that can use tools via LLM function calling."""
    
    def __init__(self, name: str, description: str, system_prompt: str, llm_router: Any, available_tools: ToolCollection, **kwargs):
        super().__init__(name, description, system_prompt, llm_router, **kwargs)
        self.available_tools = available_tools

    async def think(self) -> ThinkResult:
        tools = self.available_tools.to_function_schemas()
        
        # Pass the specific model for this agent if configured
        response = await self.llm.complete(
            messages=self.memory,
            model=self.model,  # Will fallback to global setting if None
            tools=tools
        )
        
        msg = response.get("content", "")
        self.add_to_memory("assistant", msg)
        
        # Litellm response parsing
        tool_calls = response.get("tool_calls", [])
        if tool_calls:
            tc = tool_calls[0]
            return ThinkResult(
                should_act=True,
                tool_name=tc["function"]["name"],
                tool_args=json.loads(tc["function"]["arguments"]),
                reasoning=msg or "Executing tool"
            )
            
        return ThinkResult(should_act=False, reasoning=msg.content or "")

    async def act(self, think_result: ThinkResult) -> Optional[str]:
        if not think_result.tool_name:
            return "No tool selected"
            
        tool = self.available_tools.get(think_result.tool_name)
        if not tool:
            result_str = f"Error: Tool {think_result.tool_name} not found."
        else:
            tool_res = await tool.execute(**(think_result.tool_args or {}))
            if tool_res.error:
                result_str = f"Tool Error: {tool_res.error}"
            else:
                result_str = f"Tool Output:\n{tool_res.output}"
                
        self.add_to_memory("tool", result_str)
        return None # Return None to continue the loop
