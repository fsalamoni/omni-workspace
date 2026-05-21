from typing import List, Dict, Any

class ContextCondenser:
    """Manages context window by summarizing older messages."""
    
    def monitor_usage(self, messages: List[Dict[str, Any]], max_tokens: int = 4000) -> bool:
        # A rough heuristic: ~4 chars per token
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        estimated_tokens = total_chars / 4
        return estimated_tokens > max_tokens

    async def condense(self, messages: List[Dict[str, Any]], llm_router: Any, keep_recent: int = 5) -> List[Dict[str, Any]]:
        """Summarizes older messages while keeping system prompt and recent ones."""
        if len(messages) <= keep_recent + 1:
            return messages
            
        system_msgs = [m for m in messages if m.get("role") == "system"]
        recent_msgs = messages[-keep_recent:]
        
        old_msgs = [m for m in messages if m not in system_msgs and m not in recent_msgs]
        if not old_msgs:
            return messages
            
        summary_prompt = "Summarize the following conversation history briefly and objectively, keeping key facts:\n\n"
        for m in old_msgs:
            summary_prompt += f"{m.get('role')}: {m.get('content')}\n"
            
        # We would use the llm_router here in a real impl
        # summary_resp = await llm_router.complete([{"role": "user", "content": summary_prompt}], model="...")
        # summary = summary_resp.choices[0].message.content
        summary = "[Condensation stub: Summarized previous context]"
        
        new_messages = system_msgs + [{"role": "system", "content": f"Previous context summary: {summary}"}] + recent_msgs
        return new_messages
