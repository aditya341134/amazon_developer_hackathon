from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from app.settings import settings
from app.http.cors import configure_cors
from app.http.health import router as health_router
from app.auth.metadata import router as metadata_router
from app.auth.oauth_server import router as oauth_router

from app.db.connection import connect
from app.db.schema import init_schema
from app.db import repo

from app.domain.routines.models import DEFAULT_ROUTINES
from app.domain.simulator.scenarios import DEFAULT_SCENARIOS

from app.mcp_server import build_mcp_starlette_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("routine-doctor")

app = FastAPI(title="Routine Doctor (Alexa+ MCP + Simulator)")

# CORS
configure_cors(app, settings.frontend_origin)

# Health endpoints (both /health and /api/health)
app.include_router(health_router)
app.include_router(health_router, prefix="/api")

# Alexa+ Auth Discovery & OAuth endpoints
app.include_router(metadata_router)
app.include_router(oauth_router)

# DB connection
conn = connect(settings.db_path)


@app.on_event("startup")
def startup():
    init_schema(conn)

    if repo.table_empty(conn, "routines"):
        repo.seed_routines(conn, DEFAULT_ROUTINES)

    if repo.table_empty(conn, "scenarios"):
        repo.seed_scenarios(conn, DEFAULT_SCENARIOS)


@app.on_event("shutdown")
def shutdown():
    try:
        conn.close()
    except Exception:
        pass


# ---- Alexa+ MCP Auth Guard Middleware ----
# Invariant: Unauthenticated /mcp requests return 401 WITHOUT WWW-Authenticate header
@app.middleware("http")
async def mcp_auth_middleware(request: Request, call_next):
    if settings.auth_enabled and request.url.path.startswith("/mcp"):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            resp = Response(content="Unauthorized", status_code=401, media_type="text/plain")
            if "www-authenticate" in resp.headers:
                del resp.headers["www-authenticate"]
            return resp

    response = await call_next(request)
    return response


# ---- MCP mounted at /mcp ----
app.mount("/mcp", build_mcp_starlette_app(conn))


# ---- REST API for the React simulator ----

class RunRequest(BaseModel):
    routine_id: str
    scenario_id: str


class FixModeRequest(BaseModel):
    fix_mode: str = "both"


class ApplyFixRequest(BaseModel):
    fix_id: str


@app.get("/api/routines")
def api_list_routines():
    return {"routines": repo.list_routines(conn)}


@app.get("/api/scenarios")
def api_list_scenarios(routine_id: str):
    return {"routine_id": routine_id, "scenarios": repo.list_scenarios(conn, routine_id)}


@app.post("/api/runs")
def api_run(req: RunRequest):
    try:
        run = repo.create_run(conn, routine_id=req.routine_id, scenario_id=req.scenario_id)
        return run
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/runs/{run_id}/timeline")
def api_timeline(run_id: str):
    try:
        return {"run_id": run_id, "events": repo.get_timeline(conn, run_id)}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/runs/{run_id}/graph")
def api_graph(run_id: str):
    try:
        return repo.get_graph(conn, run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/runs/{run_id}/snapshots")
def api_snapshots(run_id: str):
    try:
        return {"run_id": run_id, "snapshots": repo.get_snapshots(conn, run_id)}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/runs/{run_id}/explain")
def api_explain(run_id: str):
    try:
        return repo.get_explain(conn, run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/runs/{run_id}/fixes/propose")
def api_propose_fixes(run_id: str, body: FixModeRequest):
    try:
        run = repo.get_run(conn, run_id)
        failure_type = run.get("primary_failure_type")
        if not failure_type:
            return {"run_id": run_id, "fixes": []}
        fixes = repo.list_or_create_fixes(conn, run_id, failure_type)
        return {"run_id": run_id, "fixes": fixes}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/runs/{run_id}/fixes/apply")
def api_apply_fix(run_id: str, body: ApplyFixRequest):
    try:
        return repo.apply_fix(conn, run_id, body.fix_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/runs/{run_id}/replay")
def api_replay(run_id: str):
    try:
        return repo.replay_run(conn, run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))