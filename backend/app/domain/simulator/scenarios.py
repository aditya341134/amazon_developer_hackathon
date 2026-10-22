from __future__ import annotations

from typing import Any
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


DEFAULT_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_id": "s1_f1_unreachable",
        "routine_id": "r1",
        "name": "Device unreachable",
        "description": "Light endpoint is unreachable when Alexa tries to turn it on.",
        "seed": 1,
        "base_time": "2026-10-19T19:30:00Z",
        "fault": {"type": F1_UNREACHABLE},
    },
    {
        "scenario_id": "s2_f3_cap_mismatch",
        "routine_id": "r1",
        "name": "Capability mismatch",
        "description": "Brightness is declared but not actually supported at runtime.",
        "seed": 2,
        "base_time": "2026-10-19T22:15:00Z",
        "fault": {"type": F3_CAPABILITY_MISMATCH},
    },
    {
        "scenario_id": "s3_f2_stale_state",
        "routine_id": "r2",
        "name": "Stale lock state (timeOfSample)",
        "description": "Reported lock state is stale/incorrect, causing the routine to skip the action.",
        "seed": 3,
        "base_time": "2026-10-19T22:00:00Z",
        "fault": {"type": F2_STALE_STATE},
    },
]