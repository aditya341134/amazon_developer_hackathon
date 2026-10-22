from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel


EventKind = Literal[
    "SENSOR_EVENT",
    "DECISION",
    "DIRECTIVE",
    "RESPONSE",
    "ASSERT",
    "INFO",
]


class Event(BaseModel):
    event_id: str
    ts: str
    kind: EventKind
    summary: str
    payload: dict[str, Any]