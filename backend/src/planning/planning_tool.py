import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..tools.base import BaseTool, ToolResult

class PlanStep(BaseModel):
    id: str
    title: str
    description: str
    status: str = "pending" # pending, in_progress, completed, failed
    agent_type: Optional[str] = "manus"
    result: Optional[str] = None

class Plan(BaseModel):
    id: str
    title: str
    steps: List[PlanStep]
    created_at: str
    status: str = "active"

class PlanningTool(BaseTool):
    """Tool for managing execution plans."""
    
    def __init__(self):
        super().__init__(
            name="planning_tool",
            description="Create and manage multi-step execution plans.",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "mark_step", "list", "get"],
                        "description": "The action to perform."
                    },
                    "title": {"type": "string", "description": "Title for new plan."},
                    "steps": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "agent_type": {"type": "string"}
                            }
                        }
                    },
                    "plan_id": {"type": "string"},
                    "step_id": {"type": "string"},
                    "step_status": {"type": "string", "enum": ["in_progress", "completed", "failed"]},
                    "step_result": {"type": "string"}
                },
                "required": ["action"]
            }
        )
        self.plans: Dict[str, Plan] = {}

    async def execute(self, action: str, **kwargs) -> ToolResult:
        if action == "create":
            plan_id = str(uuid.uuid4())
            steps_data = kwargs.get("steps", [])
            steps = [
                PlanStep(
                    id=str(uuid.uuid4()),
                    title=s.get("title", f"Step {i}"),
                    description=s.get("description", ""),
                    agent_type=s.get("agent_type", "manus")
                ) for i, s in enumerate(steps_data)
            ]
            
            plan = Plan(
                id=plan_id,
                title=kwargs.get("title", "Execution Plan"),
                steps=steps,
                created_at=datetime.utcnow().isoformat()
            )
            self.plans[plan_id] = plan
            return ToolResult(output=f"Created plan {plan_id} with {len(steps)} steps.")
            
        elif action == "mark_step":
            plan_id = kwargs.get("plan_id")
            step_id = kwargs.get("step_id")
            status = kwargs.get("step_status")
            
            if not plan_id or plan_id not in self.plans:
                return ToolResult(output="", error="Invalid plan_id")
                
            plan = self.plans[plan_id]
            for step in plan.steps:
                if step.id == step_id:
                    step.status = status
                    if "step_result" in kwargs:
                        step.result = kwargs["step_result"]
                    return ToolResult(output=f"Marked step {step_id} as {status}")
                    
            return ToolResult(output="", error="Step not found")
            
        elif action == "list":
            res = "\n".join([f"[{p.id}] {p.title} ({p.status})" for p in self.plans.values()])
            return ToolResult(output=res or "No plans.")
            
        elif action == "get":
            plan_id = kwargs.get("plan_id")
            if not plan_id or plan_id not in self.plans:
                return ToolResult(output="", error="Invalid plan_id")
            return ToolResult(output=self.plans[plan_id].model_dump_json(indent=2))
            
        return ToolResult(output="", error=f"Unknown action {action}")
