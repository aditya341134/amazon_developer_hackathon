from __future__ import annotations

from typing import Any

from app.domain.events.logger import make_event
from app.domain.routines.compiler import build_graph_for_run
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH
from app.domain.simulator.world import SimulatedWorld
from app.domain.diagnostics.explainer import explain_failure
from app.util.time import add_seconds


def _has_patch(patches: list[dict[str, Any]], patch_type: str) -> bool:
    return any(p.get("type") == patch_type for p in patches)


def execute_run(
    routine_spec: dict[str, Any],
    scenario_def: dict[str, Any],
    patches: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    patches = patches or []
    routine_id = routine_spec["routine_id"]
    base_time = scenario_def["base_time"]
    fault_type = scenario_def["fault"]["type"]

    # Initialize simulated world
    world = SimulatedWorld(scenario_def=scenario_def, patches=patches)
    # Capture initial device state snapshot
    world.capture_all_snapshots(base_time)

    events: list[dict[str, Any]] = []

    # trigger
    events.append(make_event(base_time, "SENSOR_EVENT", "Motion detected", {"device_id": "motion_1", "value": "MOTION"}))

    graph = build_graph_for_run(routine_id)
    node_status: dict[str, Any] = {}
    failed_node_id: str | None = None

    def mark(node_id: str, status: str, ts: str, event_id: str):
        node_status[node_id] = {"status": status, "at": ts, "event_id": event_id}

    # defaults
    status = "PASS"
    primary_failure_type: str | None = None

    # Simulated logic branches
    if routine_id == "r1":
        # n_action_on
        ts_on = add_seconds(base_time, 1)
        e_dir_on = make_event(ts_on, "DIRECTIVE", "Attempting to turn on entry light", {
            "namespace": "Alexa.PowerController",
            "name": "TurnOn",
            "endpointId": "light_1",
            "payload": {},
        })
        events.append(e_dir_on)
        mark("n_trigger", "SUCCESS", base_time, events[0]["event_id"])

        # F1: unreachable unless fixed by retry or integration patch
        if fault_type == F1_UNREACHABLE and not (_has_patch(patches, "ROUTINE_ADD_RETRY") or _has_patch(patches, "INTEGRATION_ENDPOINT_HEALTH_FIX")):
            e_resp = make_event(ts_on, "RESPONSE", "Device unreachable", {
                "name": "ErrorResponse",
                "errorType": "ENDPOINT_UNREACHABLE",
                "message": "Endpoint unreachable",
            })
            events.append(e_resp)
            mark("n_action_on", "FAILED", ts_on, e_resp["event_id"])
            failed_node_id = "n_action_on"
            primary_failure_type = F1_UNREACHABLE
            status = "FAIL"
            world.capture_snapshot("light_1", ts_on)
        else:
            # Success path; if retry patch exists, show a failed attempt then a success retry (nice demo)
            if fault_type == F1_UNREACHABLE and _has_patch(patches, "ROUTINE_ADD_RETRY"):
                e_first_fail = make_event(ts_on, "RESPONSE", "Initial attempt failed, retrying...", {
                    "name": "ErrorResponse",
                    "errorType": "ENDPOINT_UNREACHABLE",
                    "message": "Transient failure",
                })
                events.append(e_first_fail)
                e_retry = make_event(add_seconds(base_time, 2), "INFO", "Retry succeeded", {"retries": 1})
                events.append(e_retry)

            e_resp_ok = make_event(ts_on, "RESPONSE", "Light turned on", {"name": "Response"})
            events.append(e_resp_ok)
            mark("n_action_on", "SUCCESS", ts_on, e_resp_ok["event_id"])
            world.devices["light_1"].actual_state["power"] = "ON"
            world.devices["light_1"].reported_state["power"] = "ON"
            world.capture_snapshot("light_1", ts_on)

            # condition after 21:00 -> true in our scenarios (since base_time for r1 is 19:30 or 22:15)
            cond_ts = add_seconds(base_time, 1.2)
            is_night = scenario_def["base_time"].endswith("22:15:00Z")  # scenario 2 is late
            e_cond = make_event(cond_ts, "DECISION", "Evaluating time condition (after 21:00)", {"result": is_night})
            events.append(e_cond)
            mark("n_cond_night", "SUCCESS", cond_ts, e_cond["event_id"])

            if is_night:
                # brightness step
                dim_ts = add_seconds(base_time, 1.4)

                # If degrade patch exists, skip brightness
                if _has_patch(patches, "ROUTINE_DEGRADE_BRIGHTNESS"):
                    e_skip = make_event(dim_ts, "INFO", "Skipping brightness adjustment (not supported)", {"reason": "degrade_gracefully"})
                    events.append(e_skip)
                    mark("n_action_dim", "SKIPPED", dim_ts, e_skip["event_id"])
                else:
                    e_dir_dim = make_event(dim_ts, "DIRECTIVE", "Setting brightness to 30%", {
                        "namespace": "Alexa.BrightnessController",
                        "name": "SetBrightness",
                        "endpointId": "light_1",
                        "payload": {"brightness": 30},
                    })
                    events.append(e_dir_dim)

                    # F3 mismatch unless integration patch adds capability
                    if fault_type == F3_CAPABILITY_MISMATCH and not _has_patch(patches, "INTEGRATION_ACTUAL_CAPS_ADD"):
                        e_dim_fail = make_event(dim_ts, "RESPONSE", "Brightness not supported", {
                            "name": "ErrorResponse",
                            "errorType": "INVALID_DIRECTIVE",
                            "message": "BrightnessController not supported",
                            "declared_capabilities": ["Alexa.PowerController", "Alexa.BrightnessController"],
                            "actual_capabilities": ["Alexa.PowerController"],
                        })
                        events.append(e_dim_fail)
                        mark("n_action_dim", "FAILED", dim_ts, e_dim_fail["event_id"])
                        failed_node_id = "n_action_dim"
                        primary_failure_type = F3_CAPABILITY_MISMATCH
                        status = "FAIL"
                        world.capture_snapshot("light_1", dim_ts)
                    else:
                        e_dim_ok = make_event(dim_ts, "RESPONSE", "Brightness set", {"name": "Response"})
                        events.append(e_dim_ok)
                        mark("n_action_dim", "SUCCESS", dim_ts, e_dim_ok["event_id"])
                        world.devices["light_1"].actual_state["brightness"] = 30
                        world.devices["light_1"].reported_state["brightness"] = 30
                        world.capture_snapshot("light_1", dim_ts)

            # assert
            assert_ts = add_seconds(base_time, 2.0)
            if status == "FAIL":
                e_assert = make_event(assert_ts, "ASSERT", "Expectation failed: light should be ON within 5 seconds", {
                    "expected": "light_1 power=ON",
                    "within_seconds": 5,
                    "result": "FAIL",
                })
                events.append(e_assert)
                mark("n_assert", "FAILED", assert_ts, e_assert["event_id"])
            else:
                e_assert = make_event(assert_ts, "ASSERT", "Expectation met: light is ON", {
                    "expected": "light_1 power=ON",
                    "within_seconds": 5,
                    "result": "PASS",
                })
                events.append(e_assert)
                mark("n_assert", "SUCCESS", assert_ts, e_assert["event_id"])

    else:
        # r2: lock freshness condition
        mark("n_trigger", "SUCCESS", base_time, events[0]["event_id"])

        cond_ts = add_seconds(base_time, 0.5)

        stale = (fault_type == F2_STALE_STATE) and not (_has_patch(patches, "ROUTINE_REFRESH_STATE") or _has_patch(patches, "INTEGRATION_REPORTING_FIX"))
        if stale:
            e_cond = make_event(cond_ts, "DECISION", "Evaluating lock condition using reported state (STALE)", {
                "device_id": "lock_1",
                "reported_lockState": "LOCKED",
                "reported_timeOfSample": "2026-10-19T21:40:00Z",
                "freshness_limit_seconds": 60,
                "result": False,
            })
            events.append(e_cond)
            mark("n_cond_lock", "FAILED", cond_ts, e_cond["event_id"])
            failed_node_id = "n_cond_lock"
            primary_failure_type = F2_STALE_STATE
            status = "FAIL"
            world.capture_snapshot("lock_1", cond_ts)

            assert_ts = add_seconds(base_time, 2.0)
            e_assert = make_event(assert_ts, "ASSERT", "Expectation failed: light should be ON", {
                "expected": "light_1 power=ON",
                "within_seconds": 5,
                "result": "FAIL",
            })
            events.append(e_assert)
            mark("n_assert", "FAILED", assert_ts, e_assert["event_id"])

        else:
            # If refresh patch, include refresh event
            if fault_type == F2_STALE_STATE and _has_patch(patches, "ROUTINE_REFRESH_STATE"):
                e_refresh = make_event(add_seconds(base_time, 0.3), "INFO", "Refreshing lock state due to stale timeOfSample", {
                    "device_id": "lock_1",
                    "action": "refresh_state",
                    "max_age_seconds": 60,
                })
                events.append(e_refresh)
                world.devices["lock_1"].reported_state["lockState"] = "UNLOCKED"
                world.devices["lock_1"].time_of_sample = add_seconds(base_time, 0.2)
                world.capture_snapshot("lock_1", add_seconds(base_time, 0.3))

            e_cond = make_event(cond_ts, "DECISION", "Lock condition evaluated true (fresh)", {
                "device_id": "lock_1",
                "reported_lockState": "UNLOCKED",
                "reported_timeOfSample": add_seconds(base_time, 0.2),
                "freshness_limit_seconds": 60,
                "result": True,
            })
            events.append(e_cond)
            mark("n_cond_lock", "SUCCESS", cond_ts, e_cond["event_id"])

            # action
            act_ts = add_seconds(base_time, 1.0)
            e_dir = make_event(act_ts, "DIRECTIVE", "Turning on porch light", {
                "namespace": "Alexa.PowerController",
                "name": "TurnOn",
                "endpointId": "light_1",
                "payload": {},
            })
            events.append(e_dir)

            e_resp = make_event(act_ts, "RESPONSE", "Light turned on", {"name": "Response"})
            events.append(e_resp)
            mark("n_action_on", "SUCCESS", act_ts, e_resp["event_id"])
            world.devices["light_1"].actual_state["power"] = "ON"
            world.devices["light_1"].reported_state["power"] = "ON"
            world.capture_snapshot("light_1", act_ts)

            # assert
            assert_ts = add_seconds(base_time, 2.0)
            e_assert = make_event(assert_ts, "ASSERT", "Expectation met: light is ON", {
                "expected": "light_1 power=ON",
                "within_seconds": 5,
                "result": "PASS",
            })
            events.append(e_assert)
            mark("n_assert", "SUCCESS", assert_ts, e_assert["event_id"])

    graph_out = {
        "run_id": None,  # filled by caller when run_id known
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "execution": {
            "node_status": node_status,
            "failed_node_id": failed_node_id,
        },
    }

    # Explain (evidence = all events for MVP; pass snapshot facts)
    when_ts = events[-1]["ts"] if events else base_time
    evidence_ids = [e["event_id"] for e in events]
    explain_out = None
    if status == "FAIL" and primary_failure_type and failed_node_id:
        explain_out = {
            "run_id": None,
            **explain_failure(
                primary_failure_type,
                when_ts,
                failed_node_id,
                evidence_ids,
                snapshot_facts=world.snapshots,
            ),
        }
    else:
        explain_out = {
            "run_id": None,
            "classification": None,
            "homeowner": {
                "what": "Routine succeeded",
                "when": when_ts,
                "why": "No failure detected.",
                "next_steps": ["No action needed."],
            },
            "developer": {
                "failed_node_id": None,
                "evidence": [{"type": "EVENT_TRACE", "event_ids": evidence_ids, "snapshots": world.snapshots}],
                "recommended_fix_modes": [],
            },
        }

    return {
        "status": status,
        "primary_failure_type": primary_failure_type,
        "events": events,
        "graph": graph_out,
        "explain": explain_out,
        "snapshots": world.snapshots,
    }