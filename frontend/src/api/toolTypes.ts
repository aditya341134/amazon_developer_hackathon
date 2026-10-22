export type RoutineSummary = {
  routine_id: string;
  name: string;
  description?: string;
};

export type ScenarioSummary = {
  scenario_id: string;
  name: string;
  description?: string;
};

export type RunSummary = {
  run_id: string;
  routine_id: string;
  scenario_id: string;
  started_at: string;
  status: "PASS" | "FAIL";
  primary_failure_type: string | null;
};

export type TimelineEvent = {
  event_id: string;
  ts: string;
  kind:
    | "SENSOR_EVENT"
    | "DECISION"
    | "DIRECTIVE"
    | "RESPONSE"
    | "ASSERT"
    | "INFO";
  summary: string;
  payload: Record<string, unknown>;
};

export type TimelineResponse = {
  run_id: string;
  events: TimelineEvent[];
};

export type DeviceSnapshot = {
  snapshot_id: string;
  ts: string;
  device_id: string;
  endpoint_health: "OK" | "UNREACHABLE";
  actual_state: Record<string, unknown>;
  reported_state: Record<string, unknown>;
  time_of_sample: string | null;
  declared_capabilities: string[];
  actual_capabilities: string[];
};

export type SnapshotsResponse = {
  run_id: string;
  snapshots: DeviceSnapshot[];
};

export type GraphNode = {
  id: string;
  kind: "TRIGGER" | "CONDITION" | "ACTION" | "ASSERT" | "START" | "END";
  label: string;
  ref?: string;
};

export type GraphEdge = {
  from: string;
  to: string;
  when?: "true" | "false";
};

export type GraphExecution = {
  node_status: Record<
    string,
    { status: "SUCCESS" | "FAILED" | "SKIPPED"; at: string; event_id: string }
  >;
  failed_node_id: string | null;
};

export type WorkflowGraph = {
  run_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  execution: GraphExecution;
};

export type ExplainResponse = {
  run_id: string;
  classification: string | null;
  homeowner: {
    what: string;
    when: string;
    why: string;
    next_steps: string[];
  };
  developer: {
    failed_node_id: string | null;
    evidence: Array<Record<string, unknown>>;
    recommended_fix_modes: string[];
  };
};

export type Fix = {
  fix_id: string;
  mode: "routine" | "integration";
  title: string;
  why_it_works: string;
  patch: Record<string, unknown>;
  safety: { auto_apply_ok: boolean; notes: string };
  applied?: boolean;
};

export type ProposeFixesResponse = {
  run_id: string;
  fixes: Fix[];
};

export type ApplyFixResponse = {
  run_id: string;
  fix_id: string;
  applied: boolean;
  changes: {
    routine_changed: boolean;
    integration_config_changed: boolean;
  };
};

export type ReplayResponse = {
  original_run_id: string;
  replay_run_id: string;
  status: "PASS" | "FAIL";
  primary_failure_type: string | null;
  diff_summary: {
    fixed: boolean;
    failure_before: string | null;
    failure_after: string | null;
    nodes_changed: Array<{ node_id: string; from: string; to: string }>;
  };
};