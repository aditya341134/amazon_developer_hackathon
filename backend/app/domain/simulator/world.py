from __future__ import annotations

from typing import Any
from dataclasses import dataclass, field
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH
from app.util.time import add_seconds
from app.util.ids import new_id


@dataclass
class DeviceState:
    device_id: str
    endpoint_health: str = "OK"  # "OK" or "UNREACHABLE"
    actual_state: dict[str, Any] = field(default_factory=dict)
    reported_state: dict[str, Any] = field(default_factory=dict)
    time_of_sample: str | None = None
    declared_capabilities: list[str] = field(default_factory=list)
    actual_capabilities: list[str] = field(default_factory=list)

    def snapshot(self, ts: str) -> dict[str, Any]:
        return {
            "snapshot_id": new_id("snap"),
            "ts": ts,
            "device_id": self.device_id,
            "endpoint_health": self.endpoint_health,
            "actual_state": dict(self.actual_state),
            "reported_state": dict(self.reported_state),
            "time_of_sample": self.time_of_sample,
            "declared_capabilities": list(self.declared_capabilities),
            "actual_capabilities": list(self.actual_capabilities),
        }


class SimulatedWorld:
    def __init__(self, scenario_def: dict[str, Any], patches: list[dict[str, Any]] | None = None):
        self.scenario_def = scenario_def
        self.patches = patches or []
        self.base_time = scenario_def["base_time"]
        self.fault_type = scenario_def.get("fault", {}).get("type")
        self.devices: dict[str, DeviceState] = {}
        self.snapshots: list[dict[str, Any]] = []
        self._init_world()

    def _has_patch(self, patch_type: str) -> bool:
        return any(p.get("type") == patch_type for p in self.patches)

    def _init_world(self) -> None:
        routine_id = self.scenario_def.get("routine_id", "r1")

        # 1. Motion Sensor (motion_1)
        self.devices["motion_1"] = DeviceState(
            device_id="motion_1",
            endpoint_health="OK",
            actual_state={"motion": "DETECTED"},
            reported_state={"motion": "DETECTED"},
            time_of_sample=self.base_time,
            declared_capabilities=["Alexa.MotionSensor"],
            actual_capabilities=["Alexa.MotionSensor"],
        )

        # 2. Entry / Porch Light (light_1)
        light_health = "OK"
        if self.fault_type == F1_UNREACHABLE:
            # If integration fix or retry patch is applied, endpoint recovers
            if self._has_patch("INTEGRATION_ENDPOINT_HEALTH_FIX") or self._has_patch("ROUTINE_ADD_RETRY"):
                light_health = "OK"
            else:
                light_health = "UNREACHABLE"

        declared_light_caps = ["Alexa.PowerController"]
        actual_light_caps = ["Alexa.PowerController"]

        if routine_id == "r1":
            declared_light_caps = ["Alexa.PowerController", "Alexa.BrightnessController"]
            if self.fault_type == F3_CAPABILITY_MISMATCH and not self._has_patch("INTEGRATION_ACTUAL_CAPS_ADD"):
                actual_light_caps = ["Alexa.PowerController"]  # Mismatch: declared has brightness, actual does not
            else:
                actual_light_caps = ["Alexa.PowerController", "Alexa.BrightnessController"]

        self.devices["light_1"] = DeviceState(
            device_id="light_1",
            endpoint_health=light_health,
            actual_state={"power": "OFF", "brightness": 0},
            reported_state={"power": "OFF", "brightness": 0},
            time_of_sample=self.base_time,
            declared_capabilities=declared_light_caps,
            actual_capabilities=actual_light_caps,
        )

        # 3. Smart Door Lock (lock_1)
        lock_reported_state = {"lockState": "UNLOCKED"}
        lock_tos = self.base_time

        if self.fault_type == F2_STALE_STATE:
            if self._has_patch("INTEGRATION_REPORTING_FIX") or self._has_patch("ROUTINE_REFRESH_STATE"):
                lock_reported_state = {"lockState": "UNLOCKED"}
                lock_tos = add_seconds(self.base_time, -10)
            else:
                # Stale sample: 20 minutes before base_time
                lock_reported_state = {"lockState": "LOCKED"}
                lock_tos = add_seconds(self.base_time, -1200)

        self.devices["lock_1"] = DeviceState(
            device_id="lock_1",
            endpoint_health="OK",
            actual_state={"lockState": "UNLOCKED"},
            reported_state=lock_reported_state,
            time_of_sample=lock_tos,
            declared_capabilities=["Alexa.LockController"],
            actual_capabilities=["Alexa.LockController"],
        )

    def capture_snapshot(self, device_id: str, ts: str) -> dict[str, Any]:
        dev = self.devices.get(device_id)
        if not dev:
            raise KeyError(f"Unknown device: {device_id}")
        snap = dev.snapshot(ts)
        self.snapshots.append(snap)
        return snap

    def capture_all_snapshots(self, ts: str) -> list[dict[str, Any]]:
        snaps = []
        for dev in self.devices.values():
            snap = dev.snapshot(ts)
            self.snapshots.append(snap)
            snaps.append(snap)
        return snaps
