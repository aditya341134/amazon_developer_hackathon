from __future__ import annotations

import json
from typing import Any

from app.util.ids import new_id
from app.domain.routines.engine import execute_run
from app.domain.fixes.applier import apply_patch


def table_empty(conn, table: str) -> bool:
    row = conn.execute(f"SELECT COUNT(1) AS c FROM {table}").fetchone()
    return row["c"] == 0


def seed_routines(conn, routines: list[dict[str, Any]]) -> None:
    for r in routines:
        conn.execute(
            "INSERT OR REPLACE INTO routines(routine_id,name,description,spec_json) VALUES (?,?,?,?)",
            (r["routine_id"], r["name"], r.get("description", ""), json.dumps(r)),
        )
    conn.commit()


def seed_scenarios(conn, scenarios: list[dict[str, Any]]) -> None:
    for s in scenarios:
        conn.execute(
            "INSERT OR REPLACE INTO scenarios(scenario_id,routine_id,name,description,seed,definition_json) VALUES (?,?,?,?,?,?)",
            (
                s["scenario_id"],
                s["routine_id"],
                s["name"],
                s.get("description", ""),
                int(s.get("seed", 0)),
                json.dumps(s),
            ),
        )
    conn.commit()


def list_routines(conn) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT routine_id,name,description FROM routines ORDER BY routine_id").fetchall()
    return [dict(r) for r in rows]


def list_scenarios(conn, routine_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT scenario_id,name,description FROM scenarios WHERE routine_id=? ORDER BY scenario_id",
        (routine_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_routine_spec(conn, routine_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT spec_json FROM routines WHERE routine_id=?", (routine_id,)).fetchone()
    if not row:
        raise KeyError(f"Routine not found: {routine_id}")
    return json.loads(row["spec_json"])


def get_scenario_def(conn, scenario_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT definition_json FROM scenarios WHERE scenario_id=?", (scenario_id,)).fetchone()
    if not row:
        raise KeyError(f"Scenario not found: {scenario_id}")
    return json.loads(row["definition_json"])


def get_run(conn, run_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if not row:
        raise KeyError(f"Run not found: {run_id}")
    return dict(row)


def insert_events(conn, run_id: str, events: list[dict[str, Any]]) -> None:
    conn.executemany(
        "INSERT INTO events(event_id,run_id,ts,kind,summary,payload_json) VALUES (?,?,?,?,?,?)",
        [(e["event_id"], run_id, e["ts"], e["kind"], e["summary"], json.dumps(e["payload"])) for e in events],
    )
    conn.commit()


def get_timeline(conn, run_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT event_id,ts,kind,summary,payload_json FROM events WHERE run_id=? ORDER BY ts",
        (run_id,),
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "event_id": r["event_id"],
            "ts": r["ts"],
            "kind": r["kind"],
            "summary": r["summary"],
            "payload": json.loads(r["payload_json"]),
        })
    return out


def insert_snapshots(conn, run_id: str, snapshots: list[dict[str, Any]]) -> None:
    conn.executemany(
        """INSERT INTO device_snapshots(
            snapshot_id, run_id, ts, device_id, endpoint_health,
            actual_state_json, reported_state_json, time_of_sample,
            declared_caps_json, actual_caps_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [
            (
                s.get("snapshot_id", new_id("snap")),
                run_id,
                s["ts"],
                s["device_id"],
                s["endpoint_health"],
                json.dumps(s.get("actual_state", {})),
                json.dumps(s.get("reported_state", {})),
                s.get("time_of_sample"),
                json.dumps(s.get("declared_capabilities", [])),
                json.dumps(s.get("actual_capabilities", [])),
            )
            for s in snapshots
        ],
    )
    conn.commit()


def get_snapshots(conn, run_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """SELECT snapshot_id, ts, device_id, endpoint_health,
                  actual_state_json, reported_state_json, time_of_sample,
                  declared_caps_json, actual_caps_json
           FROM device_snapshots WHERE run_id=? ORDER BY ts""",
        (run_id,),
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "snapshot_id": r["snapshot_id"],
            "ts": r["ts"],
            "device_id": r["device_id"],
            "endpoint_health": r["endpoint_health"],
            "actual_state": json.loads(r["actual_state_json"]),
            "reported_state": json.loads(r["reported_state_json"]),
            "time_of_sample": r["time_of_sample"],
            "declared_capabilities": json.loads(r["declared_caps_json"]),
            "actual_capabilities": json.loads(r["actual_caps_json"]),
        })
    return out


def create_run(conn, routine_id: str, scenario_id: str, patches: list[dict[str, Any]] | None = None, created_from_run_id: str | None = None) -> dict[str, Any]:
    patches = patches or []

    routine_spec = get_routine_spec(conn, routine_id)
    scenario_def = get_scenario_def(conn, scenario_id)

    exec_result = execute_run(routine_spec, scenario_def, patches=patches)

    run_id = new_id("run")

    graph = exec_result["graph"]
    graph["run_id"] = run_id

    explain = exec_result["explain"]
    explain["run_id"] = run_id

    started_at = scenario_def["base_time"]

    conn.execute("""
      INSERT INTO runs(
        run_id, routine_id, scenario_id, started_at, status, primary_failure_type,
        graph_json, explain_json, applied_patches_json, created_from_run_id
      )
      VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        run_id,
        routine_id,
        scenario_id,
        started_at,
        exec_result["status"],
        exec_result["primary_failure_type"],
        json.dumps(graph),
        json.dumps(explain),
        json.dumps(patches),
        created_from_run_id,
    ))
    conn.commit()

    insert_events(conn, run_id, exec_result["events"])

    if exec_result.get("snapshots"):
        insert_snapshots(conn, run_id, exec_result["snapshots"])

    return {
        "run_id": run_id,
        "routine_id": routine_id,
        "scenario_id": scenario_id,
        "started_at": started_at,
        "status": exec_result["status"],
        "primary_failure_type": exec_result["primary_failure_type"],
    }


def get_graph(conn, run_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT graph_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if not row:
        raise KeyError(f"Run not found: {run_id}")
    return json.loads(row["graph_json"]) if row["graph_json"] else {}


def get_explain(conn, run_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT explain_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if not row:
        raise KeyError(f"Run not found: {run_id}")
    return json.loads(row["explain_json"]) if row["explain_json"] else {}


def list_or_create_fixes(conn, run_id: str, failure_type: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT fix_id, mode, title, why_it_works, patch_json, auto_apply_ok, applied FROM fixes WHERE run_id=?",
        (run_id,),
    ).fetchall()
    if rows:
        return [
            {
                "fix_id": r["fix_id"],
                "mode": r["mode"],
                "title": r["title"],
                "why_it_works": r["why_it_works"],
                "patch": json.loads(r["patch_json"]),
                "safety": {"auto_apply_ok": bool(r["auto_apply_ok"]), "notes": ""},
                "applied": bool(r["applied"]),
            }
            for r in rows
        ]

    from app.domain.fixes.proposer import propose_fixes
    proposals = propose_fixes(failure_type)

    fixes_out = []
    for p in proposals:
        fix_id = new_id("fix")
        conn.execute(
            "INSERT INTO fixes(fix_id,run_id,mode,title,why_it_works,patch_json,auto_apply_ok,applied) VALUES (?,?,?,?,?,?,?,0)",
            (fix_id, run_id, p["mode"], p["title"], p["why_it_works"], json.dumps(p["patch"]), 1 if p["auto_apply_ok"] else 0),
        )
        fixes_out.append({
            "fix_id": fix_id,
            "mode": p["mode"],
            "title": p["title"],
            "why_it_works": p["why_it_works"],
            "patch": p["patch"],
            "safety": {"auto_apply_ok": bool(p["auto_apply_ok"]), "notes": ""},
            "applied": False,
        })
    conn.commit()
    return fixes_out


def apply_fix(conn, run_id: str, fix_id: str) -> dict[str, Any]:
    run = get_run(conn, run_id)

    fix_row = conn.execute("SELECT patch_json, applied FROM fixes WHERE fix_id=? AND run_id=?", (fix_id, run_id)).fetchone()
    if not fix_row:
        raise KeyError(f"Fix not found: {fix_id}")

    patch = json.loads(fix_row["patch_json"])
    existing_patches = json.loads(run["applied_patches_json"])
    new_patches = apply_patch(existing_patches, patch)

    conn.execute("UPDATE runs SET applied_patches_json=? WHERE run_id=?", (json.dumps(new_patches), run_id))
    conn.execute("UPDATE fixes SET applied=1 WHERE fix_id=?", (fix_id,))
    conn.commit()

    return {
        "run_id": run_id,
        "fix_id": fix_id,
        "applied": True,
        "changes": {
            "routine_changed": patch.get("type", "").startswith("ROUTINE_"),
            "integration_config_changed": patch.get("type", "").startswith("INTEGRATION_"),
        },
    }


def replay_run(conn, run_id: str) -> dict[str, Any]:
    run = get_run(conn, run_id)
    patches = json.loads(run["applied_patches_json"])

    new_run = create_run(
        conn,
        routine_id=run["routine_id"],
        scenario_id=run["scenario_id"],
        patches=patches,
        created_from_run_id=run_id,
    )

    old_graph = get_graph(conn, run_id)
    new_graph = get_graph(conn, new_run["run_id"])
    nodes_changed = []
    old_status = old_graph.get("execution", {}).get("node_status", {})
    new_status = new_graph.get("execution", {}).get("node_status", {})
    for node_id, n_data in new_status.items():
        prev_st = old_status.get(node_id, {}).get("status")
        curr_st = n_data.get("status")
        if prev_st and prev_st != curr_st:
            nodes_changed.append({
                "node_id": node_id,
                "from": prev_st,
                "to": curr_st,
            })

    diff = {
        "fixed": (run["status"] == "FAIL" and new_run["status"] == "PASS"),
        "failure_before": run.get("primary_failure_type"),
        "failure_after": new_run.get("primary_failure_type"),
        "nodes_changed": nodes_changed,
    }

    return {
        "original_run_id": run_id,
        "replay_run_id": new_run["run_id"],
        "status": new_run["status"],
        "primary_failure_type": new_run["primary_failure_type"],
        "diff_summary": diff,
    }