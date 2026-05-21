from typing import Any
from ..agents.tool_agent import ToolCallAgent
from ..tools.base import ToolCollection, BaseTool, ToolResult
import pyautogui
import mss
import base64
from io import BytesIO
from PIL import Image

class ScreenshotTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="desktop_screenshot",
            description="Take a screenshot of the primary display. Returns a base64 encoded image.",
            parameters={"type": "object", "properties": {}}
        )

    async def execute(self, **kwargs) -> ToolResult:
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                return ToolResult(output=f"Screenshot taken. Size: {img.size}. Base64: {img_str[:50]}...")
        except Exception as e:
            return ToolResult(output="", error=str(e))

class MouseClickTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="desktop_mouse_click",
            description="Click the mouse at specific x, y coordinates.",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate"},
                    "y": {"type": "integer", "description": "Y coordinate"}
                },
                "required": ["x", "y"]
            }
        )

    async def execute(self, x: int, y: int, **kwargs) -> ToolResult:
        try:
            pyautogui.click(x=x, y=y)
            return ToolResult(output=f"Clicked at ({x}, {y})")
        except Exception as e:
            return ToolResult(output="", error=str(e))

class KeyboardTypeTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="desktop_keyboard_type",
            description="Type a string using the keyboard.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        )

    async def execute(self, text: str, **kwargs) -> ToolResult:
        try:
            pyautogui.typewrite(text)
            return ToolResult(output=f"Typed: {text}")
        except Exception as e:
            return ToolResult(output="", error=str(e))

class DesktopAgent(ToolCallAgent):
    """
    Desktop Control Agent Bridge.
    Uses pyautogui / Computer Use API.
    """
    
    def __init__(self, llm_router: Any, model: str = None):
        tools = ToolCollection()
        tools.register(ScreenshotTool())
        tools.register(MouseClickTool())
        tools.register(KeyboardTypeTool())
        
        super().__init__(
            name="DesktopAgent",
            description="Agent specialized in local desktop interaction and UI control.",
            system_prompt="You are a local computer automation agent. You can take screenshots, click elements, and type text. Be precise.",
            llm_router=llm_router,
            model=model,
            available_tools=tools,
            max_steps=30
        )
