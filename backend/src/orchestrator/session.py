"""Session management — lifecycle, persistence, and lookup.

Each user interaction is wrapped in a ``Session`` that owns its own
``EventStream``, plan state, and workspace context.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional

import aiosqlite
from pydantic import BaseModel, Field

from src.orchestrator.event_stream import EventStream


# ────────────────────────────────────────────────────────────────────
# Models
# ────────────────────────────────────────────────────────────────────

class SessionStatus(StrEnum):
    """Lifecycle status of a session."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class SessionInfo(BaseModel):
    """Serialisable snapshot of a session (without the live EventStream)."""

    id: str
    user_id: str = "default"
    status: SessionStatus = SessionStatus.ACTIVE
    workspace_path: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    title: str = ""
    event_count: int = 0
    plan_id: Optional[str] = None


class Session:
    """A live session object holding the event stream and associated state."""

    def __init__(
        self,
        session_id: str | None = None,
        user_id: str = "default",
        workspace_path: str = "",
        title: str = "",
    ) -> None:
        self.id = session_id or uuid.uuid4().hex
        self.user_id = user_id
        self.workspace_path = workspace_path
        self.title = title
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.event_stream = EventStream(session_id=self.id)
        self.plan_state: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}

    # ── Helpers ────────────────────────────────────────────────────
    def touch(self) -> None:
        """Bump the ``updated_at`` timestamp."""
        self.updated_at = datetime.now(UTC)

    def to_info(self) -> SessionInfo:
        """Create a serialisable snapshot."""
        return SessionInfo(
            id=self.id,
            user_id=self.user_id,
            status=self.status,
            workspace_path=self.workspace_path,
            created_at=self.created_at,
            updated_at=self.updated_at,
            title=self.title,
            event_count=len(self.event_stream),
            plan_id=self.plan_state.get("plan_id"),
        )

    def __repr__(self) -> str:
        return (
            f"<Session id={self.id!r} status={self.status} "
            f"events={len(self.event_stream)}>"
        )


# ────────────────────────────────────────────────────────────────────
# Session Manager
# ────────────────────────────────────────────────────────────────────

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default',
    status TEXT NOT NULL DEFAULT 'active',
    workspace_path TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class SessionManager:
    """In-memory session store with optional SQLite persistence layer.

    Parameters
    ----------
    db_path:
        Path to a SQLite database file.  If ``None`` sessions live only in
        memory for the lifetime of the process.
    """

    def __init__(self, db_path: str | None = None) -> None:
        self._sessions: dict[str, Session] = {}
        self._db_path = db_path

    # ── Lifecycle ──────────────────────────────────────────────────
    async def initialize(self) -> None:
        """Create the persistence table if a DB path was provided."""
        if self._db_path:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(_CREATE_TABLE_SQL)
                await db.commit()

    # ── CRUD ───────────────────────────────────────────────────────
    async def create_session(
        self,
        user_id: str = "default",
        workspace_path: str = "",
        title: str = "",
    ) -> Session:
        """Create and register a new session."""
        session = Session(
            user_id=user_id,
            workspace_path=workspace_path,
            title=title,
        )
        self._sessions[session.id] = session
        await self._persist(session)
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Return a session by ID, or ``None``."""
        return self._sessions.get(session_id)

    def list_sessions(self, user_id: str | None = None) -> list[SessionInfo]:
        """Return serialisable info objects for all (or a user's) sessions."""
        result = [
            s.to_info()
            for s in self._sessions.values()
            if user_id is None or s.user_id == user_id
        ]
        return sorted(result, key=lambda s: s.created_at, reverse=True)

    async def delete_session(self, session_id: str) -> bool:
        """Remove a session from memory and persistence.  Returns success."""
        if session_id not in self._sessions:
            return False
        del self._sessions[session_id]
        if self._db_path:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                await db.commit()
        return True

    async def update_session_status(
        self, session_id: str, status: SessionStatus
    ) -> None:
        """Update the status of a session."""
        session = self._sessions.get(session_id)
        if session:
            session.status = status
            session.touch()
            await self._persist(session)

    # ── Persistence helpers ────────────────────────────────────────
    async def _persist(self, session: Session) -> None:
        if not self._db_path:
            return
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO sessions
                    (id, user_id, status, workspace_path, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.user_id,
                    session.status.value,
                    session.workspace_path,
                    session.title,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                ),
            )
            await db.commit()

    async def load_from_db(self) -> None:
        """Restore session metadata from SQLite (events are *not* persisted)."""
        if not self._db_path:
            return
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM sessions") as cur:
                async for row in cur:
                    sid = row["id"]
                    if sid not in self._sessions:
                        s = Session(
                            session_id=sid,
                            user_id=row["user_id"],
                            workspace_path=row["workspace_path"],
                            title=row["title"],
                        )
                        s.status = SessionStatus(row["status"])
                        s.created_at = datetime.fromisoformat(row["created_at"])
                        s.updated_at = datetime.fromisoformat(row["updated_at"])
                        self._sessions[sid] = s
