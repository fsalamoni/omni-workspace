import asyncio
from typing import Any, AsyncGenerator, Dict

from .session import SessionManager, Session
from .event_stream import MessageEvent, ActionEvent, ObservationEvent
from ..planning.planner import PlanningFlow

class CentralOrchestrator:
    """The brain of SalomoneUI. Connects UI requests to agents and tools."""
    
    def __init__(self, settings: Any, llm_router: Any, memory: Any, session_manager: SessionManager, settings_db: Any = None, docker_workspace: Any = None):
        self.settings = settings
        self.llm_router = llm_router
        self.memory = memory
        self.session_manager = session_manager
        self.settings_db = settings_db
        self.docker_workspace = docker_workspace
        self.on_sandbox_event = None
        
        if self.docker_workspace:
            self.docker_workspace.on_observation = self._handle_sandbox_observation
            
    async def _handle_sandbox_observation(self, session_id, action, obs):
        if self.on_sandbox_event:
            await self.on_sandbox_event(session_id, {
                "type": "sandbox_log",
                "command": action.command,
                "stdout": obs.stdout,
                "stderr": obs.stderr,
                "exit_code": obs.exit_code
            })

    async def process_request(self, session_id: str, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a user request and yield events for the WebSocket."""
        session = self.session_manager.get_session(session_id)
        if not session:
            yield {"type": "error", "message": "Session not found"}
            return

        # Record user message
        user_event = MessageEvent(data={"role": "user", "content": user_message})
        session.event_stream.append(user_event)
        yield user_event.model_dump()

        # Execute flow
        flow = PlanningFlow(self.llm_router, session.workspace_path, self.settings_db, self.docker_workspace, session.id)
        
        async for update in flow.execute(user_message):
            if update["type"] == "info":
                ev = MessageEvent(data={"role": "system", "content": update["message"]})
                session.event_stream.append(ev)
                yield ev.model_dump()
            elif update["type"] == "result":
                ev = MessageEvent(data={"role": "assistant", "content": update["message"]})
                session.event_stream.append(ev)
                yield ev.model_dump()
