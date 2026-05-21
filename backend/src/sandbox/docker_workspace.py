import asyncio
import os
import uuid
import docker
from typing import Optional, Dict
from .models import SandboxAction, SandboxObservation

class DockerWorkspace:
    """Manages Docker containers for secure sandboxed execution."""
    
    def __init__(self, base_image: str = "python:3.12-slim"):
        self.base_image = base_image
        self.containers: Dict[str, str] = {} # session_id -> container_id
        self.on_observation = None # Callback for streaming logs
        
        try:
            self.client = docker.from_env()
            # Ensure image exists
            try:
                self.client.images.get(base_image)
            except docker.errors.ImageNotFound:
                print(f"[Sandbox] Pulling image {base_image}...")
                self.client.images.pull(base_image)
        except Exception as e:
            print(f"[Sandbox] Error initializing Docker client: {e}")
            self.client = None

    async def create_container(self, session_id: str, workspace_dir: str) -> Optional[str]:
        """Create a new sandbox container for a session."""
        if not self.client:
            return None
            
        try:
            container_name = f"omni_sandbox_{session_id}_{uuid.uuid4().hex[:8]}"
            
            # Ensure workspace dir exists
            os.makedirs(workspace_dir, exist_ok=True)
            
            container = self.client.containers.run(
                self.base_image,
                command="tail -f /dev/null", # Keep alive
                name=container_name,
                detach=True,
                remove=True,
                network_mode="bridge",
                volumes={
                    workspace_dir: {'bind': '/workspace', 'mode': 'rw'}
                },
                working_dir="/workspace",
                # Security limits
                mem_limit="1g",
                cpu_quota=100000,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"]
            )
            
            self.containers[session_id] = container.id
            print(f"[Sandbox] Created container {container.id} for session {session_id}")
            return container.id
            
        except Exception as e:
            print(f"[Sandbox] Error creating container: {e}")
            return None

    async def execute(self, session_id: str, action: SandboxAction) -> SandboxObservation:
        """Execute a command in the session's sandbox."""
        if not self.client or session_id not in self.containers:
            return SandboxObservation(
                stdout="",
                stderr="Sandbox not initialized or Docker unavailable",
                exit_code=-1
            )
            
        try:
            container_id = self.containers[session_id]
            container = self.client.containers.get(container_id)
            
            # Simple exec_run for now (in a real app, use the action_server for persistence)
            cmd = action.command
            if action.action_type == 'python':
                # Write to temp file and run
                cmd = f'python -c "{cmd.replace('"', '\\"')}"'
                
            exit_code, output = container.exec_run(
                cmd,
                workdir="/workspace"
            )
            
            # Decode output
            out_str = output.decode('utf-8') if output else ""
            
            obs = SandboxObservation(
                stdout=out_str if exit_code == 0 else "",
                stderr=out_str if exit_code != 0 else "",
                exit_code=exit_code
            )
            
            if self.on_observation:
                asyncio.create_task(self.on_observation(session_id, action, obs))
                
            return obs
            
        except Exception as e:
            return SandboxObservation(stdout="", stderr=str(e), exit_code=-1)

    async def destroy_container(self, session_id: str):
        """Destroy a session's sandbox."""
        if not self.client or session_id not in self.containers:
            return
            
        try:
            container_id = self.containers[session_id]
            container = self.client.containers.get(container_id)
            container.stop()
            del self.containers[session_id]
            print(f"[Sandbox] Destroyed container for session {session_id}")
        except Exception as e:
            print(f"[Sandbox] Error destroying container: {e}")
