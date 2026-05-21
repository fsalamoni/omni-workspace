"""Base tool abstractions.

Every tool in OmniWorkspace implements ``BaseTool`` and is collected in a
``ToolCollection`` for registration, lookup, and LLM function-schema export.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────────────
# Result model
# ────────────────────────────────────────────────────────────────────

class ToolResult(BaseModel):
    """Standardised result returned by every tool execution."""

    output: str = ""
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None


# ────────────────────────────────────────────────────────────────────
# Base class
# ────────────────────────────────────────────────────────────────────

class BaseTool(ABC):
    """Abstract base class for all OmniWorkspace tools.

    Subclasses must implement :meth:`execute` and set the class-level
    ``name``, ``description``, and ``parameters`` attributes.
    """

    name: str = "base_tool"
    description: str = "Base tool — override in subclass."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given arguments and return a result."""
        ...

    def to_function_schema(self) -> dict[str, Any]:
        """Export this tool as an OpenAI-compatible function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def __repr__(self) -> str:
        return f"<Tool {self.name!r}>"


# ────────────────────────────────────────────────────────────────────
# Terminate tool (built-in)
# ────────────────────────────────────────────────────────────────────

class Terminate(BaseTool):
    """Special sentinel tool that signals the agent should stop."""

    name: str = "terminate"
    description: str = (
        "Call this tool when the task is fully complete. "
        "Pass a final summary of what was accomplished."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Final summary of what was accomplished.",
            }
        },
        "required": ["summary"],
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        summary = kwargs.get("summary", "Task completed.")
        return ToolResult(output=summary, metadata={"terminated": True})


# ────────────────────────────────────────────────────────────────────
# Tool collection
# ────────────────────────────────────────────────────────────────────

class ToolCollection:
    """Registry of ``BaseTool`` instances with lookup and schema export."""

    def __init__(self, *tools: BaseTool) -> None:
        self._tools: dict[str, BaseTool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance by its name."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Look up a tool by name."""
        return self._tools.get(name)

    def unregister(self, name: str) -> bool:
        """Remove a tool.  Returns ``True`` if it existed."""
        return self._tools.pop(name, None) is not None

    def to_function_schemas(self) -> list[dict[str, Any]]:
        """Export all tools as OpenAI function-calling schemas."""
        return [t.to_function_schema() for t in self._tools.values()]

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<ToolCollection tools={self.tool_names}>"


def parse_tool_args(raw_args: str | dict[str, Any]) -> dict[str, Any]:
    """Safely parse tool arguments from an LLM response (string or dict)."""
    if isinstance(raw_args, dict):
        return raw_args
    try:
        return json.loads(raw_args)
    except (json.JSONDecodeError, TypeError):
        return {"input": raw_args}
