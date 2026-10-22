from __future__ import annotations

from typing import Any
from app.util.ids import new_id


def make_event(ts: str, kind: str, summary: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": new_id("evt"),
        "ts": ts,
        "kind": kind,
        "summary": summary,
        "payload": payload,
    }