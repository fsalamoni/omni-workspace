import asyncio
from typing import Any, Optional
from playwright.async_api import async_playwright, Page, Browser
from src.tools.base import BaseTool, ToolResult

# Global browser instance
_browser: Optional[Browser] = None
_page: Optional[Page] = None
_playwright = None

async def _get_page() -> Page:
    global _browser, _page, _playwright
    if not _playwright:
        _playwright = await async_playwright().start()
    if not _browser:
        _browser = await _playwright.chromium.launch(headless=True)
    if not _page:
        _page = await _browser.new_page()
    return _page

class NavigateTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="browser_navigate",
            description="Navigate to a specific URL in the browser.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to navigate to."}
                },
                "required": ["url"]
            }
        )

    async def execute(self, url: str, **kwargs) -> ToolResult:
        try:
            page = await _get_page()
            await page.goto(url, wait_until="networkidle")
            title = await page.title()
            return ToolResult(output=f"Navigated to {url}. Title: {title}")
        except Exception as e:
            return ToolResult(output="", error=str(e))

class ExtractPageContentTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="browser_extract_text",
            description="Extract all visible text from the current browser page.",
            parameters={"type": "object", "properties": {}}
        )

    async def execute(self, **kwargs) -> ToolResult:
        try:
            page = await _get_page()
            # Extract text
            content = await page.evaluate("document.body.innerText")
            # Truncate if too long to save context
            if len(content) > 10000:
                content = content[:10000] + "\n...[TRUNCATED]"
            return ToolResult(output=content)
        except Exception as e:
            return ToolResult(output="", error=str(e))
