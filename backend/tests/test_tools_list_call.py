import unittest
import asyncio
import json
from dataclasses import dataclass
from typing import Any

from app.db.connection import connect
from app.db.schema import init_schema
from app.db import repo
from app.domain.routines.models import DEFAULT_ROUTINES
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS
from app.mcp.tools import list_tools, call_tool


@dataclass
class DummyCallParams:
    name: str
    arguments: dict[str, Any]


class TestToolsListCall(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        init_schema(self.conn)
        repo.seed_routines(self.conn, DEFAULT_ROUTINES)
        repo.seed_scenarios(self.conn, DEFAULT_SCENARIOS)

    def tearDown(self):
        self.conn.close()

    def test_list_tools(self):
        result = list_tools()
        tool_names = [t.name for t in result.tools]
        expected_tools = [
            "list_routines",
            "list_scenarios",
            "run_scenario",
            "get_timeline",
            "get_workflow_graph",
            "explain_failure",
            "propose_fixes",
            "apply_fix",
            "replay_run",
        ]
        for et in expected_tools:
            self.assertIn(et, tool_names)

    def test_call_all_tools_end_to_end(self):
        async def run_calls():
            # 1. list_routines
            res = await call_tool(self.conn, None, DummyCallParams("list_routines", {}))
            self.assertFalse(res.isError)
            data = json.loads(res.content[0].text)
            self.assertEqual(len(data["routines"]), 2)

            # 2. list_scenarios
            res = await call_tool(self.conn, None, DummyCallParams("list_scenarios", {"routine_id": "r1"}))
            self.assertFalse(res.isError)
            data = json.loads(res.content[0].text)
            self.assertTrue(len(data["scenarios"]) >= 2)

            # 3. run_scenario
            res = await call_tool(
                self.conn, None, DummyCallParams("run_scenario", {"routine_id": "r1", "scenario_id": "s1_f1_unreachable"})
            )
            self.assertFalse(res.isError)
            run_data = json.loads(res.content[0].text)
            run_id = run_data["run_id"]
            self.assertEqual(run_data["status"], "FAIL")

            # 4. get_timeline
            res = await call_tool(self.conn, None, DummyCallParams("get_timeline", {"run_id": run_id}))
            self.assertFalse(res.isError)
            tl_data = json.loads(res.content[0].text)
            self.assertTrue(len(tl_data["events"]) > 0)

            # 5. get_workflow_graph
            res = await call_tool(self.conn, None, DummyCallParams("get_workflow_graph", {"run_id": run_id}))
            self.assertFalse(res.isError)
            graph_data = json.loads(res.content[0].text)
            self.assertIn("nodes", graph_data)

            # 6. explain_failure
            res = await call_tool(self.conn, None, DummyCallParams("explain_failure", {"run_id": run_id}))
            self.assertFalse(res.isError)
            explain_data = json.loads(res.content[0].text)
            self.assertEqual(explain_data["classification"], "F1_UNREACHABLE")

            # 7. propose_fixes
            res = await call_tool(self.conn, None, DummyCallParams("propose_fixes", {"run_id": run_id}))
            self.assertFalse(res.isError)
            fixes_data = json.loads(res.content[0].text)
            self.assertEqual(len(fixes_data["fixes"]), 2)
            fix_id = fixes_data["fixes"][0]["fix_id"]

            # 8. apply_fix
            res = await call_tool(self.conn, None, DummyCallParams("apply_fix", {"run_id": run_id, "fix_id": fix_id}))
            self.assertFalse(res.isError)
            apply_data = json.loads(res.content[0].text)
            self.assertTrue(apply_data["applied"])

            # 9. replay_run
            res = await call_tool(self.conn, None, DummyCallParams("replay_run", {"run_id": run_id}))
            self.assertFalse(res.isError)
            replay_data = json.loads(res.content[0].text)
            self.assertEqual(replay_data["status"], "PASS")

        asyncio.run(run_calls())


if __name__ == "__main__":
    unittest.main()
