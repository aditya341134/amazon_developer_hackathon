import unittest
from app.domain.routines.models import ROUTINE_R2
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.routines.engine import execute_run
from app.domain.simulator.faults import F2_STALE_STATE


class TestF2StaleState(unittest.TestCase):
    def setUp(self):
        self.scenario = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s3_f2_stale_state")

    def test_f2_fails_with_stale_state(self):
        res = execute_run(ROUTINE_R2, self.scenario)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["primary_failure_type"], F2_STALE_STATE)

        exec_info = res["graph"]["execution"]
        self.assertEqual(exec_info["failed_node_id"], "n_cond_lock")
        self.assertEqual(exec_info["node_status"]["n_cond_lock"]["status"], "FAILED")

        # Snapshot check
        lock_snaps = [s for s in res["snapshots"] if s["device_id"] == "lock_1"]
        self.assertTrue(len(lock_snaps) > 0)
        self.assertEqual(lock_snaps[0]["reported_state"]["lockState"], "LOCKED")
        self.assertEqual(lock_snaps[0]["actual_state"]["lockState"], "UNLOCKED")

        # Decision event check
        decisions = [e for e in res["events"] if e["kind"] == "DECISION"]
        self.assertTrue(len(decisions) > 0)
        self.assertFalse(decisions[0]["payload"]["result"])


if __name__ == "__main__":
    unittest.main()
