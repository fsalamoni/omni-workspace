from enum import Enum
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from contextlib import contextmanager

class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    def __init__(self, name: str, description: str, system_prompt: str, llm_router: Any, model: Optional[str] = None, max_steps: int = 30):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.llm = llm_router
        self.model = model
        self.max_steps = max_steps
        self.state = AgentState.IDLE
        self.memory: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self._step_count = 0

    @contextmanager
    def state_context(self):
        self.state = AgentState.RUNNING
        try:
            yield
            self.state = AgentState.FINISHED
        except Exception as e:
            self.state = AgentState.ERROR
            raise e

    def add_to_memory(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})

    def is_stuck(self) -> bool:
        if len(self.memory) < 4:
            return False
        # Simple duplicate detection for last two assistant messages
        assistant_msgs = [m for m in self.memory if m["role"] == "assistant"]
        if len(assistant_msgs) >= 2:
            return assistant_msgs[-1]["content"] == assistant_msgs[-2]["content"]
        return False

    async def run(self, request: str) -> str:
        self.add_to_memory("user", request)
        self._step_count = 0
        
        with self.state_context():
            while self.state == AgentState.RUNNING:
                if self._step_count >= self.max_steps:
                    return "Max steps reached."
                if self.is_stuck():
                    return "Agent is stuck in a loop."
                    
                result = await self.step()
                if result:
                    return result
                self._step_count += 1
        return ""

    @abstractmethod
    async def step(self) -> Optional[str]:
        """Execute a single step. Return string if finished, None to continue loop."""
        pass
