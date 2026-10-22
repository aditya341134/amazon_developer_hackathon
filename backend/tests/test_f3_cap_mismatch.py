import unittest
from app.domain.routines.models import ROUTINE_R1
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.routines.engine import execute_run
from app.domain.simulator.faults import F3_CAPABILITY_MISMATCH


class TestF3CapabilityMismatch(unittest.TestCase):
    def setUp(self):
        self.scenario = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s2_f3_cap_mismatch")

    def test_f3_fails_with_cap_mismatch(self):
        res = execute_run(ROUTINE_R1, self.scenario)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["primary_failure_type"], F3_CAPABILITY_MISMATCH)

        exec_info = res["graph"]["execution"]
        self.assertEqual(exec_info["failed_node_id"], "n_action_dim")
        self.assertEqual(exec_info["node_status"]["n_action_dim"]["status"], "FAILED")

        # Snapshot check
        light_snaps = [s for s in res["snapshots"] if s["device_id"] == "light_1"]
        self.assertTrue(len(light_snaps) > 0)
        self.assertIn("Alexa.BrightnessController", light_snaps[0]["declared_capabilities"])
        self.assertNotIn("Alexa.BrightnessController", light_snaps[0]["actual_capabilities"])

        # Error response check
        err_events = [e for e in res["events"] if e.get("payload", {}).get("name") == "ErrorResponse"]
        self.assertTrue(len(err_events) > 0)
        self.assertEqual(err_events[0]["payload"]["errorType"], "INVALID_DIRECTIVE")


if __name__ == "__main__":
    unittest.main()
