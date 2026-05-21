"""Immutable event system inspired by OpenHands.

Every action, observation, plan update, and error in the system is recorded as
an immutable event in an append-only ``EventStream``.  Events are frozen
Pydantic models and can be serialised to JSON for persistence or WebSocket
streaming.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────────────
# Enums
# ────────────────────────────────────────────────────────────────────

class EventType(StrEnum):
    """Discriminator for all event kinds."""

    MESSAGE = "message"
    ACTION = "action"
    OBSERVATION = "observation"
    PLAN = "plan"
    DELEGATION = "delegation"
    ERROR = "error"
    CONDENSATION = "condensation"


class ActionType(StrEnum):
    """Sub-discriminator for action events."""

    CMD_RUN = "cmd_run"
    FILE_EDIT = "file_edit"
    PYTHON_RUN = "python_run"
    BROWSER = "browser"
    TOOL_CALL = "tool_call"


class PlanStepStatus(StrEnum):
    """Status of an individual plan step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ────────────────────────────────────────────────────────────────────
# Base Event
# ────────────────────────────────────────────────────────────────────

class Event(BaseModel):
    """Immutable base event.  All events inherit from this."""

    model_config = {"frozen": True}

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: EventType
    session_id: str = ""
    source: str = ""


# ────────────────────────────────────────────────────────────────────
# Concrete Event Types
# ────────────────────────────────────────────────────────────────────

class MessageEvent(Event):
    """A user or assistant chat message."""

    event_type: EventType = EventType.MESSAGE
    role: str = "user"
    content: str = ""
    attachments: list[str] = Field(default_factory=list)


class ActionEvent(Event):
    """An agent action (command, file edit, tool call, …)."""

    event_type: EventType = EventType.ACTION
    action_type: ActionType = ActionType.TOOL_CALL
    tool_name: str = ""
    tool_args: dict[str, Any] = Field(default_factory=dict)
    thought: str = ""


class CmdRunAction(ActionEvent):
    """Shell command execution."""

    action_type: ActionType = ActionType.CMD_RUN
    command: str = ""
    timeout: int = 120


class FileEditAction(ActionEvent):
    """File read / write / patch."""

    action_type: ActionType = ActionType.FILE_EDIT
    path: str = ""
    content: str = ""
    old_content: Optional[str] = None


class PythonRunAction(ActionEvent):
    """In-process or subprocess Python execution."""

    action_type: ActionType = ActionType.PYTHON_RUN
    code: str = ""


class BrowserAction(ActionEvent):
    """Browser-automation action."""

    action_type: ActionType = ActionType.BROWSER
    url: str = ""
    instruction: str = ""


class ToolCallAction(ActionEvent):
    """Generic tool / function call."""

    action_type: ActionType = ActionType.TOOL_CALL


class ObservationEvent(Event):
    """Result / output of an action."""

    event_type: EventType = EventType.OBSERVATION
    content: str = ""
    exit_code: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    action_id: str = ""


class PlanEvent(Event):
    """A planning lifecycle event (create / update / step complete)."""

    event_type: EventType = EventType.PLAN
    plan_id: str = ""
    title: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)
    current_step_index: int = 0
    status: str = "in_progress"


class DelegationEvent(Event):
    """Records delegation of work to a sub-agent."""

    event_type: EventType = EventType.DELEGATION
    from_agent: str = ""
    to_agent: str = ""
    task: str = ""


class ErrorEvent(Event):
    """An error encountered during processing."""

    event_type: EventType = EventType.ERROR
    error_type: str = "runtime"
    message: str = ""
    traceback: Optional[str] = None


class CondensationEvent(Event):
    """Records a context-condensation operation."""

    event_type: EventType = EventType.CONDENSATION
    original_count: int = 0
    condensed_count: int = 0
    summary: str = ""


# ────────────────────────────────────────────────────────────────────
# EventStream
# ────────────────────────────────────────────────────────────────────

# Type alias for subscriber callbacks.
EventCallback = Callable[[Event], Any]


class EventStream:
    """Append-only, observable stream of ``Event`` objects.

    Subscribers are notified synchronously on ``append``.  The stream is
    the single source of truth for everything that has happened in a session.
    """

    def __init__(self, session_id: str = "") -> None:
        self.session_id = session_id
        self._events: list[Event] = []
        self._subscribers: list[EventCallback] = []
        self._id_index: dict[str, int] = {}  # event_id → position

    # ── Mutations ───────────────────────────────────────────────────
    def append(self, event: Event) -> Event:
        """Append an event and notify all subscribers.

        If the event's ``session_id`` is empty it is automatically set to the
        stream's own ``session_id``.

        Returns the (possibly updated) event.
        """
        if not event.session_id and self.session_id:
            # Frozen model – must reconstruct with the session_id set.
            event = event.model_copy(update={"session_id": self.session_id})

        pos = len(self._events)
        self._events.append(event)
        self._id_index[event.id] = pos

        for callback in self._subscribers:
            try:
                callback(event)
            except Exception:  # noqa: BLE001 – subscribers must not break the stream
                pass

        return event

    # ── Queries ─────────────────────────────────────────────────────
    def get_events(
        self,
        after_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        limit: int = 200,
    ) -> list[Event]:
        """Return events, optionally filtered and paginated."""
        start = 0
        if after_id and after_id in self._id_index:
            start = self._id_index[after_id] + 1

        result: list[Event] = []
        for ev in self._events[start:]:
            if event_type and ev.event_type != event_type:
                continue
            result.append(ev)
            if len(result) >= limit:
                break
        return result

    def get_event(self, event_id: str) -> Optional[Event]:
        """Look up a single event by ID."""
        idx = self._id_index.get(event_id)
        if idx is not None:
            return self._events[idx]
        return None

    @property
    def last(self) -> Optional[Event]:
        """Return the most recent event, or ``None``."""
        return self._events[-1] if self._events else None

    def __len__(self) -> int:
        return len(self._events)

    # ── Subscriptions ───────────────────────────────────────────────
    def subscribe(self, callback: EventCallback) -> None:
        """Register a callback invoked on every ``append``."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: EventCallback) -> None:
        """Remove a previously registered callback."""
        self._subscribers = [s for s in self._subscribers if s is not callback]

    # ── Serialisation ───────────────────────────────────────────────
    def to_json(self) -> list[dict[str, Any]]:
        """Serialise the full stream to a list of dicts."""
        return [ev.model_dump(mode="json") for ev in self._events]

    def __repr__(self) -> str:
        return f"<EventStream session={self.session_id!r} events={len(self._events)}>"
