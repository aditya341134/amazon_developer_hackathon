from __future__ import annotations

from datetime import datetime, timedelta, timezone


def parse_iso(ts: str) -> datetime:
    # Accept "Z"
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def add_seconds(base_ts: str, seconds: float) -> str:
    dt = parse_iso(base_ts) + timedelta(seconds=seconds)
    return to_iso(dt)