import socketio
from ..orchestrator.core import CentralOrchestrator

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# This will be injected at startup
orchestrator = None

async def _emit_sandbox_event(session_id, event_data):
    # Emit a specific sandbox event
    await sio.emit('sandbox_event', event_data, room=session_id)

def setup_orchestrator(orch):
    global orchestrator
    orchestrator = orch
    orchestrator.on_sandbox_event = _emit_sandbox_event

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def user_message(sid, data):
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not session_id or not message:
        await sio.emit('error', {'message': 'session_id and message required'}, room=sid)
        return
        
    try:
        async for event in orchestrator.process_request(session_id, message):
            await sio.emit('event', event, room=sid)
    except Exception as e:
        await sio.emit('error', {'message': str(e)}, room=sid)
