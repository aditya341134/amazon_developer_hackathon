import unittest
from app.domain.simulator.world import SimulatedWorld
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


class TestSimulatorWorld(unittest.TestCase):
    def test_world_init_f1(self):
        s1 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s1_f1_unreachable")
        world = SimulatedWorld(s1)
        self.assertIn("light_1", world.devices)
        self.assertEqual(world.devices["light_1"].endpoint_health, "UNREACHABLE")

    def test_world_init_f2(self):
        s3 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s3_f2_stale_state")
        world = SimulatedWorld(s3)
        self.assertIn("lock_1", world.devices)
        lock = world.devices["lock_1"]
        self.assertEqual(lock.reported_state["lockState"], "LOCKED")
        self.assertEqual(lock.actual_state["lockState"], "UNLOCKED")
        self.assertIsNotNone(lock.time_of_sample)

    def test_world_init_f3(self):
        s2 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s2_f3_cap_mismatch")
        world = SimulatedWorld(s2)
        light = world.devices["light_1"]
        self.assertIn("Alexa.BrightnessController", light.declared_capabilities)
        self.assertNotIn("Alexa.BrightnessController", light.actual_capabilities)

    def test_capture_snapshots(self):
        s1 = DEFAULT_SCENARIOS[0]
        world = SimulatedWorld(s1)
        snaps = world.capture_all_snapshots(s1["base_time"])
        self.assertEqual(len(snaps), 3)
        snap_light = world.capture_snapshot("light_1", s1["base_time"])
        self.assertEqual(snap_light["device_id"], "light_1")
        self.assertEqual(snap_light["endpoint_health"], "UNREACHABLE")


if __name__ == "__main__":
    unittest.main()
