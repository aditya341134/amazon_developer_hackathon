import unittest
from app.domain.diagnostics.explainer import explain_failure
from app.domain.simulator.faults import F1_UNREACHABLE, F2_STALE_STATE, F3_CAPABILITY_MISMATCH


class TestDiagnostics(unittest.TestCase):
    def test_explain_f1_unreachable(self):
        res = explain_failure(
            failure_type=F1_UNREACHABLE,
            when_ts="2026-10-19T19:30:01Z",
            failed_node_id="n_action_on",
            evidence_event_ids=["evt_1", "evt_2"],
            snapshot_facts=[{"device_id": "light_1", "endpoint_health": "UNREACHABLE"}],
        )
        self.assertEqual(res["classification"], F1_UNREACHABLE)
        self.assertIn("homeowner", res)
        self.assertIn("developer", res)
        self.assertIn("couldn't reach", res["homeowner"]["why"])
        self.assertEqual(res["developer"]["failed_node_id"], "n_action_on")
        self.assertEqual(res["developer"]["evidence"][0]["property"], "endpoint_health")

    def test_explain_f2_stale_state(self):
        res = explain_failure(
            failure_type=F2_STALE_STATE,
            when_ts="2026-10-19T22:00:01Z",
            failed_node_id="n_cond_lock",
            evidence_event_ids=["evt_10"],
        )
        self.assertEqual(res["classification"], F2_STALE_STATE)
        self.assertIn("out-of-date lock status", res["homeowner"]["why"])
        self.assertEqual(res["developer"]["failed_node_id"], "n_cond_lock")

    def test_explain_f3_cap_mismatch(self):
        res = explain_failure(
            failure_type=F3_CAPABILITY_MISMATCH,
            when_ts="2026-10-19T22:15:02Z",
            failed_node_id="n_action_dim",
            evidence_event_ids=["evt_20"],
        )
        self.assertEqual(res["classification"], F3_CAPABILITY_MISMATCH)
        self.assertIn("doesn't support brightness", res["homeowner"]["why"])
        self.assertEqual(res["developer"]["failed_node_id"], "n_action_dim")


if __name__ == "__main__":
    unittest.main()
