from typing import Any
from ..agents.tool_agent import ToolCallAgent
from ..tools.base import ToolCollection
from ..tools.browser import NavigateTool, ExtractPageContentTool

class BrowserAgent(ToolCallAgent):
    """
    Browser Agent Bridge.
    Uses Playwright under the hood for web automation.
    """
    
    def __init__(self, llm_router: Any, model: str = None):
        tools = ToolCollection()
        tools.register(NavigateTool())
        tools.register(ExtractPageContentTool())
        
        super().__init__(
            name="BrowserAgent",
            description="Agent specialized in web browsing, interaction, and data extraction.",
            system_prompt="You are a browser automation agent. You can navigate the web, extract data, and browse pages. ALWAYS explain what you found or achieved clearly.",
            llm_router=llm_router,
            model=model,
            available_tools=tools,
            max_steps=30
        )
