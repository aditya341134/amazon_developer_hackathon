import unittest
from app.domain.routines.models import ROUTINE_R1, ROUTINE_R2
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.domain.routines.engine import execute_run


class TestReplayDeterminism(unittest.TestCase):
    def test_r1_determinism(self):
        s1 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s1_f1_unreachable")
        run1 = execute_run(ROUTINE_R1, s1)
        run2 = execute_run(ROUTINE_R1, s1)

        self.assertEqual(run1["status"], run2["status"])
        self.assertEqual(run1["primary_failure_type"], run2["primary_failure_type"])
        self.assertEqual(len(run1["events"]), len(run2["events"]))

        for e1, e2 in zip(run1["events"], run2["events"]):
            self.assertEqual(e1["ts"], e2["ts"])
            self.assertEqual(e1["kind"], e2["kind"])
            self.assertEqual(e1["summary"], e2["summary"])
            self.assertEqual(e1["payload"], e2["payload"])

    def test_r2_determinism(self):
        s3 = next(s for s in DEFAULT_SCENARIOS if s["scenario_id"] == "s3_f2_stale_state")
        run1 = execute_run(ROUTINE_R2, s3)
        run2 = execute_run(ROUTINE_R2, s3)

        self.assertEqual(run1["status"], run2["status"])
        self.assertEqual(run1["primary_failure_type"], run2["primary_failure_type"])
        self.assertEqual(len(run1["events"]), len(run2["events"]))


if __name__ == "__main__":
    unittest.main()
