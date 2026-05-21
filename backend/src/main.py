from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import os

from .config import Settings
from .llm.router import LLMRouter
from .memory.agent_db import AgentDB
from .orchestrator.session import SessionManager
from src.orchestrator.core import CentralOrchestrator
from src.db.settings_db import SettingsDB
from src.sandbox.docker_workspace import DockerWorkspace
from .api import routes, websocket

# Globals
settings = Settings()
session_manager = SessionManager(db_path="./.data/omni_sessions.db")
settings_db = SettingsDB(db_path="./.data/omni_settings.db")
llm_router = LLMRouter(settings, settings_db)
# We use dummy paths for the memory DB to ensure it starts without errors in dev
agent_db = AgentDB(db_path="./.data/omni_memory") 
docker_workspace = DockerWorkspace()
orchestrator = CentralOrchestrator(settings, llm_router, agent_db, session_manager, settings_db, docker_workspace)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("OmniWorkspace Backend starting up...")
    await settings_db.init_db()
    websocket.setup_orchestrator(orchestrator)
    yield
    print("Shutting down...")

app = FastAPI(title="OmniWorkspace API", lifespan=lifespan)
app.state.settings_db = settings_db

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

# Wrap the FastAPI app with Socket.IO ASGIApp
app = socketio.ASGIApp(websocket.sio, other_asgi_app=app)
