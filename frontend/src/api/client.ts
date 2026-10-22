import {
  ApplyFixResponse,
  ExplainResponse,
  ProposeFixesResponse,
  ReplayResponse,
  RoutineSummary,
  RunSummary,
  ScenarioSummary,
  SnapshotsResponse,
  TimelineResponse,
  WorkflowGraph
} from "./toolTypes";

const BASE =
  import.meta.env.VITE_BACKEND_BASE_URL?.toString() ?? "http://localhost:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
  }
  return (await res.json()) as T;
}

export async function listRoutines(): Promise<{ routines: RoutineSummary[] }> {
  return http(`/api/routines`);
}

export async function listScenarios(
  routine_id: string
): Promise<{ routine_id: string; scenarios: ScenarioSummary[] }> {
  const qs = new URLSearchParams({ routine_id }).toString();
  return http(`/api/scenarios?${qs}`);
}

export async function runScenario(body: {
  routine_id: string;
  scenario_id: string;
}): Promise<RunSummary> {
  return http(`/api/runs`, { method: "POST", body: JSON.stringify(body) });
}

export async function getTimeline(run_id: string): Promise<TimelineResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/timeline`);
}

export async function getGraph(run_id: string): Promise<WorkflowGraph> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/graph`);
}

export async function getSnapshots(run_id: string): Promise<SnapshotsResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/snapshots`);
}

export async function explain(run_id: string): Promise<ExplainResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/explain`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export async function proposeFixes(
  run_id: string
): Promise<ProposeFixesResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/fixes/propose`, {
    method: "POST",
    body: JSON.stringify({ fix_mode: "both" })
  });
}

export async function applyFix(
  run_id: string,
  fix_id: string
): Promise<ApplyFixResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/fixes/apply`, {
    method: "POST",
    body: JSON.stringify({ fix_id })
  });
}

export async function replay(run_id: string): Promise<ReplayResponse> {
  return http(`/api/runs/${encodeURIComponent(run_id)}/replay`, {
    method: "POST",
    body: JSON.stringify({})
  });
}