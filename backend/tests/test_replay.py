import unittest
from app.db.connection import connect
from app.db.schema import init_schema
from app.db import repo
from app.domain.routines.models import DEFAULT_ROUTINES
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS


class TestReplay(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        init_schema(self.conn)
        repo.seed_routines(self.conn, DEFAULT_ROUTINES)
        repo.seed_scenarios(self.conn, DEFAULT_SCENARIOS)

    def tearDown(self):
        self.conn.close()

    def test_end_to_end_replay_flow(self):
        # 1. Create run for F1
        run = repo.create_run(self.conn, routine_id="r1", scenario_id="s1_f1_unreachable")
        run_id = run["run_id"]
        self.assertEqual(run["status"], "FAIL")
        self.assertEqual(run["primary_failure_type"], "F1_UNREACHABLE")

        # 2. Check snapshots were stored
        snaps = repo.get_snapshots(self.conn, run_id)
        self.assertTrue(len(snaps) > 0)

        # 3. Propose fixes
        fixes = repo.list_or_create_fixes(self.conn, run_id, run["primary_failure_type"])
        self.assertEqual(len(fixes), 2)
        routine_fix = next(f for f in fixes if f["mode"] == "routine")

        # 4. Apply fix
        applied = repo.apply_fix(self.conn, run_id, routine_fix["fix_id"])
        self.assertTrue(applied["applied"])

        # 5. Replay run
        replay_res = repo.replay_run(self.conn, run_id)
        self.assertEqual(replay_res["original_run_id"], run_id)
        self.assertNotEqual(replay_res["replay_run_id"], run_id)
        self.assertEqual(replay_res["status"], "PASS")
        self.assertTrue(replay_res["diff_summary"]["fixed"])
        self.assertEqual(replay_res["diff_summary"]["failure_before"], "F1_UNREACHABLE")
        self.assertIsNone(replay_res["diff_summary"]["failure_after"])


if __name__ == "__main__":
    unittest.main()
