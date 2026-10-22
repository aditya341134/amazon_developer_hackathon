from __future__ import annotations

from typing import Any


def classify(primary_failure_type: str | None) -> str | None:
    # For MVP, classification is already produced deterministically by engine.
    # This module exists so later you can classify from raw traces/events.
    return primary_failure_type