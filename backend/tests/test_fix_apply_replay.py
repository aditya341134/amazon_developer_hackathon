import unittest
from app.domain.routines.models import ROUTINE_R1, ROUTINE_R2
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.routines.engine import execute_run


class TestFixApplyReplay(unittest.TestCase):
    def test_f1_fix_replays_to_pass(self):
        s1 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s1_f1_unreachable")
        # Pre-fix: fails
        res_fail = execute_run(ROUTINE_R1, s1)
        self.assertEqual(res_fail["status"], "FAIL")

        # Post-fix with ROUTINE_ADD_RETRY: passes
        patch = [{"type": "ROUTINE_ADD_RETRY", "retries": 2}]
        res_pass = execute_run(ROUTINE_R1, s1, patches=patch)
        self.assertEqual(res_pass["status"], "PASS")
        self.assertIsNone(res_pass["primary_failure_type"])

    def test_f2_fix_replays_to_pass(self):
        s3 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s3_f2_stale_state")
        res_fail = execute_run(ROUTINE_R2, s3)
        self.assertEqual(res_fail["status"], "FAIL")

        patch = [{"type": "ROUTINE_REFRESH_STATE", "device_id": "lock_1"}]
        res_pass = execute_run(ROUTINE_R2, s3, patches=patch)
        self.assertEqual(res_pass["status"], "PASS")

    def test_f3_fix_replays_to_pass(self):
        s2 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s2_f3_cap_mismatch")
        res_fail = execute_run(ROUTINE_R1, s2)
        self.assertEqual(res_fail["status"], "FAIL")

        # Graceful degradation fix
        patch = [{"type": "ROUTINE_DEGRADE_BRIGHTNESS"}]
        res_pass = execute_run(ROUTINE_R1, s2, patches=patch)
        self.assertEqual(res_pass["status"], "PASS")
        self.assertEqual(res_pass["graph"]["execution"]["node_status"]["n_action_dim"]["status"], "SKIPPED")


if __name__ == "__main__":
    unittest.main()
