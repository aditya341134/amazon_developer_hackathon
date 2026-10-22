from __future__ import annotations

from typing import Any

from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


def explain_failure(
    failure_type: str,
    when_ts: str,
    failed_node_id: str,
    evidence_event_ids: list[str],
    snapshot_facts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot_facts = snapshot_facts or []

    if failure_type == F1_UNREACHABLE:
        homeowner = {
            "what": "Entry light didn't turn on",
            "when": when_ts,
            "why": "Alexa couldn't reach the light device (device unreachable).",
            "next_steps": [
                "Check the light's power or connectivity",
                "Apply the retry fix and replay to confirm",
            ],
        }
        dev_evidence = [
            {
                "type": "ENDPOINT_UNREACHABLE",
                "device_id": "light_1",
                "property": "endpoint_health",
                "reported_value": "UNREACHABLE",
                "actual_value": "UNREACHABLE",
                "event_ids": evidence_event_ids,
                "snapshots": snapshot_facts,
            }
        ]
    elif failure_type == F3_CAPABILITY_MISMATCH:
        homeowner = {
            "what": "Light dimming failed",
            "when": when_ts,
            "why": "This bulb doesn't support brightness (capability mismatch).",
            "next_steps": [
                "Apply the 'degrade gracefully' routine fix",
                "Or update the device integration to support brightness",
            ],
        }
        dev_evidence = [
            {
                "type": "CAPABILITY_MISMATCH",
                "device_id": "light_1",
                "property": "capabilities",
                "declared_capabilities": ["Alexa.PowerController", "Alexa.BrightnessController"],
                "actual_capabilities": ["Alexa.PowerController"],
                "event_ids": evidence_event_ids,
                "snapshots": snapshot_facts,
            }
        ]
    elif failure_type == F2_STALE_STATE:
        homeowner = {
            "what": "Porch light didn't turn on",
            "when": when_ts,
            "why": "Alexa used an out-of-date lock status (stale timeOfSample).",
            "next_steps": [
                "Check that the lock is online",
                "Apply the 'refresh state if stale' fix and replay",
            ],
        }
        dev_evidence = [
            {
                "type": "STALE_TIME_OF_SAMPLE",
                "device_id": "lock_1",
                "property": "lockState",
                "reported_value": "LOCKED",
                "actual_value": "UNREACHABLE" if False else "UNLOCKED",
                "freshness_limit_seconds": 60,
                "event_ids": evidence_event_ids,
                "snapshots": snapshot_facts,
            }
        ]
    else:
        homeowner = {
            "what": "Routine failed",
            "when": when_ts,
            "why": "Unknown failure",
            "next_steps": ["Check logs and retry"],
        }
        dev_evidence = [
            {
                "type": "UNKNOWN",
                "event_ids": evidence_event_ids,
                "snapshots": snapshot_facts,
            }
        ]

    return {
        "classification": failure_type,
        "homeowner": homeowner,
        "developer": {
            "failed_node_id": failed_node_id,
            "evidence": dev_evidence,
            "recommended_fix_modes": ["routine", "integration"],
        },
    }