import unittest
from app.domain.routines.models import ROUTINE_R1
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.routines.engine import execute_run
from app.domain.simulator.faults import F1_UNREACHABLE


class TestF1Unreachable(unittest.TestCase):
    def setUp(self):
        self.scenario = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s1_f1_unreachable")

    def test_f1_fails_with_unreachable(self):
        res = execute_run(ROUTINE_R1, self.scenario)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["primary_failure_type"], F1_UNREACHABLE)

        # Node check
        exec_info = res["graph"]["execution"]
        self.assertEqual(exec_info["failed_node_id"], "n_action_on")
        self.assertEqual(exec_info["node_status"]["n_action_on"]["status"], "FAILED")

        # Snapshot check
        self.assertTrue(len(res["snapshots"]) > 0)
        light_snaps = [s for s in res["snapshots"] if s["device_id"] == "light_1"]
        self.assertTrue(any(s["endpoint_health"] == "UNREACHABLE" for s in light_snaps))

        # Events check
        directive_events = [e for e in res["events"] if e["kind"] == "DIRECTIVE"]
        self.assertTrue(len(directive_events) > 0)
        error_events = [e for e in res["events"] if e.get("payload", {}).get("name") == "ErrorResponse"]
        self.assertTrue(len(error_events) > 0)
        self.assertEqual(error_events[0]["payload"]["errorType"], "ENDPOINT_UNREACHABLE")


if __name__ == "__main__":
    unittest.main()
