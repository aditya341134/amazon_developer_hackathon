from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class Trigger(BaseModel):
    type: str
    device_id: str


class Condition(BaseModel):
    id: str
    type: str
    device_id: Optional[str] = None
    property: Optional[str] = None
    equals: Optional[str] = None
    freshness_seconds: Optional[int] = None
    value: Optional[str] = None


class Action(BaseModel):
    id: str
    type: str
    device_id: str
    value: Optional[int] = None
    only_if: Optional[str] = None


class Expectation(BaseModel):
    id: str
    type: str
    device_id: str
    property: str
    equals: str
    within_seconds: int = 5


class RoutineSpec(BaseModel):
    routine_id: str
    name: str
    description: str
    trigger: Trigger
    conditions: list[Condition] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    expectations: list[Expectation] = Field(default_factory=list)


# ---- Seed routines (JSON-like dicts) ----
ROUTINE_R1: dict[str, Any] = {
    "routine_id": "r1",
    "name": "Arrival safety light",
    "description": "When motion is detected, turn on entry light. If it's late, dim it.",
    "trigger": {"type": "motion.detected", "device_id": "motion_1"},
    "conditions": [
        {"id": "c1", "type": "time.after", "value": "21:00"}
    ],
    "actions": [
        {"id": "a1", "type": "light.power_on", "device_id": "light_1"},
        {"id": "a2", "type": "light.set_brightness", "device_id": "light_1", "value": 30, "only_if": "c1"},
    ],
    "expectations": [
        {"id": "e1", "type": "device_state", "device_id": "light_1", "property": "power", "equals": "ON", "within_seconds": 5}
    ],
}

ROUTINE_R2: dict[str, Any] = {
    "routine_id": "r2",
    "name": "Porch light when door is unlocked",
    "description": "Turn on porch light when motion is detected and the door is unlocked.",
    "trigger": {"type": "motion.detected", "device_id": "motion_1"},
    "conditions": [
        {
            "id": "c_lock_unlocked",
            "type": "device_property_equals",
            "device_id": "lock_1",
            "property": "lockState",
            "equals": "UNLOCKED",
            "freshness_seconds": 60,
        }
    ],
    "actions": [
        {"id": "a_light_on", "type": "light.power_on", "device_id": "light_1", "only_if": "c_lock_unlocked"}
    ],
    "expectations": [
        {"id": "e_light_on", "type": "device_state", "device_id": "light_1", "property": "power", "equals": "ON", "within_seconds": 5}
    ],
}

DEFAULT_ROUTINES: list[dict[str, Any]] = [ROUTINE_R1, ROUTINE_R2]