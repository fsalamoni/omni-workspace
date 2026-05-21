from typing import Optional, Any, Dict, Tuple
from pydantic import BaseModel
from .base import BaseAgent

class ThinkResult(BaseModel):
    should_act: bool
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    reasoning: str

class ReActAgent(BaseAgent):
    """Agent implementing Think-then-Act pattern."""
    
    async def step(self) -> Optional[str]:
        think_result = await self.think()
        
        if not think_result.should_act:
            return think_result.reasoning
            
        act_result = await self.act(think_result)
        return act_result

    async def think(self) -> ThinkResult:
        """Analyze current state and decide next action."""
        raise NotImplementedError

    async def act(self, think_result: ThinkResult) -> Optional[str]:
        """Execute chosen action based on think phase."""
        raise NotImplementedError
