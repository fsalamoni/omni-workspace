from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from ..orchestrator.session import SessionManager

router = APIRouter()

# Dependency stub
def get_session_manager() -> SessionManager:
    from ..main import session_manager
    return session_manager

def get_settings_db():
    from ..main import settings_db
    return settings_db

@router.get("/health")
async def health():
    return {"status": "ok", "service": "OmniWorkspace Backend"}

@router.post("/sessions")
async def create_session(sm: SessionManager = Depends(get_session_manager)):
    session = sm.create_session()
    return {"id": session.id, "workspace": session.workspace_path}

@router.get("/sessions")
async def list_sessions(sm: SessionManager = Depends(get_session_manager)):
    return {"sessions": [{"id": s.id} for s in sm.list_sessions()]}

@router.get("/sessions/{session_id}/events")
async def get_events(session_id: str, after_id: str = None, sm: SessionManager = Depends(get_session_manager)):
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    events = session.event_stream.get_events(after_id)
    return {"events": [e.model_dump() for e in events]}

from fastapi import Request

@router.get("/providers")
async def list_providers():
    # Hardcoded popular providers for UI
    return {
        "providers": [
            "OpenAI", "Anthropic", "Google", "DeepSeek", "OpenRouter", 
            "Groq", "Ollama", "Mistral", "Cohere", "Together AI", 
            "Fireworks", "Perplexity", "xAI", "ElevenLabs", "fal.ai"
        ]
    }

@router.get("/models/global")
async def list_global_models(db = Depends(get_settings_db)):
    import litellm
    
    # Get user configured providers
    configured_providers = set()
    if db:
        keys = await db._get_json("api_keys") or []
        for k in keys:
            if k.get("key") and k.get("key").strip():
                configured_providers.add(k.get("provider", "").lower().replace(" ", ""))

    models = []
    
    # Map UI names to Litellm internal names for edge cases
    provider_aliases = {
        "google": ["gemini", "vertex_ai"],
        "togetherai": ["together_ai"],
        "fireworks": ["fireworks_ai"],
        "xai": ["grok"],
        "fal.ai": ["fal"]
    }
    
    expanded_providers = set(configured_providers)
    for p in configured_providers:
        if p in provider_aliases:
            expanded_providers.update(provider_aliases[p])
    
    # Force inject state-of-the-art models that litellm might miss
    sota_models = [
        {"id": "deepseek/deepseek-reasoner", "label": "DeepSeek Reasoner (R1)", "provider": "deepseek"},
        {"id": "deepseek/deepseek-chat", "label": "DeepSeek Chat (V3)", "provider": "deepseek"},
        {"id": "openrouter/deepseek/deepseek-r1", "label": "DeepSeek R1 (OpenRouter)", "provider": "openrouter"},
        {"id": "openrouter/deepseek/deepseek-chat", "label": "DeepSeek V3 (OpenRouter)", "provider": "openrouter"},
        {"id": "openrouter/openai/o3-mini", "label": "OpenAI o3-mini (OpenRouter)", "provider": "openrouter"},
    ]
    
    seen_ids = set()

    for m in sota_models:
        prov = m["provider"].lower()
        if prov in expanded_providers:
            models.append({"id": m["id"], "label": m["label"], "provider": prov.capitalize(), "tier": "advanced"})
            seen_ids.add(m["id"])

    # Litellm has model_cost which maps model_name -> dict(cost, provider, etc.)
    for model_name, info in litellm.model_cost.items():
        if model_name in seen_ids:
            continue
            
        provider = info.get("litellm_provider", "unknown").lower()
        
        # Normalize provider names to match our UI config (e.g. google, openai, anthropic, deepseek)
        norm_prov = provider.replace(" ", "")
        
        # If user has not configured this provider, skip
        if norm_prov not in expanded_providers:
            # Special fallback for generic models or open source if needed, but strict mode requested
            continue

        models.append({
            "id": model_name,
            "label": model_name,
            "provider": provider.capitalize() if provider else "Unknown",
            "tier": "balanced"
        })
        
    return {"models": models}

@router.get("/settings/debug")
async def debug_db_path(db = Depends(get_settings_db)):
    import os
    if not db: return {"error": "no db"}
    return {"path": os.path.abspath(db.db_path)}

@router.get("/settings/api-keys")
async def get_api_keys(db = Depends(get_settings_db)):
    if not db: return {"keys": []}
    keys = await db._get_json("api_keys") or []
    # Mask keys for security
    masked = [{"provider": k["provider"], "key": k["key"][:4] + "***"} for k in keys]
    return {"keys": masked}

@router.post("/settings/api-keys")
async def save_api_keys(request: Request, db = Depends(get_settings_db)):
    data = await request.json()
    new_keys_list = data.get("keys", [])
    if not db: return {"status": "error"}

    # Get existing
    existing_keys = await db._get_json("api_keys") or []
    existing_map = {k["provider"]: k["key"] for k in existing_keys}
    print("EXISTING:", existing_map)
    print("NEW KEYS:", new_keys_list)
    
    # Merge
    for nk in new_keys_list:
        p = nk.get("provider")
        v = nk.get("key", "").strip()
        
        if v == "":
            # User cleared it, remove from map
            if p in existing_map:
                del existing_map[p]
        elif "***" in v:
            # Masked string, do not overwrite, keep existing
            pass
        else:
            # New key
            existing_map[p] = v
            
    print("MERGED MAP:", existing_map)
    # Save back
    merged = [{"provider": p, "key": v} for p, v in existing_map.items()]
    await db._set_json("api_keys", merged)
    return {"status": "ok"}

@router.get("/settings/catalog")
async def get_catalog(db = Depends(get_settings_db)):
    if not db: return {"catalog": []}
    catalog = await db.get_personal_catalog()
    return {"catalog": catalog}

@router.post("/settings/catalog")
async def save_catalog(request: Request, db = Depends(get_settings_db)):
    data = await request.json()
    if db:
        await db.save_personal_catalog(data)
    return {"status": "ok"}

@router.get("/settings/agents")
async def get_agent_configs(db = Depends(get_settings_db)):
    if not db: return {"configs": {}}
    configs = await db.get_agent_configs()
    return {"configs": configs}

@router.post("/settings/agents")
async def save_agent_configs(request: Request, db = Depends(get_settings_db)):
    data = await request.json()
    if db:
        await db.save_agent_configs(data)
    return {"status": "ok"}
