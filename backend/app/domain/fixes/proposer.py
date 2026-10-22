from __future__ import annotations

from typing import Any

from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


def propose_fixes(failure_type: str) -> list[dict[str, Any]]:
    # Returns patch objects that the engine knows how to apply during replay.
    if failure_type == F1_UNREACHABLE:
        return [
            {
                "mode": "routine",
                "title": "Add retry/backoff when device is unreachable",
                "why_it_works": "Retries can recover transient connectivity failures.",
                "auto_apply_ok": True,
                "patch": {"type": "ROUTINE_ADD_RETRY", "retries": 2, "backoff_seconds": [1, 3]},
            },
            {
                "mode": "integration",
                "title": "Improve endpoint health reporting and connectivity recovery",
                "why_it_works": "Accurate endpoint health helps Alexa avoid acting on unreachable devices.",
                "auto_apply_ok": False,
                "patch": {"type": "INTEGRATION_ENDPOINT_HEALTH_FIX"},
            },
        ]

    if failure_type == F2_STALE_STATE:
        return [
            {
                "mode": "routine",
                "title": "Refresh lock state if stale, then re-evaluate the condition",
                "why_it_works": "Prevents decisions based on outdated timeOfSample values.",
                "auto_apply_ok": True,
                "patch": {"type": "ROUTINE_REFRESH_STATE", "device_id": "lock_1", "max_age_seconds": 60},
            },
            {
                "mode": "integration",
                "title": "Send ChangeReport promptly and set correct timeOfSample",
                "why_it_works": "Keeps reported state accurate and fresh for routine evaluation.",
                "auto_apply_ok": False,
                "patch": {"type": "INTEGRATION_REPORTING_FIX"},
            },
        ]

    if failure_type == F3_CAPABILITY_MISMATCH:
        return [
            {
                "mode": "routine",
                "title": "Degrade gracefully: skip brightness if unsupported",
                "why_it_works": "Avoids failing the routine when the device can't dim.",
                "auto_apply_ok": True,
                "patch": {"type": "ROUTINE_DEGRADE_BRIGHTNESS"},
            },
            {
                "mode": "integration",
                "title": "Fix capability implementation or declaration for brightness",
                "why_it_works": "Ensures discovery and runtime behavior match.",
                "auto_apply_ok": False,
                "patch": {"type": "INTEGRATION_ACTUAL_CAPS_ADD", "device_id": "light_1", "capability": "Alexa.BrightnessController"},
            },
        ]

    return []