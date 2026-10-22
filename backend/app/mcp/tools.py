from __future__ import annotations

import json
from . import types
from mcp.server import ServerRequestContext

from app.db import repo


def _json_text(data) -> types.TextContent:
    return types.TextContent(type="text", text=json.dumps(data, indent=2))


def list_tools() -> types.ListToolsResult:
    tools = [
        types.Tool(
            name="list_routines",
            description="List available routines",
            input_schema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="list_scenarios",
            description="List scenarios for a routine",
            input_schema={
                "type": "object",
                "required": ["routine_id"],
                "properties": {"routine_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="run_scenario",
            description="Execute a routine+scenario run (creates a run_id)",
            input_schema={
                "type": "object",
                "required": ["routine_id", "scenario_id"],
                "properties": {
                    "routine_id": {"type": "string"},
                    "scenario_id": {"type": "string"},
                },
            },
        ),
        types.Tool(
            name="get_timeline",
            description="Fetch the timeline for a run_id",
            input_schema={
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="get_workflow_graph",
            description="Fetch the workflow graph for a run_id",
            input_schema={
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="explain_failure",
            description="Explain why a run failed (homeowner + developer view)",
            input_schema={
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="propose_fixes",
            description="Propose fixes for a failed run",
            input_schema={
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="apply_fix",
            description="Apply a fix patch to a run (updates applied_patches)",
            input_schema={
                "type": "object",
                "required": ["run_id", "fix_id"],
                "properties": {"run_id": {"type": "string"}, "fix_id": {"type": "string"}},
            },
        ),
        types.Tool(
            name="replay_run",
            description="Replay a run with applied patches (creates a new run)",
            input_schema={
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            },
        ),
    ]
    return types.ListToolsResult(tools=tools)


async def call_tool(conn, ctx: ServerRequestContext, params: types.CallToolRequestParams) -> types.CallToolResult:
    name = params.name
    args = params.arguments or {}

    try:
        if name == "list_routines":
            out = {"routines": repo.list_routines(conn)}
            return types.CallToolResult(content=[_json_text(out)])

        if name == "list_scenarios":
            routine_id = str(args["routine_id"])
            out = {"routine_id": routine_id, "scenarios": repo.list_scenarios(conn, routine_id)}
            return types.CallToolResult(content=[_json_text(out)])

        if name == "run_scenario":
            routine_id = str(args["routine_id"])
            scenario_id = str(args["scenario_id"])
            out = repo.create_run(conn, routine_id=routine_id, scenario_id=scenario_id)
            return types.CallToolResult(content=[_json_text(out)])

        if name == "get_timeline":
            run_id = str(args["run_id"])
            out = {"run_id": run_id, "events": repo.get_timeline(conn, run_id)}
            return types.CallToolResult(content=[_json_text(out)])

        if name == "get_workflow_graph":
            run_id = str(args["run_id"])
            out = repo.get_graph(conn, run_id)
            return types.CallToolResult(content=[_json_text(out)])

        if name == "explain_failure":
            run_id = str(args["run_id"])
            out = repo.get_explain(conn, run_id)
            return types.CallToolResult(content=[_json_text(out)])

        if name == "propose_fixes":
            run_id = str(args["run_id"])
            run = repo.get_run(conn, run_id)
            failure_type = run.get("primary_failure_type")
            if not failure_type:
                out = {"run_id": run_id, "fixes": []}
            else:
                fixes = repo.list_or_create_fixes(conn, run_id, failure_type)
                out = {"run_id": run_id, "fixes": fixes}
            return types.CallToolResult(content=[_json_text(out)])

        if name == "apply_fix":
            run_id = str(args["run_id"])
            fix_id = str(args["fix_id"])
            out = repo.apply_fix(conn, run_id, fix_id)
            return types.CallToolResult(content=[_json_text(out)])

        if name == "replay_run":
            run_id = str(args["run_id"])
            out = repo.replay_run(conn, run_id)
            return types.CallToolResult(content=[_json_text(out)])

        return types.CallToolResult(
            isError=True,
            content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
        )

    except Exception as e:
        return types.CallToolResult(
            isError=True,
            content=[types.TextContent(type="text", text=f"Tool error: {type(e).__name__}: {e}")],
        )