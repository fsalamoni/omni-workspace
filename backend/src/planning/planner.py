from typing import Any, AsyncGenerator, Dict
from ..agents.manus import ManusAgent
from ..browser.browser_agent import BrowserAgent
from ..desktop.desktop_agent import DesktopAgent
import json

class PlanningFlow:
    """Orchestrates complex task execution using PlanningTool and sub-agents."""
    
    def __init__(self, llm_router: Any, workspace_dir: str, settings_db: Any = None, docker_workspace: Any = None, session_id: str = None):
        self.llm_router = llm_router
        self.workspace_dir = workspace_dir
        self.settings_db = settings_db
        self.docker_workspace = docker_workspace
        self.session_id = session_id

    async def execute(self, user_request: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes a plan flow. Yields status updates.
        """
        yield {"type": "info", "message": "Analyzing request to determine the best agent..."}
        
        # Determine the agent via LLM
        routing_prompt = f"""
You are an intelligent router. Choose the best agent to handle the user request.
Agents:
1. "Manus": General coding, terminal execution, file editing, web search.
2. "Browser": Web automation, navigating pages, extracting text/data from websites.
3. "Desktop": Local computer control, mouse clicks, keyboard typing, taking screenshots.

User Request: {user_request}

Return ONLY a JSON object with the key "agent" and value as the agent name ("Manus", "Browser", or "Desktop").
"""
        try:
            route_res = await self.llm_router.complete(messages=[{"role": "user", "content": routing_prompt}], model=None)
            route_json = json.loads(route_res.get("content", '{"agent": "Manus"}').strip('` \n'))
            target_agent = route_json.get("agent", "Manus")
        except:
            target_agent = "Manus"

        yield {"type": "info", "message": f"Delegating to {target_agent} Agent..."}
        
        # Get configured models
        agent_model = None
        if self.settings_db:
            configs = await self.settings_db.get_agent_configs()
            agent_model = configs.get(target_agent)
            
        # Ensure container exists if needed
        if target_agent == "Manus" and self.docker_workspace and self.session_id:
            await self.docker_workspace.create_container(self.session_id, self.workspace_dir)
            
        if target_agent == "Browser":
            agent = BrowserAgent(self.llm_router, model=agent_model)
        elif target_agent == "Desktop":
            agent = DesktopAgent(self.llm_router, model=agent_model)
        else:
            agent = ManusAgent(self.llm_router, self.workspace_dir, model=agent_model, docker_workspace=self.docker_workspace, session_id=self.session_id)
            
        result = await agent.run(user_request)
        
        yield {"type": "result", "message": result}
