#!/bin/bash
set -e

echo "Starting OmniWorkspace Sandbox..."

# Start tmux session for background bash commands
tmux new-session -d -s sandbox "bash"

# Start the action server (assumes the orchestrator mounts the action_server.py to /app/action_server.py)
if [ -f "/app/action_server.py" ]; then
    echo "Starting action server..."
    uvicorn action_server:app --app-dir /app --host 0.0.0.0 --port 8080
else
    echo "Warning: action_server.py not found at /app/action_server.py. Keeping container alive."
    tail -f /dev/null
fi
