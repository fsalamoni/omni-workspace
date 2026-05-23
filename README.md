# SalomoneUI (formerly SalomoneUI)

> The definitive multi-agent orchestration, cowrok, and computer control platform.

SalomoneUI combines the best aspects of SalomoneUI, OpenHands, OpenManus, Ruflo, Stagehand, and UI-TARS into a single, cohesive, React/FastAPI-based platform.

## Features
- **Multi-Agent Orchestration**: ReAct and ToolCall agents orchestrated by a Central Orchestrator.
- **GOAP Planning Engine**: Goal-Oriented Action Planning inspired by Ruflo, with dependency trees visualized in ReactFlow.
- **Docker Sandbox**: Secure, isolated code execution environments (like OpenHands).
- **Desktop & Browser Control**: Ready for integration with Stagehand (Browser) and UI-TARS (Desktop) VLMs.
- **MCP Hub**: Seamlessly connect tools across boundaries using the Model Context Protocol.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Running the Full Stack (Docker)
```bash
docker-compose up --build
```
The UI will be available at `http://localhost:3000`.

### Running Locally (Development)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -e .
uvicorn src.main:sio_app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Architecture
See `docs/architecture.md` for a detailed breakdown of the system.
