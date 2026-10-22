import unittest
from app.domain.fixes.proposer import propose_fixes
from app.domain.fixes.applier import apply_patch
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


class TestFixes(unittest.TestCase):
    def test_propose_f1_fixes(self):
        fixes = propose_fixes(F1_UNREACHABLE)
        self.assertEqual(len(fixes), 2)
        modes = [f["mode"] for f in fixes]
        self.assertIn("routine", modes)
        self.assertIn("integration", modes)
        routine_fix = next(f for f in fixes if f["mode"] == "routine")
        self.assertEqual(routine_fix["patch"]["type"], "ROUTINE_ADD_RETRY")
        self.assertTrue(routine_fix["auto_apply_ok"])

    def test_propose_f2_fixes(self):
        fixes = propose_fixes(F2_STALE_STATE)
        self.assertEqual(len(fixes), 2)
        routine_fix = next(f for f in fixes if f["mode"] == "routine")
        self.assertEqual(routine_fix["patch"]["type"], "ROUTINE_REFRESH_STATE")

    def test_propose_f3_fixes(self):
        fixes = propose_fixes(F3_CAPABILITY_MISMATCH)
        self.assertEqual(len(fixes), 2)
        routine_fix = next(f for f in fixes if f["mode"] == "routine")
        self.assertEqual(routine_fix["patch"]["type"], "ROUTINE_DEGRADE_BRIGHTNESS")

    def test_apply_patch(self):
        existing = [{"type": "FOO"}]
        new_patch = {"type": "ROUTINE_ADD_RETRY"}
        updated = apply_patch(existing, new_patch)
        self.assertEqual(len(updated), 2)
        self.assertEqual(updated[1]["type"], "ROUTINE_ADD_RETRY")


if __name__ == "__main__":
    unittest.main()
