from __future__ import annotations

from typing import Any


def build_graph_for_run(routine_id: str) -> dict[str, Any]:
    if routine_id == "r1":
        return {
            "nodes": [
                {"id": "n_trigger", "kind": "TRIGGER", "label": "motion_1 detected"},
                {"id": "n_action_on", "kind": "ACTION", "label": "light_1 TurnOn", "ref": "a1"},
                {"id": "n_cond_night", "kind": "CONDITION", "label": "After 21:00?", "ref": "c1"},
                {"id": "n_action_dim", "kind": "ACTION", "label": "light_1 SetBrightness 30%", "ref": "a2"},
                {"id": "n_assert", "kind": "ASSERT", "label": "Expect light ON within 5s", "ref": "e1"},
            ],
            "edges": [
                {"from": "n_trigger", "to": "n_action_on"},
                {"from": "n_action_on", "to": "n_cond_night"},
                {"from": "n_cond_night", "to": "n_action_dim", "when": "true"},
                {"from": "n_cond_night", "to": "n_assert", "when": "false"},
                {"from": "n_action_dim", "to": "n_assert"},
            ],
        }

    # r2
    return {
        "nodes": [
            {"id": "n_trigger", "kind": "TRIGGER", "label": "motion_1 detected"},
            {"id": "n_cond_lock", "kind": "CONDITION", "label": "Lock is UNLOCKED (fresh<=60s)", "ref": "c_lock_unlocked"},
            {"id": "n_action_on", "kind": "ACTION", "label": "light_1 TurnOn", "ref": "a_light_on"},
            {"id": "n_assert", "kind": "ASSERT", "label": "Expect light ON within 5s", "ref": "e_light_on"},
        ],
        "edges": [
            {"from": "n_trigger", "to": "n_cond_lock"},
            {"from": "n_cond_lock", "to": "n_action_on", "when": "true"},
            {"from": "n_cond_lock", "to": "n_assert", "when": "false"},
            {"from": "n_action_on", "to": "n_assert"},
        ],
    }